class LoadLambResponse(object):
    def __init__(self,response,content_str):
        self.response = response
        self.content_str = content_str

    def save(self):
        pass


class ContentNotFound(LoadLambResponse):
    pass


class ContentResponse(object):
    pass


class Request(object):

    def __init__(self,session, req_config, proj_config, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session

    def run(self):
        path = '{}{}'.format(self.proj_config.get('url'),self.req_config.get('path'))
        return self.assert_contains(self.session.request(self.req_config.get('method_type'),
                                    path,**self.kwargs))

    def assert_contains(self,response):
        c = self.req_config.get('contains')
        if c:
            if not c in response.content:
                return ContentNotFound(response,c)
        return response