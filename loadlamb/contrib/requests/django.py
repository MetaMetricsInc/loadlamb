import asyncio
import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_csrf_token


class DjangoPost(Request):

    async def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'), self.req_config.get('path'))
        try:
            a = await self.session.request('get', url)
        except asyncio.TimeoutError:
            return self.get_null_response(self.timeout)
        data = random.choice(self.req_config.get('data', {}))
        try:
            data['csrfmiddlewaretoken'] = get_csrf_token(a)
        except AttributeError:
            return self.get_null_response(self.timeout)
        try:
            b = await self.session.request('post', url, data=data, headers={'referer': url})
        except asyncio.TimeoutError:
            return self.get_null_response(self.timeout)

        resp = Response(b, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))
        resp.assert_contains()
        return resp.get_ltr()
