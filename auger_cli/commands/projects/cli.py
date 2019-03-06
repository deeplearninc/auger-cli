# -*- coding: utf-8 -*-

import click

from ...auger_config import AugerConfig
from ...client import pass_client
from ...formatter import (
    print_line,
    print_list,
    print_stream,
    print_record
)
from .api import (
    project_attributes,
    list_projects,
    create_project,
    delete_project,
    launch_project_url,
    read_project,
    download_project_file
)


@click.group(
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def projects_group(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.coreapi_action():
            print_list(list_projects(ctx.obj), project_attributes)


@click.command(short_help='Create a new Auger project.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to create.'
)
@click.option(
    '--organization-id',
    '-o',
    type=click.INT,
    required=True,
    help='Organization for the project.'
)
@pass_client
def create(ctx, project, organization_id):
    create_project(ctx, project, organization_id)


@click.command(
    short_help='Delete an project from Auger Hub. This cannot be undone.'
)
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to delete.'
)
@pass_client
def delete(ctx, project):
    delete_project(ctx, project)


@click.command(
    short_help='Download file from project. Path should be relative project path. For example: files/iris_data_sample.csv'
)
@click.argument('remote_path', required=True)
@click.option(
    '--local-path',
    '-l',
    type=click.STRING,
    required=False,
    default="files",
    help='Name of the project to delete.'
)
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=False,
    default=None,
    help='Name of the project to delete.'
)
@pass_client
def download_file(ctx, remote_path, local_path, project):
    if project is None:
        config = AugerConfig()
        project_id = config.get_project_id()
    else:
        project_id = read_project(ctx, project).get('id')

    download_project_file(ctx, project_id, remote_path, local_path)


@click.command(short_help='Display project logs.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=False,
    default=None,
    help='Name of the project to delete.'
)
@click.option(
    '--tail',
    '-t',
    type=click.BOOL,
    is_flag=True,
    help='Stream logs to console.'
)
@pass_client
def logs(ctx, project, tail):
    if project is None:
        config = AugerConfig()
        project_id = config.get_project_id()
    else:
        project_id = read_project(ctx, project).get('id')
    
    if tail:
        params = {
            'id': project_id
        }
        print_stream(ctx, params)
    else:
        result = ctx.client.action(
            ctx.document,
            ['projects', 'logs'],
            params={
                'id': project_id
            }
        )
        print_line(result)


@click.command(short_help='Open project in a browser.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    help='Name of project to open.'
)
@pass_client
def open_project(ctx, project):
    launch_project_url(ctx, project)


@click.command(short_help='Display project details.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to display.'
)
@pass_client
def show(ctx, project):
    print_record(read_project(ctx, project), project_attributes)

projects_group.add_command(create)
projects_group.add_command(delete)
projects_group.add_command(logs)
projects_group.add_command(open_project, name='open')
projects_group.add_command(show)
projects_group.add_command(download_file)

