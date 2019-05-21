import asyncio
import random
import time

from loadlamb.chalicelib.request import Request
from loadlamb.chalicelib.response import Response
from loadlamb.chalicelib.utils import get_csrf_token


class DjangoPost(Request):

    async def run(self):
        url = '{}{}'.format(self.get_url(), self.req_config.get('path'))
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
            b = await self.session.request('post', url, data=data, headers={'referer': url})
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)


        end_time = time.perf_counter()
        time_taken = end_time - start_time
        resp = Response(b, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), time_taken, self.user_no, self.group_no)
        resp.assert_contains()
        return await resp.get_ltr()
