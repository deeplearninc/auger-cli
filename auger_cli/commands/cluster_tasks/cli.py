# -*- coding: utf-8 -*-

import click

from ...formatter import (
    print_list,
    print_record
)
from ...client import pass_client

from .api import (
    cluster_task_attributes,
    list_cluster_tasks,
    create_cluster_task
)


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
        with ctx.obj.coreapi_action():
            print_list(
                list_cluster_tasks(ctx.obj, project_id),
                cluster_task_attributes
            )


@click.command(short_help='Display cluster task details.')
@click.argument('cluster_task_id')
@pass_client
def show(ctx, cluster_task_id):
    with ctx.coreapi_action():
        cluster_data = ctx.client.action(
            ctx.document,
            ['cluster_tasks', 'read'],
            params={
                'id': cluster_task_id
            }
        )
        print(cluster_data['data'])

        print_record(cluster_data['data'], cluster_task_attributes)


@click.command(short_help='Create a new cluster task.')
@click.argument('project_id')
@click.argument('name')
@click.argument('args')
@pass_client
def create(ctx, project_id, name, args):
    with ctx.coreapi_action():
        result = create_cluster_task(ctx, project_id, name, args)
        if result is not None and not result.ok:
            raise click.ClickException('Failed to create cluster task.')


cluster_tasks_group.add_command(create)
cluster_tasks_group.add_command(show)
