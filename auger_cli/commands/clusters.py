# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
from auger_cli.cluster_config import ClusterConfig
from auger_cli.utils import print_formatted_list, print_formatted_object
import click
import webbrowser


attributes = [
    'name',
    'id',
    'organization_id',
    'status',
    'seconds_since_created',
    'uptime_seconds',
    'worker_nodes_count',
    'instance_type',
    'ip_address'
]


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
            print_formatted_list(clusters['data'], attributes)
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
    with ctx.coreapi_action():
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
        cluster_dict = cluster['data']
        ClusterConfig(cluster_dict=cluster_dict).save()
        print_formatted_object(cluster_dict, attributes)


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
        webbrowser.open_new_tab(dashboard_url)


@click.command(short_help='Terminate a cluster.')
@click.argument('cluster_id')
@pass_client
def delete(ctx, cluster_id):
    with ctx.coreapi_action():
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
    with ctx.coreapi_action():
        cluster = ClusterConfig.fetch(ctx, cluster_id)
        print_formatted_object(cluster, attributes)


cli.add_command(create)
cli.add_command(dashboard)
cli.add_command(delete)
cli.add_command(show)
