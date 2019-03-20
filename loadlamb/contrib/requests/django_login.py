import asyncio
import random
import time

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_csrf_token


class DjangoLogin(Request):

    async def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'), self.req_config.get('path'))
        try:
            a = await self.session.request('get', url)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)
        data = random.choice(self.req_config.get('data', {}))
        try:
            data['csrfmiddlewaretoken'] = get_csrf_token(a)
        except AttributeError:
            return await self.get_null_response(self.timeout)
        start_time = time.perf_counter()
        try:
            b = await self.session.request('post', a.url, data=data, headers={'referer': url})
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)

        end_time = time.perf_counter()
        time_taken = end_time - start_time
        resp = Response(b, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), time_taken)
        await resp.assert_contains()
        return await resp.get_ltr()
