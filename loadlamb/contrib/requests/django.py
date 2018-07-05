import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_csrf_token


class DjangoPost(Request):

    def run(self):
        url = '{}{}'.format(
            self.proj_config.get('url'),self.req_config.get('path'))
        a = self.session.request('get',url)
        self.session.headers.update({'referer': url})
        data = random.choice(self.req_config.get('data',{}))
        data['csrfmiddlewaretoken'] = get_csrf_token(a)
        b = self.session.request('post', url, data=data)
        self.session.headers.pop('referer')
        return Response(b,self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))
