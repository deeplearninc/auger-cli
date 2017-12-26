# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...cluster_config import ClusterConfig
from ...formatter import (
    print_list,
    print_record
)
from .api import (
    cluster_attributes,
    list_clusters,
    create_cluster,
    delete_cluster
)


@click.group(
    'clusters',
    invoke_without_command=True,
    short_help='Manage Auger Clusters.'
)
@click.pass_context
def clusters_group(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.coreapi_action():
            print_list(list_clusters(ctx.obj), cluster_attributes)


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
    result = create_cluster(
        ctx, name, organization_id,
        worker_count, instance_type, wait
    )
    if result is not None and not result.ok:
        raise click.ClickException('Failed to create cluster.')


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
    ok = delete_cluster(ctx, cluster_id, wait)
    if ok is not None and not ok:
        raise click.ClickException('Failed to delete cluster.')


@click.command(short_help='Display cluster details.')
@click.argument('cluster_id')
@pass_client
def show(ctx, cluster_id):
    with ctx.coreapi_action():
        cluster = ClusterConfig.fetch(ctx, cluster_id)
        print_record(cluster, cluster_attributes)


clusters_group.add_command(create)
clusters_group.add_command(credentials)
clusters_group.add_command(dashboard)
clusters_group.add_command(delete)
clusters_group.add_command(show)
