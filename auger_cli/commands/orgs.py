# -*- coding: utf-8 -*-

import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import print_list, print_record
from auger_cli.api import orgs


@click.group(
    'orgs',
    invoke_without_command=True,
    short_help='Manage Auger Organizations.'
)
@click.pass_context
def orgs_group(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():
            print_list(
                list_data=orgs.list(ctx.obj),
                attributes=orgs.display_attributes
            )
    else:
        pass


@click.command(short_help='Display organization details.')
@click.option(
    '--org-name',
    '-n',
    type=click.STRING,
    default=None,
    help='Name of the organization to display.'
)
@click.option(
    '--org-id',
    '-i',
    type=click.STRING,
    default=None,
    help='ID of the organization to display.'
)
@pass_client
def show(client, org_name, org_id):
    with client.cli_error_handler():
        print_record(orgs.read(client, org_name=org_name, org_id=org_id), orgs.display_attributes)

orgs_group.add_command(show)
