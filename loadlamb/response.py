from loadlamb.contrib.db.models import LoadTestResponse


class Response(object):
    def __init__(self,response,request_config,project_slug,run_slug):
        self.response = response
        self.request_config = request_config
        self.project_slug = project_slug
        self.run_slug = run_slug

    def assert_contains(self):
        try:
            contains = self.request_config['contains']
        except KeyError:
            return True
        return contains in str(self.response.content)

    def save(self):
        ltr = LoadTestResponse(
            run_slug=self.run_slug,
            project_slug=self.project_slug,
            path=self.response.url,
            elapsed_time=self.response.elapsed.total_seconds(),
            contains_string=self.request_config.get('contains'),
            status_code=self.response.status_code,
            method_type=self.response.request.method,
            body=str(self.response.content),
            headers=self.response.request.headers
        )
        ltr.save()
