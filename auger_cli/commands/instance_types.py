# -*- coding: utf-8 -*-

import click

from auger_cli.formatter import print_list
from auger_cli.api import instance_types


@click.command(
    'instance-types',
    short_help='Display available instance types for clusters.'
)
@click.pass_context
def instance_types_group(ctx):
    with ctx.obj.cli_error_handler():
        print_list(
            instance_types.list(ctx.obj),
            instance_types.display_attributes
        )
