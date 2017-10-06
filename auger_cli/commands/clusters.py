# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
from auger_cli.utils import string_for_attrib
import click
import webbrowser


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
            for cluster in iter(clusters['data']):
                click.echo('=======')
                _print_cluster(cluster)
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
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'read'],
        params={
            'id': cluster_id
        }
    )
    dashboard_url = cluster['data']['{}_url'.format(dashboard_name)]
    webbrowser.open_new_tab(dashboard_url)


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
    # for attrib in cluster['data']:
    #     print(attrib + ' ' + str(cluster['data'][attrib]))
    _print_cluster(cluster['data'])


def _print_cluster(cluster_dict):
    attributes = [
        'name',
        'id',
        'organization_id',
        'status',
        'seconds_since_created',
        'uptime_seconds',
        'worker_nodes_count',
        'instance_type',
        'ip_address',
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                attrib,
                string_for_attrib(cluster_dict[attrib]),
                width=width
            )
        )


cli.add_command(create)
cli.add_command(dashboard)
cli.add_command(delete)
cli.add_command(show)
