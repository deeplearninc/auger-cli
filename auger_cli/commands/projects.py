# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import (
    print_line,
    print_list,
    print_stream,
    print_record,
    print_plain_list,
    print_table
)
from auger_cli.api import projects


@click.group(
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def projects_group(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():
            print_list(projects.list(ctx.obj), projects.display_attributes)


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
def create(client, project, organization_id):
    with client.cli_error_handler():
        project = projects.create(client, project, organization_id)
        print_record(project, projects.display_attributes)

@click.command(
    short_help='Delete an project from Auger Hub. This cannot be undone.'
)
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    default=None,
    help='Name of the project to delete.'
)
@click.option(
    '--project-id',
    '-i',
    type=click.STRING,
    default=None,
    help='ID of the project to delete.'
)
@pass_client
def delete(client, project, project_id):
    with client.cli_error_handler():
        if project_id is None:
            project_id = projects.read(client, project_name=project).get('id')

        projects.delete(client, project_id)
        print_line('Projects {} deleted.'.format(project_id))

@click.command( "download_file",
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
def download_file(client, remote_path, local_path, project):
    with client.cli_error_handler():
        project_id = None
        if project:
            project_id = read_project(client, project).get('id')

        file_path = projects.download_file(client, project_id, remote_path, local_path)
        print_line('Downloaded file: {}'.format(file_path))


@click.command( "list_files",
    short_help='Download file from project. Path should be relative project path. For example: files/iris_data_sample.csv'
)
@click.option(
    '--remote-path',
    '-r',
    type=click.STRING,
    default=None,
    help='Folder path to list files.'
)
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    default=None,
    help='Name of the project to delete.'
)
@pass_client
def list_files(client, remote_path, project):
    with client.cli_error_handler():
        project_id = None
        if project:
            project_id = read_project(client, project).get('id')

        print_plain_list(projects.list_files(client, project_id, remote_path))


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
def logs(client, project, tail):
    with client.cli_error_handler():
        if project is None:
            project_id = client.config.get_project_id()
        else:
            project_id = projects.read(client, project).get('id')

        if tail:
            print_stream(client, {'id': project_id})
        else:
            result = client.call_hub_api_ex('get_project_logs', params={'id': project_id})
            print_line(result)


@click.command("open_project", short_help='Open project in a browser.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    default=None,
    help='Name of project to open.'
)
@pass_client
def open_project(client, project):
    from auger_cli.utils import urlparse
    with client.cli_error_handler():
        project_name = project
        if project is None:
            project = projects.get_or_create(client, create_if_not_exist=True)
            project_name = project.get('name')

        parsed_url = urlparse(client.config.get_api_url())
        url = "{}://{}/auger/projects/{}".format(parsed_url.scheme, parsed_url.netloc, project_name)
        print("Open url in default browser: %s"%url)

        click.launch(url)


@click.command(short_help='Display project details.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to display.'
)
@pass_client
def show(client, project):
    with client.cli_error_handler():
        print_record(projects.read(client, project), projects.display_attributes)

@click.command(short_help='Display running projects details.')
@pass_client
def leaderboard(client):
    with client.cli_error_handler():
        print_table(projects.read_leaderboard(client))

projects_group.add_command(create)
projects_group.add_command(delete)
projects_group.add_command(logs)
projects_group.add_command(open_project, name='open')
projects_group.add_command(show)
projects_group.add_command(download_file)
projects_group.add_command(list_files)
projects_group.add_command(leaderboard)

