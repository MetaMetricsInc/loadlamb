class Response(object):
    def __init__(self,response,request_config,project_slug):
        self.response = response
        self.request_config = request_config
        self.project_slug = project_slug

    def save(self):
        pass