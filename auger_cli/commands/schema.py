# -*- coding: utf-8 -*-

from ..cli import pass_client
import click


@click.command('schema', short_help='Display current Auger schema.')
@pass_client
def cli(ctx):
    ctx.fetch_document(url=ctx.document.url)
    click.echo(ctx.document)
