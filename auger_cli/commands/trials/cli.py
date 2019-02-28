# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_list,
    print_record
)

from .api import (
    trial_attributes,
    list_trials,
    read_trial
)


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
        # request_list requires some limit and we use one big enough
        print_list(
            list_data=list_trials(ctx.obj, experiment_session_id),
            attributes=trial_attributes
        )
    else:
        pass


@click.command(short_help='Display experiment session trial details.')
@click.argument('trial_id')
@click.argument('experiment_session_id')
@pass_client
def show(ctx, trial_id, experiment_session_id):
    print_record(read_trial(ctx, trial_id, experiment_session_id), trial_attributes)


trials_group.add_command(show)
