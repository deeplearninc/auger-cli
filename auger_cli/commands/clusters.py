# -*- coding: utf-8 -*-

from ..cli import pass_client
from ..cluster_config import ClusterConfig
from ..formatter import (
    command_progress_bar,
    print_line,
    print_list,
    print_record
)
from .lib.lib import clusters_attributes, clusters_create

import click
import sys


attributes = clusters_attributes


@click.group(
    'clusters',
    invoke_without_command=True,
    short_help='Manage Auger Clusters.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.coreapi_action():
            clusters = ctx.obj.client.action(
                ctx.obj.document,
                ['clusters', 'list']
            )
            print_list(clusters['data'], attributes)
    else:
        pass


@click.command(short_help='Create a new cluster.')
@click.argument('name')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the cluster will use.'
)
@click.option(
    '--worker-count',
    '-c',
    default=1,
    help='Number of worker nodes to create.'
)
@click.option(
    '--instance-type',
    '-i',
    default='t2.medium',
    help='Instance type for the worker nodes.'
)
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to run.'
)
@pass_client
def create(ctx, name, organization_id, worker_count, instance_type, wait):
    result = clusters_create(ctx, name, organization_id, worker_count, instance_type, wait)
    if result is not None:
        sys.exit(0 if result.ok else 1)


@click.command(short_help='Print cluster registry credentials.')
@click.argument('cluster_id')
@pass_client
def credentials(ctx, cluster_id):
    with ctx.coreapi_action():
        cluster = ClusterConfig.fetch(ctx, cluster_id)
        print_record(
            cluster['registry'],
            ['url', 'login', 'password']
        )


@click.command(short_help='Open cluster dashboard in a browser.')
@click.argument('cluster_id')
@click.option(
    '--dashboard-name',
    '-d',
    type=click.Choice(
        ['kubernetes', 'grafana', 'spark_ui']
    ),
    default='kubernetes',
    help='Name of dashboard to open.'
)
@pass_client
def dashboard(ctx, cluster_id, dashboard_name):
    with ctx.coreapi_action():
        cluster = ClusterConfig.fetch(ctx, cluster_id)
        dashboard_url = cluster['{}_url'.format(dashboard_name)]
        click.launch(dashboard_url)


@click.command(short_help='Terminate a cluster.')
@click.argument('cluster_id')
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to be terminated.'
)
@pass_client
def delete(ctx, cluster_id, wait):
    with ctx.coreapi_action():
        cluster = ctx.client.action(
            ctx.document,
            ['clusters', 'delete'],
            params={
                'id': cluster_id
            }
        )['data']
        if cluster['id'] == int(cluster_id):
            print_line("Deleting {}.".format(cluster['name']))
            if wait:
                ok = command_progress_bar(
                    ctx=ctx,
                    endpoint=['clusters', 'read'],
                    params={'id': cluster['id']},
                    first_status=cluster['status'],
                    progress_statuses=[
                        'running', 'terminating'
                    ],
                    desired_status='terminated'
                )
                sys.exit(0 if ok else 1)


@click.command(short_help='Display cluster details.')
@click.argument('cluster_id')
@pass_client
def show(ctx, cluster_id):
    with ctx.coreapi_action():
        cluster = ClusterConfig.fetch(ctx, cluster_id)
        print_record(cluster, attributes)


cli.add_command(create)
cli.add_command(credentials)
cli.add_command(dashboard)
cli.add_command(delete)
cli.add_command(show)
