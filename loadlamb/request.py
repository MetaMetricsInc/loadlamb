import asyncio
import random
import time

from loadlamb.response import Response
from loadlamb.utils import import_util

METHOD_TYPES = ['get', 'post', 'put', 'head', 'delete']


class NullResponse(object):

    def __init__(self):
        self.status = 408
        self.content = ''

    async def text(self):
        return 'Null Response'



class User(object):

    def __init__(self, config, session):
        """

        :param config:
        :param session:
        """
        self.config = config
        self.session = session

    async def run(self):
        req_list = list()
        for i in self.config['tasks']:
            if i.get('method_type','').lower() in METHOD_TYPES and not i.get('request_class'):
                req_list.append(Request(self.session, i, self.config).run())
            else:
                req_list.append(import_util(i.get('request_class'))(self.session, i, self.config).run())
        return await asyncio.gather(*req_list)


class Request(object):

    def __init__(self, session, req_config, proj_config, **kwargs):
        self.req_config = req_config
        self.proj_config = proj_config
        self.kwargs = kwargs
        self.session = session
        self.timeout = self.get_timeout()

    async def get_null_response(self, timeout):
        resp = Response(NullResponse(), self.req_config, self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'),
                        timeout)
        return await resp.get_ltr()

    def get_timeout(self):
        return self.req_config.get('timeout') or \
                  self.proj_config.get('timeout', 30)

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
                        self.proj_config.get('run_slug'), end_time - start_time)
        await resp.assert_contains()
        ltr = await resp.get_ltr()
        return ltr

    def get_choice(self, choice_list):
        return random.choice(choice_list)
