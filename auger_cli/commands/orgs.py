# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
import auger_cli.constants as constants
import click


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
        for org in iter(orgs['data']):
            _print_org(org)
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
        [constants.CMD_ALIASES['orgs'], 'create'],
        params={
            'name': name,
            'access_key': access_key,
            'secret_key': secret_key
        }
    )
    _print_org(org['data'])


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


def _print_org(org_dict):
    def format_name(name): return name or 'pending'

    click.echo(
        "{0: >4}. {1: <12} ({2})".format(
            org_dict['id'],
            org_dict['name'],
            format_name(org_dict['s3_bucket_name'])
        )
    )


cli.add_command(create)
cli.add_command(delete)
