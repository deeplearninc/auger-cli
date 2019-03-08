# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import (
    print_list,
    print_record,
    print_table
)

from auger_cli.api.experiment_sessions import (
    experiment_session_attributes,
    experiment_session_list_attributes,
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
        print_table(
            list_experiment_sessions(ctx.obj, project_id, experiment_id),
            attributes=experiment_session_list_attributes
        )
    else:
        pass


@click.command(short_help='Display experiment session details.')
@click.argument('experiment_session_id')
@pass_client
def show(ctx, experiment_session_id):
    print_record(read_experiment_session(ctx, experiment_session_id), experiment_session_attributes)


experiment_sessions_group.add_command(show)
