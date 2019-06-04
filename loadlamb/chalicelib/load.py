import asyncio
import concurrent.futures
import datetime
import itertools
import time

import aiohttp
from docb.exceptions import QueryError
from slugify import slugify

from loadlamb.chalicelib.contrib.db.models import LoadTestResponse, Run, Project, Group as GroupModel, Stage
from loadlamb.chalicelib.request import Group
from loadlamb.chalicelib.utils import grouper


class LoadLamb(object):

    def __init__(self, config, commit=None):
        self.config = config
        self.commit = commit
        self.responses = None
        self.groups = None

    def get_or_create_project(self, project_slug):
        try:
            Project.objects().get({'project_slug': project_slug})
        except QueryError:
            pj = Project(project_slug=project_slug, name=self.config['name'], repo=self.config['repo'])
            pj.save()

        for stage in self.config.get('stages', []):
            try:
                Stage.objects().get({'project_slug': project_slug, 'name': stage.get('name')})
            except QueryError:
                stg = Stage(name=stage.get('name'), url=stage.get('url'), project_slug=project_slug,
                            branch=stage.get('branch'))
                stg.save()

    async def run(self):

        project_slug = slugify(self.config['name'])
        self.get_or_create_project(project_slug)

        run_slug = slugify('{}-{}'.format(self.config['name'], datetime.datetime.now()))
        run = Run(project_slug=project_slug, run_slug=run_slug, stage=self.config.get('active_stage'),
                  user_batch_size=self.config['user_batch_size'],
                  user_batch_sleep=self.config['user_batch_sleep'], commit=self.commit)
        run.save()
        self.config['project_slug'] = project_slug
        self.config['run_slug'] = run_slug
        no_requests = self.config['user_num'] * len(self.config['tasks'])
        start_time = time.perf_counter()
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 60))
        conn = aiohttp.TCPConnector()

        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            try:
                results = await asyncio.gather(
                    *[Group(no_users, session, self.config, group_no).run() for group_no, no_users in list(
                        enumerate(grouper(self.config.get('user_batch_size'), self.config.get('user_num')), 1))])
            except concurrent.futures._base.TimeoutError:
                return {
                    'failure': 'Timeout'
                }
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time

        try:
            self.groups = results
            self.responses = list(itertools.chain.from_iterable([g.responses for g in results]))
            GroupModel().bulk_save(self.groups)
            LoadTestResponse().bulk_save(self.responses)
            run.requests = no_requests
            run.requests_per_second = GroupModel.objects().filter({'project_slug': project_slug,
                                                                   'run_slug': run_slug}).mean('requests_per_second')

            try:
                run.status_200 = GroupModel.objects().filter({'project_slug': project_slug,
                                                              'run_slug': run_slug}).sum('status_200')
            except TypeError:
                run.status_200 = 0
            try:
                run.status_400 = GroupModel.objects().filter({'project_slug': project_slug,
                                                              'run_slug': run_slug}).sum('status_400')
            except TypeError:
                run.status_400 = 0

            try:
                run.status_500 = GroupModel.objects().filter({'project_slug': project_slug,
                                                              'run_slug': run_slug}).sum('status_500')
            except TypeError:
                run.status_500 = 0

            run.completed = True
            run.elapsed_time = elapsed_time
            run.commit = self.commit
            run.save()

            return {
                'project_slug': project_slug,
                'run_slug': run_slug,
                'status_200': run.status_200,
                'status_400': run.status_400,
                'status_500': run.status_500,
                'requests': no_requests,
                'request_per_second': run.requests_per_second,
                'time_taken': elapsed_time,
            }

        except Exception as e:
            run.error_msg = str(e)
            run.requests_per_second = 0
            run.completed = False
            run.requests = no_requests
            run.save()
            return {
                'project_slug': project_slug,
                'run_slug': run_slug,
                'status_200': 0,
                'status_400': 0,
                'status_500': 0,
                'requests': no_requests,
                'request_per_second': 0,
                'time_taken': 0,
            }
