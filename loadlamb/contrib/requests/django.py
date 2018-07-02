import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_form_values, get_csrf_token


class DjangoPost(Request):

    def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'),self.req_config.get('path'))
        a = self.session.request('get',url)
        self.session.headers.update({'referer': url})
        user = random.choice(self.req_config.get('users'))
        data = self.req_config.get('data',{})
        data['csrfmiddlewaretoken'] = get_csrf_token(a)
        b = self.session.request('post', url, data={'username': user.get('username'),
                                        'password': user.get('password'),
                                        'csrfmiddlewaretoken': get_csrf_token(a)})
        self.session.headers.pop('referer')
        return Response(b,self.req_config,self.proj_config.get('name'))
