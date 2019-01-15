import asyncio
import concurrent.futures
import time

import aiohttp

from loadlamb.request import User


class LoadLamb(object):

    def __init__(self, config):
        self.config = config

    async def run(self):
        start_time = time.perf_counter()
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            try:
                result = await asyncio.gather(*[User(self.config, session).run() for e in range(
                    self.config['user_num'])])
            except concurrent.futures._base.TimeoutError:
                return {
                    'failure': 'Timeout'
                }

        no_requests = self.config['user_num'] * len(self.config['tasks'])
        end_time = time.perf_counter()
        time_taken = end_time - start_time
        req_per_sec = no_requests / time_taken
        return {
            'requests': no_requests,
            'request_per_second': req_per_sec,
            'time_taken': time_taken,
        }
