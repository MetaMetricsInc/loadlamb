from loadlamb.chalicelib.contrib.db.models import LoadTestResponse


class Response(object):
    def __init__(self, response, request_config, project_slug, run_slug, time_taken, user_no, group_no):
        self.response = response
        self.request_config = request_config
        self.time_taken = time_taken
        self.project_slug = project_slug
        self.run_slug = run_slug
        self.user_no = user_no
        self.group_no = group_no

    async def assert_contains(self):
        try:
            contains = self.request_config['contains']
        except KeyError:
            return True
        self.text = await self.response.text()
        return contains in str(self.text)

    async def get_ltr(self):
        return LoadTestResponse(
            run_slug=self.run_slug,
            body=await self.response.text(),
            user_no=self.user_no,
            group_no=self.group_no,
            project_slug=self.project_slug,
            path=self.request_config.get('path'),
            elapsed_time=self.time_taken,
            contains_string=self.request_config.get('contains'),
            status_code=self.response.status,
            method_type=self.request_config.get('method_type')
        )
