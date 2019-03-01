# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_list,
    print_record,
    print_table,
    print_line,
    print_header
)

from .api import (
    experiment_attributes,
    create_experiment,
    delete_experiment,
    list_experiments,
    update_experiment,
    run_experiment,
    read_experiment_byid,
    monitor_leaderboard_experiment,
    read_leaderboard_experiment,
    export_model_experiment,
    stop_experiment
)


@click.group(
    'experiments',
    invoke_without_command=True,
    short_help='Manage Auger project experiments.'
)
@click.option(
    '--project-id',
    '-p',
    default='',
    help='Experiments project ID.'
)
@click.option(
    '--name',
    '-n',
    default='',
    help='Experiment name.'
)
@click.pass_context
def experiments_group(ctx, project_id, name):
    if ctx.invoked_subcommand is None:
        # request_list requires some limit and we use one big enough
        print_list(
            list_data=list_experiments(ctx.obj, project_id, name),
            attributes=experiment_attributes
        )
    else:
        pass


@click.command()
@click.argument('name')
@click.argument('project_id')
@click.argument('data_path')
@pass_client
def create(ctx, name, project_id):
    print_record(create_experiment(ctx, name, project_id, data_path), experiment_attributes)


@click.command(short_help='Display experiment details.')
@click.argument('experiment_id')
@pass_client
def show(ctx, experiment_id):
    print_record(read_experiment_byid(ctx, experiment_id), experiment_attributes)


@click.command()
@click.argument('experiment_id', required=True)
@pass_client
def delete(ctx, experiment_id):
    delete_experiment(ctx, experiment_id)


@click.command()
@click.argument('experiment_id', required=True)
@click.argument('name', required=True)
@pass_client
def update(ctx, experiment_id, name):
    update_experiment(ctx, experiment_id, name)


@click.command()
@pass_client
def run(ctx):
    run_experiment(ctx)


@click.command()
@pass_client
def stop(ctx):
    stop_experiment(ctx)


@click.command()
@pass_client
def leaderboard(ctx):
    leaderboard, info = read_leaderboard_experiment(ctx)
    print_line("=======================================")
    print_header(info)
    print_table(leaderboard)


@click.command()
@click.argument('name', required=True)
@pass_client
def monitor_leaderboard(ctx, name):
    monitor_leaderboard_experiment(ctx, name)


@click.command()
@click.option(
    '--trial-id',
    '-t',
    default=None,
    help='Trial ID to export model for the last experiment session, if missed best trial used.'
)
@pass_client
def export_model(ctx, trial_id):
    export_model_experiment(ctx, trial_id)

experiments_group.add_command(create)
experiments_group.add_command(show)
experiments_group.add_command(delete)
experiments_group.add_command(update)
experiments_group.add_command(run)
experiments_group.add_command(stop)
experiments_group.add_command(leaderboard)
experiments_group.add_command(export_model)
experiments_group.add_command(monitor_leaderboard)
