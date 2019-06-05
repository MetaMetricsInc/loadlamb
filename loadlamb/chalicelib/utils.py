import datetime
import inspect
import itertools
import json
import os
import shutil
import time

import base58
import importlib
import re

import boto3
import jinja2

import yaml
from pip._internal import main as _main
from bs4 import BeautifulSoup
from unipath import FSPath as path
import sammy as sm

import loadlamb
from loadlamb.chalicelib.contrib.db.loading import docb_handler

from loadlamb.chalicelib.sam import s, r, s3t

cf = boto3.client('cloudformation')

CLI_TEMPLATES = jinja2.Environment(loader=jinja2.PackageLoader(
    'loadlamb.chalicelib', 'templates'))


async def get_form_values(resp):
    content = await resp.text()
    form_children = list(filter(lambda x: hasattr(x, 'get'), list(BeautifulSoup(content).find('form').children)))
    return {i.get('name'): i.get('value') for i in form_children if i.get('type') == 'hidden'}


async def get_form_action(resp):
    return BeautifulSoup(await resp.text()).find('form').attrs['action']


def get_csrf_token(resp):
    cookies = resp.cookies
    cookies_keys = cookies.keys()
    if 'zappa' in cookies_keys and not 'csrftoken' in cookies_keys:
        zap_str = str(base58.b58decode(cookies.get('zappa').value))
        return re.match(r'^b\'{"csrftoken": "(?P<csrf_token>[-\w]+);',
                        zap_str).group('csrf_token')
    return cookies.get('csrftoken').value


def grouper(n, total):
    iterable = range(total)

    def grouper_g(n, iterable):
        it = iter(iterable)
        while True:
            chunk = tuple(itertools.islice(it, n))
            if not chunk:
                return
            yield len(chunk)

    return list(grouper_g(n, iterable))


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


def create_config_file(config, filename='loadlamb.yaml'):
    with open(filename, 'w+') as f:
        f.write(yaml.safe_dump(config, default_flow_style=False))


def read_config_file(config_file=None):
    with open(config_file or 'loadlamb.yaml', 'r') as f:
        c = yaml.load(f.read())
    return c


def save_sam_template():
    with open('sam.yml', 'w+') as f:
        f.write(s.get_template())


def create_extension_template(name, description, config_file='loadlamb.yaml'):
    class_name = name.title().replace(' ', '')
    path_name = name.lower().replace(' ', '_')
    os.makedirs(path_name)
    os.makedirs('{n}/{n}'.format(n=path_name))
    # Create __init__.py
    with open('{n}/{n}/__init__.py'.format(n=path_name.lower()), 'w+') as f:
        f.write('')

    with open('{}/requirements.txt'.format(path_name.lower()), 'w+') as f:
        f.write('')

    with open('{n}/{n}/requests.py'.format(n=path_name.lower()), 'w+') as f:
        request_template = CLI_TEMPLATES.get_template('extension.py.jinja2')
        f.write(request_template.render(extension_name=class_name))

    with open('{}/setup.py'.format(path_name), 'w+') as f:
        setup_template = CLI_TEMPLATES.get_template('setup.py.jinja2')
        f.write(setup_template.render(extension_name=path_name,
                                      description=description))

    t = read_config_file(config_file=config_file)
    exts = t.get('extensions', [])
    exts.append(path_name)
    exts = list(set(exts))
    t['extensions'] = exts
    create_config_file(t, filename=config_file)


def execute_loadlamb(stage, region_name=None, config_file=None, profile_name='default'):
    sess = boto3.Session(profile_name=profile_name)
    config = read_config_file(config_file=config_file)
    config['active_stage'] = stage
    lm = sess.client('lambda', region_name=region_name)
    lm.invoke(
        FunctionName='loadlamb-run',
        InvocationType='Event',
        Payload=json.dumps(config),
    )


class Deploy(object):
    config_path = 'loadlamb.yaml'
    venv = '_venv'
    requirements_filename = 'requirements.txt'
    zip_name = 'loadlamb.zip'

    def __init__(self, project_config, region_name='us-east-1', profile_name='default'):
        self.project_config = project_config
        self.region_name = region_name
        self.profile_name = profile_name
        self.build_clients_resources(profile_name=self.profile_name, region_name=self.region_name)

    def build_clients_resources(self, profile_name='default', region_name='us-east-1'):
        self.s = s
        self.s.build_clients_resources(region_name=region_name, profile_name=profile_name)
        self.r = r
        self.r.build_clients_resources(region_name=region_name, profile_name=profile_name)
        self.s3t = s3t
        self.s3t.build_clients_resources(region_name=region_name, profile_name=profile_name)
        self.sess = boto3.Session(region_name=region_name, profile_name=profile_name)
        self.s3 = self.sess.client('s3')

    def install_packages(self, ext_name=None):
        """
        Install loadlamb's reqs to the self.venv or install an extension and
        it's reqs to the self.venv
        :param ext_name: Name of the extension to install
        :return:
        """
        if not ext_name:
            # If there is no extension name we can assume we are installing loadlamb's requirements
            _main(['install', '-r',
                   '{}/{}'.format(self.get_loadlamb_path(), self.requirements_filename),
                   '-t', self.venv])
        elif ext_name:

            # If there is an extension name we can assumme it is for an extension
            _main(['install',
                   '{}/'.format(ext_name),
                   '-t', self.venv, '--src', '{}/_src'.format(self.venv)])

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

    def create_package_name(self):
        self.zip_name = 'loadlamb-{}.zip'.format(time.time())

    @property
    def regions(self):
        return self.project_config['regions']

    def publish(self):
        """
        Runs all of the methods required to build the virtualenv folder,
        create a zip file, upload that zip file to S3, create a SAM
        template, and deploy that SAM template.
        :return:
        """

        regions = self.project_config['regions']
        self.create_package_name()
        self.create_package()
        print('Publishing Loadlamb Role')
        self.r.publish('loadlamb-role')

        try:
            for i in regions:
                self.build_clients_resources(profile_name=self.profile_name, region_name=i)
                try:
                    dets = self.s.cf_resource.Stack('loadlamb-bucket')
                    bucket_name = list(filter(lambda x: x.get('OutputKey') == 'bucket', dets.outputs))[0]['OutputValue']
                except:
                    dets = self.s3t.publish('loadlamb-bucket')
                    bucket_name = list(filter(lambda x: x.get('OutputKey') == 'bucket', dets.outputs))[0]['OutputValue']
                print('Publishing LoadLamb Code in {} region.'.format(i))
                # Upload the zip file to the specified bucket in the project config
                self.upload_zip(bucket_name)
                loadlamb_config = 'load-lamb-{}.yaml'.format(datetime.datetime.now())
                self.s.publish_template(bucket_name, loadlamb_config)
                self.s.publish('loadlamb', CodeBucket=bucket_name, CodeZipKey=self.zip_name)
        except Exception as e:
            self.remove_zip_venv()
            raise sm.DeployFailedError(e)
        self.remove_zip_venv()
        # TODO: Add profile_name to publish_global in DocB
        try:
            docb_handler.publish_global('loadlamb', 'loadlambddb', 'loadlambddb', 'dynamodb',
                                        replication_groups=regions,
                                        profile_name=self.profile_name)
        except Exception:
            pass

    def unpublish(self):
        self.r.unpublish('loadlamb-role')
        for i in self.regions:
            self.build_clients_resources(profile_name=self.profile_name, region_name=i)
            self.s.unpublish('loadlamb')

    def get_loadlamb_path(self, imodule=loadlamb.chalicelib, ancestor=0):
        """
        Get loadlamb's path in the user's virtualenv
        :return: Unipath path object
        """
        return path(
            os.path.dirname(
                inspect.getsourcefile(imodule))).ancestor(1)

    def copy_loadlamb(self):
        # Get loadlamb's path in the user's virtualenv
        loadlamb_path = self.get_loadlamb_path(imodule=loadlamb, ancestor=1)
        # Copy loadlamb to self.venv
        shutil.copytree(loadlamb_path, self.venv)

    def build_zip(self):
        shutil.make_archive(self.zip_name.replace('.zip', ''), 'zip', self.venv)

    def upload_zip(self, bucket):
        print('Uploading Zip {} to {} bucket.'.format(self.zip_name, bucket))
        self.s3.upload_file(self.zip_name, bucket, self.zip_name)
        return bucket, self.zip_name
