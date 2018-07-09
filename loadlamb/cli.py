import os

import click

from loadlamb.utils import create_config_file, read_config_file, Deploy, create_extension_template, execute_loadlamb, \
    save_sam_template


@click.group()
def loadlamb():
    pass


def check_for_project_config_project(ctx,param,value):
    if os.path.isfile('loadlamb.yaml'):
        click.echo(click.style('There is already loadlamb.yaml in your '
                               'current directory. Please run this command again after '
                               'switching to a directory without a loadlamb.yaml', fg='red'))
        ctx.abort()
    return value


@loadlamb.command()
@click.option('--name',prompt=True,callback=check_for_project_config_project)
@click.option('--url',prompt=True)
@click.option('--user_num',prompt=True)
@click.option('--user_batch_size',prompt=True,help='Max value: 10')
@click.option('--bucket',prompt=True)
def create_project(name,url,user_num,user_batch_size,bucket):
    create_config_file({
        'name':name,
        'url':url,
        'user_num':int(user_num),
        'user_batch_size':int(user_batch_size),
        'bucket':bucket,
        'tasks':[
            {'path':'/','method_type':'GET'}
        ]
    })


@loadlamb.command()
@click.option('--name',prompt=True)
@click.option('--description',prompt=True)
def create_extension(name,description):
    create_extension_template(name,description)


@loadlamb.command()
@click.option('--delay',
    help='Delays the load test from starting by the specified number of seconds.')
def execute(delay):
    execute_loadlamb(delay)


@loadlamb.command()
def deploy():
    c = read_config_file()
    d = Deploy(c)
    d.publish()


@loadlamb.command()
def undeploy():
    c = read_config_file()
    d = Deploy(c)
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