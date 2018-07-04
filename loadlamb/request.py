import random

from loadlamb.response import Response


class Request(object):

    def __init__(self,session, req_config, proj_config, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session

    def run(self):
        path = '{}{}'.format(self.proj_config.get('url'),
                             self.req_config.get('path'))
        method_type = self.req_config.get('method_type')
        data = self.req_config.get('data')
        payload = self.req_config.get('payload')

        timeout = self.req_config.get('timeout') or \
                  self.proj_config.get('timeout',30)
        if data:
            data = self.get_choice(data)
            resp = self.session.request(method_type,path,data=data,timeout=timeout)
        elif payload:
            payload = self.get_choice(payload)
            resp = self.session.request(method_type, path, timeout=timeout, payload=payload)
        else:
            resp = self.session.request(method_type, path, timeout=timeout)
        return Response(resp,self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'))

    def get_choice(self,choice_list):
        return random.choice(choice_list)