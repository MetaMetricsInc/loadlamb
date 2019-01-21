import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_csrf_token


class DjangoPost(Request):

    async def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'), self.req_config.get('path'))
        a = await self.session.request('get', url)

        data = random.choice(self.req_config.get('data', {}))
        data['csrfmiddlewaretoken'] = get_csrf_token(a)
        b = await self.session.request('post', url, data=data, headers={'referer': url})
        resp = Response(b, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))
        resp.assert_contains()
        return resp.get_ltr()