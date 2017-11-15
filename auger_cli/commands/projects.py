# -*- coding: utf-8 -*-

from ..cli import pass_client
from ..cluster_config import ClusterConfig
from ..formatter import (
    command_progress_bar,
    print_line,
    print_list,
    print_stream,
    print_record
)
import click
import sys


attributes = [
    'id',
    'name',
    'attached',
    'status',
    'cluster_id',
    'created_at'
]


@click.group(
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        projects = ctx.obj.client.action(
            ctx.obj.document,
            ['projects', 'list']
        )
        print_list(
            list_data=projects['data'],
            attributes=attributes
        )
    else:
        pass


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
    params = {
        'name': project,
        'organization_id': organization_id
    }
    result = ctx.client.action(
        ctx.document,
        ['projects', 'create'],
        params=params
    )
    print_record(result['data'], attributes)


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
    ctx.client.action(
        ctx.document,
        ['projects', 'delete'],
        params={'name': project}
    )
    print_line('Deleted {}.'.format(project))


@click.command(short_help='Deploy an project to a cluster.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to deploy.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the project will be deployed to.'
)
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for project to be ready.'
)
@pass_client
def deploy(ctx, project, cluster_id, wait):
    cluster_config = ClusterConfig(
        ctx,
        project=project,
        cluster_id=cluster_id
    )
    print_line('Setting up docker registry.')
    cluster_config.login()
    print_line('Preparing project to deploy.')
    cluster_config.docker_client.build()
    print_line('Deploying project. (This may take a few minutes.)')
    cluster_config.docker_client.push()
    definition = ''
    with open('.auger/service.yml') as f:
        definition = f.read()

    project_data = ctx.client.action(
        ctx.document,
        ['projects', 'deploy'],
        params={
            'name': project,
            'cluster_id': cluster_id,
            'definition': definition
        }
    )['data']
    print_record(project_data, attributes)
    if wait:
        ok = command_progress_bar(
            ctx=ctx,
            endpoint=['projects', 'read'],
            params={'name': project_data['name']},
            first_status=project_data['status'],
            progress_statuses=['undeployed'],
            desired_status='ready'
        )
        sys.exit(0 if ok else 1)
    else:
        print_line('Done.')


@click.command(short_help='Display project logs.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project.'
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
    if tail:
        params = {
            'name': project
        }
        print_stream(ctx, params)
    else:
        result = ctx.client.action(
            ctx.document,
            ['projects', 'logs'],
            params={
                'name': project
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
    project = ctx.client.action(
        ctx.document,
        ['projects', 'read'],
        params={
            'name': project
        }
    )
    project_url = project['url']
    return click.launch(project_url)


@click.command(short_help='Undeploy an project from the cluster.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to undeploy.'
)
@pass_client
def undeploy(ctx, project):
    ctx.client.action(
        ctx.document,
        ['projects', 'undeploy'],
        params={'name': project}
    )
    print_line('Undeployed {}.'.format(project))


cli.add_command(create)
cli.add_command(delete)
cli.add_command(deploy)
cli.add_command(logs)
cli.add_command(open_project, name='open')
cli.add_command(undeploy)
