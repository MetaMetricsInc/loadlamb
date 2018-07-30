import random

from loadlamb.request import Request
from loadlamb.response import Response
from loadlamb.utils import get_form_values, get_csrf_token, get_form_action


class RemoteLogin(Request):

    def run(self):
        responses = []
        url = '{}{}'.format(
            self.proj_config.get('url'),self.req_config.get('path'))

        # Request to the login url on the main site
        a = self.session.get(url)

        responses.append(Response(a,self.req_config,
                                  self.proj_config.get('project_slug'),
                                  self.proj_config.get('run_slug')))

        # Add referer header to the session based on the url from the previous request
        self.session.headers.update({'Referer': a.url})
        # POST request to the login url on the remote site using the
        # form values from request A

        b = self.session.post(get_form_action(a), data=get_form_values(a),allow_redirects=False)
        responses.append(Response(b, self.req_config,
                                  self.proj_config.get('project_slug'),
                                  self.proj_config.get('run_slug')))

        location_url = b.headers['Location']
        self.session.headers.update({'Referer': b.url})
        c = self.session.get(self.req_config.get('login_url'), cookies=b.cookies.get_dict())
        responses.append(Response(c, self.req_config,
                                  self.proj_config.get('project_slug'),
                                  self.proj_config.get('run_slug')))





        # Choose a user at random to log in as
        user = random.choice(self.req_config.get('users'))
        form_data = {'username': user.get('username'),
                                        'password': user.get('password'),
                                        'csrfmiddlewaretoken': get_csrf_token(c)}

        # POST request to the login url on the remote site
        d = self.session.post(c.url, data=form_data)

        responses.append(Response(d, self.req_config,
                                  self.proj_config.get('project_slug'),
                                  self.proj_config.get('run_slug')))

        e = self.session.post(get_form_action(d),data=get_form_values(d))
        responses.append(Response(e, self.req_config,
                                  self.proj_config.get('project_slug'),
                                  self.proj_config.get('run_slug')))
        # Remove the Referer header from the session
        self.session.headers.pop('Referer')

        return responses