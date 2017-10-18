# -*- coding: utf-8 -*-

import click
from auger_cli.utils import print_formatted_list


attributes = ['id', 'description']


@click.command(
    'instance-types',
    short_help='Display available instance types for clusters.'
)
@click.pass_context
def cli(ctx):
    result = ctx.obj.client.action(
        ctx.obj.document,
        ['instance_types', 'list']
    )
    print_formatted_list(result['data'], attributes)
