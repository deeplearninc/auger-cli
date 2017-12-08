# -*- coding: utf-8 -*-

import click

from ..client import pass_client
from ..formatter import print_line


@click.command('schema', short_help='Display current Auger schema.')
@pass_client
def cli(ctx):
    ctx.fetch_document(url=ctx.document.url)
    print_line(ctx.document)
