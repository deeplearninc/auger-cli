# -*- coding: utf-8 -*-

import click


@click.command('logout', short_help='Logout from Auger.')
@click.pass_context
def cli(ctx):
    ctx.obj.clear()
    click.echo('You are now logged out.')
