# -*- coding: utf-8 -*-

from auger_cli.cli import camelize, pass_client
import click


@click.group(
    'apps',
    invoke_without_command=True,
    short_help='Manage Auger Apps.'
)
@click.option(
    'cluster_id',
    '-c',
    type=click.INT
)
@click.pass_context
def cli(ctx, cluster_id):
    if ctx.invoked_subcommand is None and cluster_id is not None:
        apps = ctx.obj.client.action(
            ctx.obj.document,
            ['apps', 'list'],
            params={
                'cluster_id': cluster_id
            }
        )
        for app in iter(apps['data']):
            _print_app(app)
    else:
        pass


@click.command(short_help='Attach an app to a cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the application to create.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the app will be deployed to.'
)
@pass_client
def create(ctx, app, cluster_id):
    result = ctx.client.action(
        ctx.document,
        ['apps', 'create'],
        params={
            'id': app,
            'cluster_id': cluster_id
        }
    )
    _print_app(result['data'])


@click.command(short_help='Remove an app from the cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the application to delete.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the app will be deployed to.'
)
@pass_client
def delete(ctx, app, cluster_id):
    ctx.client.action(
        ctx.document,
        ['apps', 'delete'],
        params={
            'id': app,
            'cluster_id': cluster_id
        }
    )
    click.echo('Deleted {}.'.format(app))


@click.command(short_help='Display app details.')
@click.argument('id')
@pass_client
def show(ctx, id):
    app = ctx.client.action(
        ctx.document,
        ['apps', 'read'],
        params={
            'id': id
        }
    )
    _print_app(app['data'])


def _print_app(app_dict):
    attributes = [
        'id',
        'url',
        'created_at'
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                camelize(attrib),
                app_dict[attrib],
                width=width
            )
        )
    click.echo()


cli.add_command(create)
cli.add_command(delete)
cli.add_command(show)
