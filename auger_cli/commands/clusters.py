# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
import click


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
            _print_cluster(cluster)
    else:
        pass


@click.command()
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
            'node_instance_type': instance_type
        }
    )
    _print_cluster(cluster['data'])


@click.command()
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
        click.echo("Deleting {0}.".format(cluster['name']))


@click.command()
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
    click.echo(
        '  ID | Org   | Name         | Status       | Uptime     | Nodes | Node Type  | IP Address'
    )
    click.echo(
        "{0: >4} | {1: <5} | {2: <12} | {3: <12} | {4: <10} | {5: <5} | {6: <10} | {7: <16}".format(
            cluster_dict['id'],
            cluster_dict['organization_id'],
            cluster_dict['name'],
            cluster_dict['status'],
            cluster_dict['uptime_seconds'],
            cluster_dict['worker_nodes_count'],
            cluster_dict['node_instance_type'],
            (cluster_dict['ip_address'] or '')
        )
    )


cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
