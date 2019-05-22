import click

from loadlamb.chalicelib.contrib.db.models import Run
from loadlamb.chalicelib.utils import create_config_file, read_config_file, Deploy, create_extension_template, \
    execute_loadlamb, save_sam_template


@click.group()
def loadlamb():
    pass


def validate_regions(ctx, param, value):
    return value.replace(" ", "").split(',')


@loadlamb.command()
@click.option('--name', prompt=True)
@click.option('--url', prompt=True, help='Dev stage URL')
@click.option('--repo_url', prompt=True)
@click.option('--user_num', prompt=True)
@click.option('--user_batch_size', prompt=True)
@click.option('--user_batch_sleep', prompt=True)
@click.option('--regions', prompt=True, callback=validate_regions,
              help='Comma delimited list of AWS region short names. ex. us-east-1, us-east-2')
@click.option('--default_stage_name', prompt=True)
@click.option('--filename', default='loadlamb.yaml')
def create_project(name, url, repo_url, user_num, user_batch_size, user_batch_sleep, regions, default_stage_name,
                   filename='loadlamb.yaml'):
    create_config_file({
        'name': name,
        'repo_url': repo_url,
        'user_num': int(user_num),
        'user_batch_size': int(user_batch_size),
        'user_batch_sleep': int(user_batch_sleep),
        'regions': regions,
        'stages': [{'name': default_stage_name, 'url': url}],
        'tasks': [{'path': '/', 'method_type': 'GET'}]
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
@click.option('--stage')
def execute(region='us-east-1', filename='loadlamb.yaml', profile_name='default', stage='dev'):
    execute_loadlamb(region, filename, profile_name, stage)


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
