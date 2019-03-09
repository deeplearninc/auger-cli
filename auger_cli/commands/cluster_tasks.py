# -*- coding: utf-8 -*-

import click

from auger_cli.formatter import (
    print_list,
    print_record
)
from auger_cli.cli_client import pass_client
from auger_cli.api import cluster_tasks


@click.group(
    'cluster-tasks',
    invoke_without_command=True,
    short_help='Manage Auger cluster tasks.'
)
@click.option(
    '--project-id',
    '-p',
    type=click.INT,
    required=False,
    help='Project ID for cluster tasks.'
)
@click.pass_context
def cluster_tasks_group(ctx, project_id):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():
            print_list(
                cluster_tasks.list(ctx.obj, project_id),
                cluster_tasks.display_attributes
            )


@click.command(short_help='Display cluster task details.')
@click.argument('cluster_task_id')
@pass_client
def show(client, cluster_task_id):
    with client.cli_error_handler():
        print_record(cluster_tasks.read(client, cluster_task_id),
                     cluster_tasks.display_attributes)


@click.command(short_help='Create a new cluster task.')
@click.argument('project_id')
@click.option(
    '--taskname',
    '-n',
    type=click.STRING,
    help='Cluster task name.',
    required=False
)
@click.option(
    '--taskargs',
    '-a',
    type=click.STRING,
    help="Cluster task arguments(json encoded): [{\"augerInfo\":{\"experiment_id\": null}}]",
    required=False
)
@click.option(
    '--taskfile',
    '-f',
    type=click.STRING,
    help='Python file with get_cluster_task_info method implemented.',
    required=False
)
@pass_client
def create(client, project_id, taskname, taskargs, taskfile):
    from importlib import import_module

    with client.cli_error_handler():
        if taskfile is not None:
            task_info_func = getattr(import_module(
                taskfile), 'get_cluster_task_info')
            res = task_info_func()
            result = cluster_tasks.create_ex(client, project_id, res[0], res[1])
        else:
            result = cluster_tasks.create(
                client, project_id, taskname, taskargs)

        client.print_line(result)


@click.command(short_help='Run cluster task from auger_experiment.yml.')
@click.option(
    '--wait',
    '-w',
    type=click.BOOL,
    is_flag=True,
    help='Wait till task will be completed.'
)
@pass_client
def run(client, wait):
    with client.cli_error_handler():
        cluster_tasks.run(client, wait)

cluster_tasks_group.add_command(create)
cluster_tasks_group.add_command(show)
cluster_tasks_group.add_command(run)
