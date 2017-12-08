# -*- coding: utf-8 -*-

import click

from ..client import pass_client
from ..formatter import print_line, print_list, print_record


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
        print_list(orgs['data'], attributes)
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
        ['orgs', 'create'],
        params={
            'name': name,
            'access_key': access_key,
            'secret_key': secret_key
        }
    )
    print_record(org['data'], attributes)


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
        print_line("Deleting {0}.".format(org['name']))


cli.add_command(create)
cli.add_command(delete)
