import datetime
import inspect
import itertools
import json
import os
import shutil

import base58
import importlib
import re

import boto3
import jinja2

import yaml
from pip._internal import main as _main
from bs4 import BeautifulSoup
from unipath import FSPath as path

import loadlamb

from loadlamb.sam import s


s3 = boto3.client('s3')

cf = boto3.client('cloudformation')

lm = boto3.client('lambda')

CLI_TEMPLATES = jinja2.Environment(loader=jinja2.PackageLoader(
    'loadlamb','templates'))


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


def grouper(n, total):
    iterable = range(total)
    def grouper_g(n,iterable):
        it = iter(iterable)
        while True:
           chunk = tuple(itertools.islice(it, n))
           if not chunk:
               return
           yield len(chunk)
    return list(grouper_g(n,iterable))


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
    with open('loadlamb.yaml', 'w+') as f:
        f.write(yaml.safe_dump(config, default_flow_style=False))


def read_config_file():
    with open('loadlamb.yaml','r') as f:
        c = yaml.load(f.read())
    return c


def save_sam_template():
    with open('sam.yml', 'w+') as f:
        f.write(s.get_template())


def create_extension_template(name,description):
    class_name = name.title().replace(' ','')
    path_name = name.lower().replace(' ','_')
    os.makedirs(path_name)
    os.makedirs('{n}/{n}'.format(n=path_name))
    # Create __init__.py
    with open('{n}/{n}/__init__.py'.format(n=path_name.lower()), 'w+') as f:
        f.write('')

    with open('{}/requirements.txt'.format(path_name.lower()), 'w+') as f:
        f.write('')

    with open('{n}/{n}/requests.py'.format(n=path_name.lower()),'w+') as f:
        request_template = CLI_TEMPLATES.get_template('extension.py.jinja2')
        f.write(request_template.render(extension_name=class_name))

    with open('{}/setup.py'.format(path_name),'w+') as f:
        setup_template = CLI_TEMPLATES.get_template('setup.py.jinja2')
        f.write(setup_template.render(extension_name=path_name,
                                      description=description))

    t = read_config_file()
    exts = t.get('extensions', [])
    exts.append(path_name)
    exts = list(set(exts))
    t['extensions'] = exts
    create_config_file(t)


def execute_loadlamb(delay=None):
    config = read_config_file()
    if delay:
        config['delay'] = delay
    lm.invoke(
        FunctionName='loadlamb-push',
        InvocationType='Event',
        Payload=json.dumps(read_config_file()),
    )


class Deploy(object):

    config_path = 'loadlamb.yaml'
    venv = '_venv'
    requirements_filename = 'requirements.txt'
    zip_name = 'loadlamb.zip'

    def __init__(self,project_config):
        self.project_config = project_config

    def install_packages(self,ext_name=None):
        """
        Install loadlamb's reqs to the self.venv or install an extension and
        it's reqs to the self.venv
        :param ext_name: Name of the extension to install
        :return:
        """
        if not ext_name:
            #If there is no extension name we can assume we are installing loadlamb's requirements
            _main(['install','-r',
                  '{}/{}'.format(self.get_loadlamb_path(),self.requirements_filename),
                  '-t',self.venv])
        elif ext_name:

            #If there is an extension name we can assumme it is for an extension
            _main(['install',
                      '{}/'.format(ext_name),
                      '-t', self.venv,'--src','{}/_src'.format(self.venv)])

    def remove_zip_venv(self):
        self.remove_venv()

    def remove_zip(self):
        os.remove('loadlamb.zip')

    def remove_venv(self):
        shutil.rmtree('_venv')

    def create_package(self):
        self.copy_loadlamb()
        self.install_packages()
        # Copy loadlamb's files and install reqs to the self.venv folder

        # Install all of the extensions to the self.venv folder
        for i in self.project_config.get('extensions', []):
            self.install_packages(ext_name=i)
        # Zip the self.venv folder
        self.build_zip()

    def publish(self):
        """
        Runs all of the methods required to build the virtualenv folder,
        create a zip file, upload that zip file to S3, create a SAM
        template, and deploy that SAM template.
        :return:
        """
        self.create_package()
        #Upload the zip file to the specified bucket in the project config
        self.upload_zip()
        self.remove_zip_venv()
        s.publish_template(self.project_config.get(
            'bucket'),'load-lamb-{}.yaml'.format(datetime.datetime.now()))
        s.publish('loadlamb', CodeBucket=self.project_config.get('bucket'),
                  CodeZipKey='loadlamb.zip')

    def unpublish(self):
        s.unpublish('loadlamb')

    def get_loadlamb_path(self):
        """
        Get loadlamb's path in the user's virtualenv
        :return: Unipath path object
        """
        return path(
            os.path.dirname(
                inspect.getsourcefile(loadlamb))).ancestor(1)

    def copy_loadlamb(self):
        # Get loadlamb's path in the user's virtualenv
        loadlamb_path = self.get_loadlamb_path()
        # Copy loadlamb to self.venv
        shutil.copytree(loadlamb_path,self.venv)

    def build_zip(self):
        shutil.make_archive(self.zip_name.replace('.zip',''),'zip',self.venv)

    def upload_zip(self):
        bucket = self.project_config.get('bucket')
        print('Uploading Zip {} to {} bucket.'.format(self.zip_name,bucket))
        s3.upload_file(self.zip_name,bucket,self.zip_name)
        return bucket, self.zip_name