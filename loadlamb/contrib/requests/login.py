import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_form_values, get_csrf_token


class RemoteLogin(Request):

    def run(self):
        responses = []
        url = '{}{}'.format(
            self.proj_config.get('url'),self.req_config.get('path'))
        a = self.session.request('get',url)
        responses.append(a)
        b = self.session.request('post', self.req_config.get('login_url'), data=get_form_values(a))
        responses.append(b)
        c = self.session.request('get', b.url)
        responses.append(c)
        self.session.headers.update({'referer': url})
        user = random.choice(self.req_config.get('users'))
        d = self.session.request('post', b.url, data={'username': user.get('username'),
                                        'password': user.get('password'),
                                        'csrfmiddlewaretoken': get_csrf_token(c)})
        responses.append(d)
        self.session.headers.pop('referer')
        e = Response(c,self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))
        responses.append(e)
        return responses