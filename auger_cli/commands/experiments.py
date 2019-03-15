# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import (
    print_list,
    print_record,
    print_table,
    print_line,
    print_header
)

from auger_cli.api import experiments


@click.group(
    'experiments',
    invoke_without_command=True,
    short_help='Manage Auger project experiments.'
)
@click.option(
    '--project-id',
    '-p',
    default=None,
    help='Experiments project ID.'
)
@click.option(
    '--name',
    '-n',
    default=None,
    help='Experiment name.'
)
@click.pass_context
def experiments_group(ctx, project_id, name):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():
            print_list(
                list_data=experiments.list(ctx.obj, project_id, name),
                attributes=experiments.display_attributes
            )
    else:
        pass


@click.command()
@click.argument('name')
@click.argument('project_id')
@click.argument('data_path')
@pass_client
def create(client, name, project_id):
    with client.cli_error_handler():
        print_record(experiments.create(cleint, name, project_id, data_path), experiments.display_attributes)


@click.command(short_help='Display experiment details.')
@click.option(
    '--experiment-id',
    '-e',
    default=None,
    help='Experiment ID.'
)
@pass_client
def show(client, experiment_id):
    with client.cli_error_handler():
        print_record(experiments.read_ex(client, experiment_id), experiments.display_attributes)


@click.command()
@click.argument('experiment_id', required=True)
@pass_client
def delete(client, experiment_id):
    with client.cli_error_handler():
        experiments.delete(client, experiment_id)


@click.command()
@click.argument('experiment_id', required=True)
@click.argument('name', required=True)
@pass_client
def update(client, experiment_id, name):
    with client.cli_error_handler():
        print_record(experiments.update(client, experiment_id, name), experiments.display_attributes)


@click.command()
@pass_client
def run(client):
    with client.cli_error_handler():
        experiments.run(client)


@click.command()
@pass_client
def stop(client):
    with client.cli_error_handler():
        experiments.stop(client)


@click.command()
@click.option(
    '--experiment-session-id',
    '-e',
    default=None,
    help='Experiment session ID.'
)
@pass_client
def leaderboard(client, experiment_session_id):
    with client.cli_error_handler():    
        leaderboard, info = experiments.read_leaderboard(client, experiment_session_id)
        print_line("=======================================")
        print_header(info)
        print_table(leaderboard)


@click.command()
@click.argument('name', required=True)
@pass_client
def monitor_leaderboard(client, name):
    experiments.monitor_leaderboard(client, name)


@click.command()
@click.option(
    '--trial-id',
    '-t',
    default=None,
    help='Trial ID to export model for the last experiment session, if missed best trial used.'
)
@pass_client
def export_model(client, trial_id):
    model_path = experiments.export_model(client, trial_id)
    client.print_line("Model exported to file: %s"%model_path)

@click.command()
@click.option(
    '--trial-id',
    '-t',
    default=None,
    help='Trial ID to deploy model for the last experiment session, if missed best trial used.'
)
@pass_client
def deploy_model(client, trial_id):
    experiments.export_model(client, trial_id, deploy=True)

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
def predict(client, pipeline_id, trial_id, file):
    predict_path = experiments.predict_by_file(client, file, pipeline_id, trial_id, save_to_file=True)
    client.print_line("Prediction result saved to file: %s"%predict_path)

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
