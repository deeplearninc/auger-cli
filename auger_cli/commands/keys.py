# -*- coding: utf-8 -*-

from auger_cli.cli import camelize, pass_client
import click


@click.group(
    'keys',
    invoke_without_command=True,
    short_help='Manage Auger cluster keys.'
)
@click.option(
    'cluster_id',
    '-c',
    type=click.INT,
    help='Display keys for a given cluster.'
)
@click.pass_context
def cli(ctx, cluster_id):
    if ctx.invoked_subcommand is None and cluster_id is not None:
        keys = ctx.obj.client.action(
            ctx.obj.document,
            ['keys', 'list'],
            params={
                'cluster_id': cluster_id
            }
        )
        for key in iter(keys['data']):
            _print_key(key)
    else:
        pass


@click.command(short_help='Add an SSH key to a cluster.')
@click.option(
    '--public-key',
    '-p',
    type=click.STRING,
    required=True,
    help='A local file path to an SSH public key used to push app code.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the key will be installed to.'
)
@pass_client
def add(ctx, public_key, cluster_id):
    try:
        with open(public_key) as f:
            key_content = f.read()
            result = ctx.client.action(
                ctx.document,
                ['keys', 'create'],
                params={
                    'public_key': key_content,
                    'cluster_id': cluster_id
                }
            )
            _print_key(result['data'])
    except IOError as e:
        print(e)
        click.echo('Error loading public key {}'.format(public_key))


def _print_key(key_dict):
    attributes = [
        'uid',
        'public_key',
        'created_at'
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                camelize(attrib),
                key_dict[attrib],
                width=width
            )
        )
    click.echo()


cli.add_command(add)
