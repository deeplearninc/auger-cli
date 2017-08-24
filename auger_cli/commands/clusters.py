# -*- coding: utf-8 -*-

from auger_cli.cli import camelize, pass_client
import click
import collections


@click.group(
    'clusters',
    invoke_without_command=True,
    short_help='Manage Auger Clusters.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        clusters = ctx.obj.client.action(
            ctx.obj.document,
            ['clusters', 'list']
        )
        for cluster in iter(clusters['data']):
            click.echo(
                "{: >4}: {} (status: {}) (uptime: {} sec) (launched: {} hours ago)".format(
                    cluster['id'],
                    cluster['name'],
                    cluster['status'],
                    cluster['uptime_seconds'],
                    cluster['seconds_since_created']//3600
                )
            )
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
@pass_client
def create(ctx, name, organization_id, worker_count, instance_type):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'create'],
        params={
            'name': name,
            'organization_id': organization_id,
            'worker_nodes_count': worker_count,
            'instance_type': instance_type
        }
    )
    _print_cluster(cluster['data'])


@click.command(short_help='Terminate a cluster.')
@click.argument('cluster_id')
@pass_client
def delete(ctx, cluster_id):
    clusters = ctx.client.action(
        ctx.document,
        ['clusters', 'delete'],
        params={
            'id': cluster_id
        }
    )
    cluster = clusters['data']
    if cluster['id'] == int(cluster_id):
        click.echo("Deleting {}.".format(cluster['name']))


@click.command(short_help='Display cluster details.')
@click.argument('cluster_id')
@pass_client
def show(ctx, cluster_id):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'read'],
        params={
            'id': cluster_id
        }
    )
    _print_cluster(cluster['data'])


def _print_cluster(cluster_dict):
    attributes = [
        'id',
        'organization_id',
        'name',
        'status',
        'uptime_seconds',
        'worker_nodes_count',
        'instance_type',
        'ip_address',
        'kubernetes_url'
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                camelize(attrib),
                _string_for_attrib(cluster_dict[attrib]),
                width=width
            )
        )


def _string_for_attrib(attrib):
    if type(attrib) in (int, str):
        return attrib
    elif type(attrib) is list:
        return attrib.join(',')
    if isinstance(attrib, collections.OrderedDict):
        return ' - '.join([v for k, v in attrib.items() if k != 'object'])
    else:
        return attrib


cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
