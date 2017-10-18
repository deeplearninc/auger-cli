# -*- coding: utf-8 -*-

import click


@click.command(
    'init',
    short_help='Setup Auger on this machine.'
)
@click.pass_context
def cli(ctx):
    pass
