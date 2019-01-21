import random
import time

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_form_values, get_csrf_token


class RemoteLogin(Request):

    async def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'),self.req_config.get('path'))
        timeout = self.req_config.get('timeout') or \
                  self.proj_config.get('timeout', 30)
        start_time = time.perf_counter()
        a = await self.session.request('get',url, timeout=timeout)
        b = await self.session.request('post', self.req_config.get('login_url'), data=await get_form_values(a),
                                       timeout=timeout)
        c = await self.session.request('get', b.url)
        user = random.choice(self.req_config.get('users'))
        c = await self.session.request('post', b.url, headers={'referer': url}, timeout=timeout,
                                       data={'username': user.get('username'),
                                        'password': user.get('password'),
                                        'csrfmiddlewaretoken': get_csrf_token(c)})
        end_time = time.perf_counter()
        resp = Response(c, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time)
        resp.assert_contains()
        return resp.get_ltr()
