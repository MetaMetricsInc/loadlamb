import asyncio
import itertools
import random
import time

from loadlamb.chalicelib.response import Response
from loadlamb.chalicelib.utils import import_util
from loadlamb.chalicelib.contrib.db.models import Group as GroupModel

METHOD_TYPES = ['get', 'post', 'put', 'head', 'delete']


class NullResponse(object):

    def __init__(self):
        self.status = 408
        self.content = ''

    async def text(self):
        return 'Null Response'


class Group(object):

    def __init__(self, no_users, session, config, group_no):
        self.config = config
        self.group_no = group_no
        self.session = session
        self.no_users = no_users

    def filter_status_code(self, results, starts_with):
        return len(list(filter(lambda x: str(x.status_code).startswith(starts_with), results)))

    async def run(self):
        sleep_time = self.config.get('user_batch_sleep') * self.group_no
        await asyncio.sleep(sleep_time)
        start_time = time.perf_counter()
        results = await asyncio.gather(
            *[User(self.config, self.session, user_no, self.group_no).run() for user_no in range(self.no_users)])
        end_time = time.perf_counter()

        elapsed_time = end_time - start_time
        requests_per_second = self.no_users / elapsed_time
        results = list(itertools.chain.from_iterable(results))

        g = GroupModel(project_slug=self.config['project_slug'], run_slug=self.config['run_slug'],
                       group_no=self.group_no, requests_per_second=requests_per_second, elapsed_time=elapsed_time,
                       completed=True, error_msg='', status_500=self.filter_status_code(results, '5'),
                       status_400=self.filter_status_code(results, '4'),
                       status_200=self.filter_status_code(results, '2'),
                       )

        g.responses = results
        return g


class User(object):

    def __init__(self, config, session, user_no, group_no):
        """

        :param config:
        :param session:
        """
        self.config = config
        self.session = session
        self.user_no = user_no
        self.group_no = group_no

    async def run(self):
        req_list = list()
        for i in self.config['tasks']:
            if i.get('method_type', '').lower() in METHOD_TYPES and not i.get('request_class'):
                req_list.append(Request(self.session, i, self.config, self.user_no, self.group_no).run())
            else:
                req_list.append(import_util(i.get('request_class'))(
                    self.session, i, self.config, self.user_no, self.group_no).run())
        return await asyncio.gather(*req_list)


class Request(object):

    def __init__(self, session, req_config, proj_config, user_no, group_no, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session
        self.user_no = user_no
        self.group_no = group_no
        self.timeout = self.get_timeout()

    async def get_null_response(self, timeout):
        resp = Response(NullResponse(), self.req_config, self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'),
                        timeout, self.user_no, self.group_no)
        return await resp.get_ltr()

    def get_timeout(self):
        return self.req_config.get('timeout') or \
                  self.proj_config.get('timeout', 30)

    def get_url(self):
        try:
            stg = next(filter(lambda x: x.get('name') == self.proj_config.get('active_stage'),
                     self.proj_config.get('stages', [])))
        except StopIteration:
            stg = {}
        return stg.get('url')

    async def run(self):
        """
        Executes a single request
        :return: Response class
        """
        path = '{}{}'.format(self.get_url(),
                             self.req_config.get('path'))
        method_type = self.req_config.get('method_type')
        data = self.req_config.get('data')
        params = self.req_config.get('params')

        start_time = time.perf_counter()
        try:
            if data:
                data = self.get_choice(data)
                resp = await self.session.request(method_type, path, data=data, timeout=self.timeout)
            elif params:
                params = self.get_choice(params)
                resp = await self.session.request(method_type, path, payload=params, timeout=self.timeout)
            else:
                resp = await self.session.request(method_type, path)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)
        end_time = time.perf_counter()

        resp = Response(resp, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time, self.user_no, self.group_no)
        await resp.assert_contains()
        ltr = await resp.get_ltr()
        return ltr

    def get_choice(self, choice_list):
        return random.choice(choice_list)
