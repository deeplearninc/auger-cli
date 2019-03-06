# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import print_list, print_record

from .api import (
    pipeline_attributes,
    list_pipelines,
    read_pipeline
)


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
        print_list(
            list_data=list_pipelines(ctx.obj, organization_id, experiment_id, active),
            attributes=pipeline_attributes
        )
    else:
        pass


@click.command(short_help='Display pipeline details.')
@click.argument('pipeline_id')
@pass_client
def show(ctx, pipeline_id):
    print_record(read_pipeline(ctx, pipeline_id), pipeline_attributes)

pipelines_group.add_command(show)
