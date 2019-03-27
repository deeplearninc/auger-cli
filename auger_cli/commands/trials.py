# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import (
    print_list,
    print_record
)
from auger_cli.api import trials


@click.group(
    'trials',
    invoke_without_command=True,
    short_help='Manage Auger experiment session trials.'
)
@click.option(
    '--experiment-session-id',
    '-e',
    default='',
    help='Experiment session ID.'
)
@click.pass_context
def trials_group(ctx, experiment_session_id):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():        
            print_list(trials.list(ctx.obj, experiment_session_id), trials.display_attributes)
    else:
        pass


@click.command(short_help='Display experiment session trial details.')
@click.argument('trial_id')
@click.option(
    '--experiment-session-id',
    '-e',
    default=None,
    help='Experiment session ID.'
)
@pass_client
def show(client, trial_id, experiment_session_id):
    print_record(trials.read(client, trial_id, experiment_session_id), trials.display_attributes, max_level=0)


trials_group.add_command(show)
