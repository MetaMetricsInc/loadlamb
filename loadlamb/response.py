class LoadLambResponse(object):
    def __init__(self,response,content_str,path,project_slug,method_type=None):
        self.response = response
        self.content_str = content_str
        self.path = path
        self.project_slug = project_slug
        self.method_type = method_type

    def save(self):
        pass


class ContentNotFound(LoadLambResponse):
    pass


class ContentResponse(LoadLambResponse):
    pass