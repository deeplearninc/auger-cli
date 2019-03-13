# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import print_list, print_record
from auger_cli.api import pipelines


@click.group(
    'pipelines',
    invoke_without_command=True,
    short_help='Manage Auger Pipelines.'
)
@click.option(
    '--organization-id',
    '-o',
    type=click.INT,
    required=False,
    default=None,
    help='Organization for the project.'
)
@click.option(
    '--experiment-id',
    '-e',
    default=None,
    help='Experiment ID.'
)
@click.option(
    '--active',
    '-a',
    type=click.BOOL,
    is_flag=True,
    help='Show only active pipelines.'
)
@click.pass_context
def pipelines_group(ctx, organization_id, experiment_id, active):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():        
            print_list(pipelines.list(ctx.obj, organization_id, experiment_id, active), pipelines.display_attributes)
    else:
        pass


@click.command(short_help='Display pipeline details.')
@click.argument('pipeline_id')
@pass_client
def show(client, pipeline_id):
    with client.cli_error_handler():
        print_record(pipelines.read(client, pipeline_id), pipelines.display_attributes)

pipelines_group.add_command(show)
