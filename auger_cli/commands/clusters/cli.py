# -*- coding: utf-8 -*-

import click

from ...cli_client import pass_client
from ...formatter import (
    print_list,
    print_record
)
from .api import (
    cluster_attributes,
    list_clusters,
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
        with ctx.obj.cli_error_handler():
            print_list(list_clusters(ctx.obj, organization_id), cluster_attributes)


@click.command(short_help='Terminate a cluster.')
@click.argument('cluster_id')
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to be terminated.'
)
@pass_client
def delete(client, cluster_id, wait):
    with client.cli_error_handler():
        ok = delete_cluster(client, cluster_id, wait)
        if not ok:
            client.print_line('Failed to delete cluster.', err=True)


@click.command(short_help='Display cluster details.')
@click.argument('cluster_id')
@pass_client
def show(client, cluster_id):
    with client.cli_error_handler():    
        print_record(read_cluster(client, cluster_id), cluster_attributes)


clusters_group.add_command(delete)
clusters_group.add_command(show)
