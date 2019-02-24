# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_list,
    print_record
)

from .api import (
    experiment_attributes,
    create_experiment,
    delete_experiment,
    list_experiments,
    update_experiment
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
@click.pass_context
def experiments_group(ctx, project_id):
    if ctx.invoked_subcommand is None:
        # request_list requires some limit and we use one big enough
        print_list(
            list_data=list_experiments(ctx, project_id),
            attributes=experiment_attributes
        )
    else:
        pass


@click.command()
@click.argument('name')
@click.argument('project_id')
@pass_client
def create(ctx, name, project_id):
    create_experiment(ctx, name, project_id)


@click.command(short_help='Display experiment details.')
@click.argument('experiment_id')
@pass_client
def show(ctx, experiment_id):
    with ctx.coreapi_action():
        experiment_data = ctx.client.action(
            ctx.document,
            ['experiments', 'read'],
            params={
                'id': experiment_id
            }
        )
        print(experiment_data['data'])

        print_record(experiment_data['data'], experiment_attributes)


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


experiments_group.add_command(create)
experiments_group.add_command(show)
experiments_group.add_command(delete)
experiments_group.add_command(update)
