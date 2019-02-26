# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import (
    print_list,
    print_record
)
from .api import (
    cluster_attributes,
    list_clusters,
    create_cluster,
    delete_cluster,
    read_cluster
)


@click.group(
    'clusters',
    invoke_without_command=True,
    short_help='Manage Auger Clusters.'
)
@click.option(
    '--organization-id',
    '-o',
    default=None,
    help='Organization of the clusters.'
)
@click.pass_context
def clusters_group(ctx, organization_id):
    if ctx.invoked_subcommand is None:
        with ctx.obj.coreapi_action():
            print_list(list_clusters(ctx.obj, organization_id), cluster_attributes)


@click.command(short_help='Create a new cluster.')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the cluster will use.'
)
@click.option(
    '--project-id',
    '-p',
    required=True,
    help='Project the cluster will deploy.'
)
@click.option(
    '--worker-count',
    '-c',
    default=2,
    help='Number of worker nodes to create.'
)
@click.option(
    '--instance-type',
    '-i',
    default='c5.large',
    help='Instance type for the worker nodes.'
)
@click.option(
    '--kubernetes-stack',
    '-k',
    default='stable',
    help='Kubernetes stack name for the cluster.'
)
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to run.'
)
@pass_client
def create(ctx, organization_id, project_id, worker_count,
           instance_type, kubernetes_stack, wait):
    result = create_cluster(
        ctx, organization_id, project_id,
        worker_count, instance_type, kubernetes_stack, wait
    )
    if result is not None and not result.ok:
        raise click.ClickException('Failed to create cluster.')


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
    print_record(read_cluster(ctx, cluster_id), cluster_attributes)


clusters_group.add_command(create)
clusters_group.add_command(delete)
clusters_group.add_command(show)
