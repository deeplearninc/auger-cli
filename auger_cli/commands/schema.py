# -*- coding: utf-8 -*-

import click
from ..formatter import print_line


@click.command('schema', short_help='Display current Auger schema.')
@click.pass_context
def cli(ctx):
    print_line(ctx.obj.document)
