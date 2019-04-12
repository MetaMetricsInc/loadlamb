import asyncio

from loadlamb.load import LoadLamb
from loadlamb.contrib.db.models import Run


class LoadLambTestRunner(object):
    loadlamb_config = {}
    docb_class = Run

    def __init__(self):
        self.loop = asyncio.get_event_loop()

    async def run_loadlamb(self):
        return await LoadLamb(self.loadlamb_config).run()

    @property
    def no_requests(self):
        return len(self.loadlamb_config['tasks']) * self.loadlamb_config['user_num']


class FlaskTestRunner(LoadLambTestRunner):

    loadlamb_config = {
        'name': 'flask',
        'url': 'http://flask:5000',
        'repo_url': 'https://github.com/metametricsinc/loadlamb',
        'user_num': 10,
        'user_batch_size': 10,
        'user_batch_sleep': 2,
        'tasks': [
            {'path': '/get', 'method_type': 'GET'},
            {'path': '/post', 'method_type': 'POST'},
            {'path': '/bad-get', 'method_type': 'GET'},
        ]
    }


class DjangoTestRunner(LoadLambTestRunner):

    loadlamb_config = {
        'name': 'django',
        'url': 'http://django:8001',
        'repo_url': 'https://github.com/metametricsinc/loadlamb',
        'user_num': 10,
        'user_batch_size': 10,
        'user_batch_sleep': 2,
        'tasks': [
            {'path': '/accounts/profile/', 'request_class': 'loadlamb.contrib.requests.django_login.DjangoLogin',
             'data': [{'username': 'loadlamb', 'password': '12345678'},
                      {'username': 'loadlamb2', 'password': '12345678'},
             ]}
        ]
    }


def test_flask():
    runner = FlaskTestRunner()
    result = runner.loop.run_until_complete(asyncio.wait_for(runner.run_loadlamb(), 300))
    run = Run.objects().get({'run_slug': result['run_slug']})
    assert runner.no_requests == result['requests']
    assert runner.no_requests / 3 == run.status_500
    assert runner.no_requests == run.requests


def test_django():
    runner = DjangoTestRunner()
    result = runner.loop.run_until_complete(asyncio.wait_for(runner.run_loadlamb(), 300))
    run = Run.objects().get({'run_slug': result['run_slug']})
    assert runner.no_requests == result['requests']
    assert runner.no_requests == run.status_200
