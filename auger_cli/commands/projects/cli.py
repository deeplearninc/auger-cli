# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_line,
    print_list,
    print_stream
)
from .api import (
    project_attributes,
    list_projects,
    create_project,
    delete_project,
    deploy_project,
    launch_project_url
)


@click.group(
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def projects_group(ctx):
    if ctx.invoked_subcommand is None:
        print_list(
            list_data=list_projects(ctx.obj)['data'],
            attributes=project_attributes
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
    ok = deploy_project(ctx, project, cluster_id, wait)
    if ok is not None and not ok:
        raise click.ClickException('Failed to deploy project.')


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
    launch_project_url(ctx, project)


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


projects_group.add_command(create)
projects_group.add_command(delete)
projects_group.add_command(deploy)
projects_group.add_command(logs)
projects_group.add_command(open_project, name='open')
projects_group.add_command(undeploy)
