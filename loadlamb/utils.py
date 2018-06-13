import base58
import importlib
import re

import yaml
from bs4 import BeautifulSoup


def get_form_values(resp):
    return {i.get('name'): i.get('value') for i in list(
        BeautifulSoup(resp.content).find('form').children) if i.get('type') == 'hidden'}


def get_form_action(resp):
    return BeautifulSoup(resp.content).find('form').attrs['action']


def get_csrf_token(resp):
    cookies = resp.cookies.get_dict()
    cookies_keys = cookies.keys()
    if 'zappa' in cookies_keys and not 'csrftoken' in cookies_keys:
        zap_str = str(base58.b58decode(cookies.get('zappa')))
        return re.match(r'^b\'{"csrftoken": "(?P<csrf_token>[-\w]+);',
                        zap_str).group('csrf_token')
    return cookies.get('csrftoken')


def import_util(imp):
    '''
    Lazily imports a utils (class,
    function,or variable) from a module) from
    a string.
    @param imp:
    '''

    mod_name, obj_name = imp.rsplit('.', 1)
    mod = importlib.import_module(mod_name)
    return getattr(mod, obj_name)


def create_config_file(config):
    with open('loadlamb.yml', 'w+') as f:
        f.write(yaml.safe_dump(config, default_flow_style=False))

def save_sam_template(template):
    with open('sam.yml', 'w+') as f:
        f.write(template.get_template())