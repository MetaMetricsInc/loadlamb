import os

import click

from loadlamb.utils import create_config_file, read_config_file, Deploy


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
@click.option('--default_user_num',prompt=True)
@click.option('--bucket',prompt=True)
def create_project(name,url,default_user_num,bucket):
    create_config_file({
        'name':name,
        'url':url,
        'default_user_num':default_user_num,
        'bucket':bucket
    })

@loadlamb.command()
def execute():
    pass


@loadlamb.command()
def deploy():
    c = read_config_file()
    d = Deploy(c)
    d.publish()



if __name__ == '__main__':
    loadlamb()