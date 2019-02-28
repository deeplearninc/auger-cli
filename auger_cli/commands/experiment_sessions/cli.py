# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_list,
    print_record
)

from .api import (
    experiment_session_attributes,
    list_experiment_sessions,
    read_experiment_session
)


@click.group(
    'experiment_sessions',
    invoke_without_command=True,
    short_help='Manage Auger project experiment sessions.'
)
@click.option(
    '--project-id',
    '-p',
    default='',
    help='Experiment sessions project ID.'
)
@click.option(
    '--experiment-id',
    '-e',
    default='',
    help='Experiment sessions experiment ID.'
)
@click.pass_context
def experiment_sessions_group(ctx, project_id, experiment_id):
    if ctx.invoked_subcommand is None:
        # request_list requires some limit and we use one big enough
        print_list(
            list_data=list_experiment_sessions(ctx.obj, project_id, experiment_id),
            attributes=experiment_session_attributes
        )
    else:
        pass


@click.command(short_help='Display experiment session details.')
@click.argument('experiment_session_id')
@pass_client
def show(ctx, experiment_session_id):
    print_record(read_experiment_session(ctx, experiment_session_id), experiment_session_attributes)


experiment_sessions_group.add_command(show)
