import asyncio
import time

from aiohttp import ClientResponseError
from aiohttp_xmlrpc.client import ServerProxy

from loadlamb.chalicelib.request import Request
from loadlamb.chalicelib.response import Response


class XMLRPCRequest(Request):

    def get_timeout(self):
        return self.req_config.get('timeout') or \
                  self.proj_config.get('timeout', 30)

    async def run(self):
        """
        Executes a single request
        :return: Response class
        """
        path = '{}{}'.format(self.get_url(),
                             self.req_config.get('path'))

        data = self.req_config.get('data')

        start_time = time.perf_counter()

        client = ServerProxy(path, client=self.session)

        method = client[self.req_config.get('method')]
        try:
            if data:
                data = self.get_choice(data).get('params', [])
                resp = await method(*data)
            else:
                return await self.get_null_response(self.timeout)
        except (asyncio.TimeoutError, ClientResponseError):
            return await self.get_null_response(self.timeout)
        end_time = time.perf_counter()

        resp = Response(resp, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time, self.user_no, self.group_no, text=resp,
                        status_code=200)
        await resp.assert_contains()
        ltr = await resp.get_ltr()

        return ltr

