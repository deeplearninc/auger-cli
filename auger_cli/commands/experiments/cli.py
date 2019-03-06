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
    read_experiment_info,
    read_experiment_byid,
    monitor_leaderboard_experiment,
    read_leaderboard_experiment,
    export_model_experiment,
    stop_experiment,
    predict_experiment
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
@click.option(
    '--experiment-id',
    '-e',
    default=None,
    help='Experiment ID.'
)
@pass_client
def show(ctx, experiment_id):
    print_record(read_experiment_info(ctx, experiment_id), experiment_attributes)


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
@click.option(
    '--experiment-session-id',
    '-e',
    default=None,
    help='Experiment session ID.'
)
@pass_client
def leaderboard(ctx, experiment_session_id):
    leaderboard, info = read_leaderboard_experiment(ctx, experiment_session_id)
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

@click.command()
@click.option(
    '--trial-id',
    '-t',
    default=None,
    help='Trial ID to deploy model for the last experiment session, if missed best trial used.'
)
@pass_client
def deploy_model(ctx, trial_id):
    export_model_experiment(ctx, trial_id, deploy=True)

@click.command()
@click.option(
    '--pipeline-id',
    '-p',
    default=None,
    help='Pipeline ID to call predict.'
)
@click.option(
    '--trial-id',
    '-t',
    default=None,
    help='Trial ID to predict model for the last experiment session, if missed best trial used.'
)
@click.option(
    '--file',
    '-f',
    type=click.STRING,
    help='CSV file with data to call predict.',
    required=True
)
@pass_client
def predict(ctx, pipeline_id, trial_id, file):
    predict_experiment(ctx, pipeline_id, trial_id, file)

experiments_group.add_command(create)
experiments_group.add_command(show)
experiments_group.add_command(delete)
experiments_group.add_command(update)
experiments_group.add_command(run)
experiments_group.add_command(stop)
experiments_group.add_command(leaderboard)
experiments_group.add_command(export_model)
experiments_group.add_command(deploy_model)
experiments_group.add_command(predict)
#experiments_group.add_command(monitor_leaderboard)
