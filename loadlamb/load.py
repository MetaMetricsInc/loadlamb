import asyncio
import concurrent.futures
import datetime
import time

import aiohttp
from docb.exceptions import QueryError
from slugify import slugify

from loadlamb.contrib.db.models import LoadTestResponse, Run, Project
from loadlamb.request import User


class LoadLamb(object):

    def __init__(self, config):
        self.config = config
        self.results = None

    def filter_status_code(self, starts_with):
        return len(list(filter(lambda x: str(x.status_code).startswith(starts_with), self.results)))

    def get_or_create_project(self, project_slug):
        try:
            Project.objects().get({'project_slug': project_slug})
        except QueryError:
            pj = Project(project_slug=project_slug, name=self.config['name'], repo_url=self.config['repo_url'],
                         url=self.config['url'])
            pj.save()

    async def run(self):

        project_slug = slugify(self.config['name'])
        self.get_or_create_project(project_slug)

        run_slug = slugify('{}-{}'.format(self.config['name'], datetime.datetime.now()))
        run = Run(project_slug=project_slug, run_slug=run_slug)
        run.save()
        self.config['project_slug'] = project_slug
        self.config['run_slug'] = run_slug
        no_requests = self.config['user_num'] * len(self.config['tasks'])
        start_time = time.perf_counter()
        timeout = aiohttp.ClientTimeout(total=self.config.get('timeout', 60))
        conn = aiohttp.TCPConnector()


        async with aiohttp.ClientSession(timeout=timeout, connector=conn) as session:
            try:
                results = await asyncio.gather(*[User(self.config, session).run() for e in range(
                    self.config['user_num'])])
            except concurrent.futures._base.TimeoutError:
                return {
                    'failure': 'Timeout'
                }
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        req_per_sec = no_requests / elapsed_time
        results_list = list()
        try:

            for i in results:

                results_list.extend(i)

            self.results = results_list
            run.requests = no_requests
            run.requests_per_second = req_per_sec
            run.status_200 = self.filter_status_code('2')
            run.status_400 = self.filter_status_code('4')
            run.status_500 = self.filter_status_code('5')
            run.completed = "False"
            run.elapsed_time = elapsed_time
            run.error_msg = ''
            run.save()
            LoadTestResponse().bulk_save(self.results)

            return {
                'project_slug': project_slug,
                'run_slug': run_slug,
                'status_200': run.status_200,
                'status_400': run.status_400,
                'status_500': run.status_500,
                'requests': no_requests,
                'request_per_second': req_per_sec,
                'time_taken': elapsed_time,
            }

        except Exception as e:
            run.error_msg = str(e)
            run.completed = True
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