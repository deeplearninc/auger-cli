# -*- coding: utf-8 -*-

import click

from ...client import pass_client
from ...formatter import print_list

from .api import (
    org_attributes,
    create_org,
    delete_org,
    list_orgs,
    update_org,
    read_org
)


@click.group(
    'orgs',
    invoke_without_command=True,
    short_help='Manage Auger Organizations.'
)
@click.pass_context
def orgs_group(ctx):
    if ctx.invoked_subcommand is None:
        print_list(
            list_data=list_orgs(ctx.obj),
            attributes=org_attributes
        )
    else:
        pass


@click.command()
@click.argument('name')
@click.option('--access-key', help='AWS public access key.')
@click.option('--secret-key', help='AWS secret key.')
@pass_client
def create(ctx, name, access_key, secret_key):
    create_org(ctx, name, access_key, secret_key)


@click.command()
@click.argument('organization_id', required=True)
@pass_client
def delete(ctx, organization_id):
    delete_org(ctx, organization_id)


@click.command()
@click.argument('organization_id', required=True)
@click.option('--access-key', required=True, help='AWS public access key.')
@click.option('--secret-key', required=True, help='AWS secret key.')
@pass_client
def update(ctx, organization_id, access_key, secret_key):
    update_org(ctx, access_key, secret_key, organization_id)


@click.command(short_help='Display organization details.')
@click.option(
    '--organization',
    '-o',
    type=click.STRING,
    required=True,
    help='Name of the organization to display.'
)
@pass_client
def show(ctx, org):
    print_record(read_org(ctx, org), org_attributes)

orgs_group.add_command(create)
orgs_group.add_command(delete)
orgs_group.add_command(update)
orgs_group.add_command(show)
