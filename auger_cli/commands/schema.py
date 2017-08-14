# -*- coding: utf-8 -*-

import click


@click.command('schema', short_help='Display current Auger schema.')
@click.pass_context
def cli(ctx):
    click.echo(ctx.obj.document)
