# -*- coding: utf-8 -*-

from ..cli import pass_client
from ..constants import CMD_ALIASES
from ..utils import print_formatted_list, print_formatted_object
import click


attributes = ['id', 'name', 'main_bucket', 'status']


@click.group(
    'orgs',
    invoke_without_command=True,
    short_help='Manage Auger Organizations.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        orgs = ctx.obj.client.action(
            ctx.obj.document,
            ['organizations', 'list']
        )
        print_formatted_list(orgs['data'], attributes)
    else:
        pass


@click.command()
@click.argument('name')
@click.option(
    '--access-key',
    required=True,
    help='AWS public access key.'
)
@click.option(
    '--secret-key',
    required=True,
    help='AWS secret key.'
)
@pass_client
def create(ctx, name, access_key, secret_key):
    org = ctx.client.action(
        ctx.document,
        [CMD_ALIASES['orgs'], 'create'],
        params={
            'name': name,
            'access_key': access_key,
            'secret_key': secret_key
        }
    )
    print_formatted_object(org['data'], attributes)


@click.command()
@click.argument('organization_id', required=True)
@pass_client
def delete(ctx, organization_id):
    orgs = ctx.client.action(
        ctx.document,
        ['organizations', 'delete'],
        params={
            'id': organization_id
        }
    )
    org = orgs['data']
    if org['id'] == int(organization_id):
        click.echo("Deleting {0}.".format(org['name']))


cli.add_command(create)
cli.add_command(delete)
