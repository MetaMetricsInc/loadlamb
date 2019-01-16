import asyncio
import random
import time

from loadlamb.response import Response
from loadlamb.utils import import_util

METHOD_TYPES = ['get', 'post', 'put', 'head', 'delete']


class User(object):

    def __init__(self, config, session):
        """

        :param config:
        :param session:
        """
        self.config = config
        self.session = session

    async def run(self):
        return await asyncio.gather(*[Request(self.session, i, self.config).run() for i in self.config['tasks']])


class Request(object):

    def __init__(self, session, req_config, proj_config, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session

    async def run(self):
        """
        Executes a single request
        :return: Response class
        """
        path = '{}{}'.format(self.proj_config.get('url'),
                             self.req_config.get('path'))
        method_type = self.req_config.get('method_type')
        data = self.req_config.get('data')
        params = self.req_config.get('params')

        timeout = self.req_config.get('timeout') or \
                  self.proj_config.get('timeout', 30)
        start_time = time.perf_counter()
        if data:
            data = self.get_choice(data)
            resp = await self.session.request(method_type, path, data=data, timeout=timeout)
        elif params:
            params = self.get_choice(params)
            resp = await self.session.request(method_type, path, payload=params, timeout=timeout)
        else:
            resp = await self.session.request(method_type, path)
        end_time = time.perf_counter()
        resp = Response(resp, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time)
        resp.assert_contains()
        return resp.get_ltr()

    def get_choice(self, choice_list):
        return random.choice(choice_list)
