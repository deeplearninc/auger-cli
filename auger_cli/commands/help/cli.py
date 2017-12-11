# -*- coding: utf-8 -*-

import click


@click.command('help')
@click.pass_context
def help_group(ctx):
    print(ctx.parent.get_help())
