import os

import click

from loadlamb.contrib.db.models import Run
from loadlamb.utils import create_config_file, read_config_file, Deploy, create_extension_template, execute_loadlamb, \
    save_sam_template


@click.group()
def loadlamb():
    pass


def validate_regions(ctx, param, value):
    return value.replace(" ", "").split(',')


@loadlamb.command()
@click.option('--name', prompt=True)
@click.option('--url', prompt=True)
@click.option('--repo_url', prompt=True)
@click.option('--user_num', prompt=True)
@click.option('--user_batch_size', prompt=True, help='Max value: 10')
@click.option('--regions', prompt=True, callback=validate_regions,
              help='Comma delimited list of AWS region short names. ex. us-east-1, us-east-2')
@click.option('--filename')
def create_project(name, url, repo_url, user_num, user_batch_size, regions, filename='loadlamb.yaml'):
    create_config_file({
        'name': name,
        'url': url,
        'repo_url': repo_url,
        'user_num': int(user_num),
        'user_batch_size': int(user_batch_size),
        'regions': regions,
        'tasks': [
            {'path': '/', 'method_type': 'GET'}
        ]
    }, filename=filename)
    click.echo(click.style('Project created successfully.', fg='green'))


@loadlamb.command()
@click.option('--name', prompt=True)
@click.option('--description', prompt=True)
def create_extension(name, description):
    create_extension_template(name, description)


@loadlamb.command()
@click.option('--region')
@click.option('--filename')
@click.option('--profile_name')
def execute(region='us-east-1', filename='loadlamb.yaml', profile_name='default'):
    execute_loadlamb(region, filename, profile_name)


@loadlamb.command()
@click.option('--filename')
@click.option('--profile_name')
def deploy(filename='loadlamb.yaml', profile_name='default'):
    c = read_config_file(filename)
    d = Deploy(c, profile_name=profile_name)
    d.publish()


@loadlamb.command()
def create_unit_test_table():
    Run().create_table()


@loadlamb.command()
@click.option('--filename')
@click.option('--profile_name')
def undeploy(filename='loadlamb.yaml', profile_name='default'):
    c = read_config_file(filename)
    d = Deploy(c, profile_name=profile_name)
    d.unpublish()


@loadlamb.command()
def create_package():
    c = read_config_file()
    d = Deploy(c)
    d.create_package()
    d.remove_venv()


@loadlamb.command()
def create_template():
    save_sam_template()


if __name__ == '__main__':
    loadlamb()
