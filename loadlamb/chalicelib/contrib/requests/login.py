import asyncio
import random
import time

from loadlamb.chalicelib.request import Request
from loadlamb.response import Response
from loadlamb.chalicelib.utils import get_form_values, get_csrf_token


class RemoteLogin(Request):

    async def run(self):
        url = '{}{}'.format(
            self.get_url(), self.req_config.get('path'))

        start_time = time.perf_counter()
        try:
            a = await self.session.request('get', url, timeout=self.timeout)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)
        login_url = '{}{}'.format(self.proj_config.get('url'), self.req_config.get('login_url'))
        try:
            b = await self.session.request('post', login_url, data=await get_form_values(a),
                                           timeout=self.timeout)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)

        try:
            c = await self.session.request('get', b.url)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)

        user = random.choice(self.proj_config.get('users'))
        try:
            d = await self.session.request('post', b.url, headers={'referer': url}, timeout=self.timeout,
                                       data={'username': user.get('username'), 'password': user.get('password'),
                                            'csrfmiddlewaretoken': get_csrf_token(c)})
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)

        end_time = time.perf_counter()
        resp = Response(d, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time, self.user_no, self.group_no)
        await resp.assert_contains()
        return await resp.get_ltr()

