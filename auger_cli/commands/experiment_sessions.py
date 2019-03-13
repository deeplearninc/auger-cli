# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import (
    print_list,
    print_record,
    print_table
)

from auger_cli.api import experiment_sessions


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
        with ctx.obj.cli_error_handler():
            print_table(
                experiment_sessions.list(ctx.obj, project_id, experiment_id),
                attributes=experiment_sessions.display_list_attributes
            )
    else:
        pass


@click.command(short_help='Display experiment session details.')
@click.argument('experiment_session_id')
@pass_client
def show(client, experiment_session_id):
    with client.cli_error_handler():
        print_record(experiment_sessions.read(client, experiment_session_id), experiment_sessions.display_attributes)


experiment_sessions_group.add_command(show)
