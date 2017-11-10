# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
from auger_cli.utils import print_formatted_list, print_formatted_object, cluster_command_progress_bar
import click
import sys
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
    'ip_address',
    'registry'
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
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to run.'
)
@pass_client
def create(ctx, name, organization_id, worker_count, instance_type, wait):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'create'],
        params={
            'name': name,
            'organization_id': organization_id,
            'worker_nodes_count': worker_count,
            'instance_type': instance_type
        }
    )['data']
    print_formatted_object(cluster, attributes)
    if wait:
        ok = cluster_command_progress_bar(
            ctx,
            cluster['id'],
            cluster['status'],
            ['waiting', 'provisioning', 'bootstrapping'],
            'running'
        )
        sys.exit(0 if ok else 1)


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
@click.option(
    '--wait/--no-wait',
    '-w/',
    default=False,
    help='Wait for cluster to be terminated.'
)
@pass_client
def delete(ctx, cluster_id, wait):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'delete'],
        params={
            'id': cluster_id
        }
    )['data']
    cluster_id = cluster['id']
    if cluster_id == int(cluster_id):
        click.echo("Deleting {}.".format(cluster['name']))
        if wait:
            ok = cluster_command_progress_bar(
                ctx,
                cluster['id'],
                cluster['status'],
                ['running', 'terminating'],
                'terminated'
            )
            sys.exit(0 if ok else 1)


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
    print_formatted_object(cluster['data'], attributes)


cli.add_command(create)
cli.add_command(dashboard)
cli.add_command(delete)
cli.add_command(show)
