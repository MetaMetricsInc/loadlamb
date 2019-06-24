import asyncio
import time

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

        method_type = self.req_config.get('method_type')
        data = self.req_config.get('data')
        params = self.req_config.get('params')

        start_time = time.perf_counter()
        try:
            if data:
                data = self.get_choice(data)
                resp = await self.session.request(method_type, path, json=data, timeout=self.timeout)
            elif params:
                params = self.get_choice(params)
                resp = await self.session.request(method_type, path, payload=params,
                                                  timeout=self.timeout)
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

