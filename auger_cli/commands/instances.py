# -*- coding: utf-8 -*-

import click

from auger_cli.formatter import print_list
from auger_cli.utils import request_list


attributes = ['id', 'description']


@click.command(
    'instance-types',
    short_help='Display available instance types for clusters.'
)
@click.pass_context
def instances_group(ctx):
    print_list(
        request_list(ctx.obj, 'instance_types', params={}),
        attributes
    )
