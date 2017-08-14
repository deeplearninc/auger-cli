# -*- coding: utf-8 -*-

import click


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
    click.echo('Available instance types:')
    for instance_type in result['data']:
        click.echo(' {}'.format(instance_type))
