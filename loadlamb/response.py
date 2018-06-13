class LoadLambResponse(object):
    def __init__(self,response,content_str):
        self.response = response
        self.content_str = content_str

    def save(self):
        pass


class ContentNotFound(LoadLambResponse):
    pass


class ContentResponse(LoadLambResponse):
    pass