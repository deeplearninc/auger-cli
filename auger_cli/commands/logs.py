# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
import click


@click.command('logs', short_help='Display cluster logs.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    help='Display application logs.'
)
@pass_client
def cli(ctx, app):
    pass
    # ctx.setup_logger(format='')
    # ctx.log(ctx.app_name)
