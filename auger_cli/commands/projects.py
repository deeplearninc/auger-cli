# -*- coding: utf-8 -*-

from ..cli import pass_client
from ..formatter import (
    print_line,
    print_list,
    print_stream
)
from .lib.lib import (
    projects_attributes,
    projects_list,
    projects_create,
    projects_delete,
    projects_deploy,
    projects_open
)

import click
import sys


attributes = projects_attributes


@click.group(
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        print_list(
            list_data=projects_list(ctx.obj)['data'],
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
    projects_create(ctx, project, organization_id)


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
    projects_delete(ctx, project)


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
    ok = projects_deploy(ctx, project, cluster_id, wait)
    if ok is not None:
        sys.exit(0 if ok else 1)


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
    projects_open(ctx, project)


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
