import asyncio
import random
import time

from loadlamb.chalicelib.request import Request
from loadlamb.chalicelib.response import Response

from warrant_lite import WarrantLite


class CogntioRequest(Request):

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

        try:
            self.session._loadlamb_tokens
        except AttributeError:
            user = random.choice(self.proj_config.get('users'))
            wl = WarrantLite(
                username=user.get('username'), password=user.get('password'), pool_id=self.proj_config.get('pool_id'),
                client_id=self.proj_config.get('client_id')

            )
            self.session._loadlamb_tokens = wl.authenticate_user()

        headers = {'Authorization': self.session._loadlamb_tokens['AuthenticationResult']['IdToken'],
                   'Accept':'application/json; version=1.0'}
        start_time = time.perf_counter()
        try:
            if data:
                data = self.get_choice(data)
                resp = await self.session.request(method_type, path, headers=headers, json=data, timeout=self.timeout)
            elif params:
                params = self.get_choice(params)
                resp = await self.session.request(method_type, path, headers=headers, payload=params,
                                                  timeout=self.timeout)
            else:
                resp = await self.session.request(method_type, path, headers=headers)
        except asyncio.TimeoutError:
            return await self.get_null_response(self.timeout)
        end_time = time.perf_counter()

        resp = Response(resp, self.req_config,
                        self.proj_config.get('project_slug'),
                        self.proj_config.get('run_slug'), end_time - start_time, self.user_no, self.group_no)
        await resp.assert_contains()
        ltr = await resp.get_ltr()
        return ltr

