import asyncio
import concurrent.futures
import datetime
import time

import aiohttp
from slugify import slugify

from loadlamb.contrib.db.models import LoadTestResponse, Run
from loadlamb.request import User


class LoadLamb(object):

    def __init__(self, config):
        self.config = config
        self.results = None

    async def run(self):
        project_slug = slugify(self.config['name'])
        run_slug = slugify('{}-{}'.format(self.config['name'], datetime.datetime.now()))
        run = Run(project_slug=project_slug, run_slug=run_slug)
        run.save()
        self.config['project_slug'] = project_slug
        self.config['run_slug'] = run_slug

        start_time = time.perf_counter()
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                results = await asyncio.gather(*[User(self.config, session).run() for e in range(
                    self.config['user_num'])])
            except concurrent.futures._base.TimeoutError:
                return {
                    'failure': 'Timeout'
                }
        end_time = time.perf_counter()
        no_requests = self.config['user_num'] * len(self.config['tasks'])

        elapsed_time = end_time - start_time
        req_per_sec = no_requests / elapsed_time
        results_list = list()
        for i in results:
            results_list.extend(i)
        self.results = results_list
        run.requests = no_requests
        run.requests_per_second = req_per_sec
        run.elapsed_time = elapsed_time
        run.save()
        LoadTestResponse().bulk_save(self.results)

        return {
            'requests': no_requests,
            'request_per_second': req_per_sec,
            'time_taken': elapsed_time,
        }
