from loadlamb.response import ContentNotFound


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
        return self.check_contains(
            self.session.request(method_type,
                        path,
                        timeout=self.req_config.get('timeout')
                                or self.proj_config.get('timeout',30),
                                 **self.kwargs))

    def check_contains(self,response):
        c = self.req_config.get('contains')
        if c:
            if not c in response.content:
                return ContentNotFound(response,c)
        return response