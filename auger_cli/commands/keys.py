# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
from auger_cli.utils import camelize
import click


@click.group(
    'keys',
    invoke_without_command=True,
    short_help='Manage Auger SSH keys.'
)
@click.option(
    'organization_id',
    '-o',
    type=click.INT,
    help='Display keys for a given organization.'
)
@click.pass_context
def cli(ctx, organization_id):
    if ctx.invoked_subcommand is None and organization_id is not None:
        keys = ctx.obj.client.action(
            ctx.obj.document,
            ['ssh_keys', 'list'],
            params={
                'organization_id': organization_id
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
    '--organization-id',
    '-o',
    type=click.INT,
    required=True,
    help='Organization the key will be installed to.'
)
@pass_client
def add(ctx, public_key, organization_id):
    try:
        with open(public_key) as f:
            key_content = f.read()
            result = ctx.client.action(
                ctx.document,
                ['ssh_keys', 'create'],
                params={
                    'public_key': key_content,
                    'organization_id': organization_id
                }
            )
            _print_key(result['data'])
    except IOError:
        click.echo('Error loading public key {}'.format(public_key))


@click.command(short_help='Delete an SSH key from a cluster.')
@click.argument('key_id')
@click.option(
    '--organization-id',
    '-o',
    type=click.INT,
    required=True,
    help='Organization the key will be deleted from.'
)
@pass_client
def delete(ctx, key_id, organization_id):
    ctx.client.action(
        ctx.document,
        ['ssh_keys', 'delete'],
        params={
            'id': key_id,
            'organization_id': organization_id
        }
    )
    click.echo("Deleted SSH key.")


def _print_key(key_dict):
    attributes = [
        'id',
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
cli.add_command(delete)
