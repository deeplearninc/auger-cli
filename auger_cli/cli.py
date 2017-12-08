# -*- coding: utf-8 -*-

import click

from . import client

import auger_cli.commands.auth
import auger_cli.commands.clusters.cli
import auger_cli.commands.help
import auger_cli.commands.instances
import auger_cli.commands.keys
import auger_cli.commands.orgs
import auger_cli.commands.projects.cli
import auger_cli.commands.start.cli
import auger_cli.commands.stop.cli
import auger_cli.commands.schema


CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGER')
COMMANDS = {
    'auth':      auger_cli.commands.auth,
    'clusters':  auger_cli.commands.clusters.cli,
    'help':      auger_cli.commands.help,
    'instances': auger_cli.commands.instances,
    'keys':      auger_cli.commands.keys,
    'orgs':      auger_cli.commands.orgs,
    'projects':  auger_cli.commands.projects.cli,
    'start':     auger_cli.commands.start.cli,
    'stop':      auger_cli.commands.stop.cli,
    'schema':    auger_cli.commands.schema
}


class AugerCLI(click.MultiCommand):
    def list_commands(self, ctx):
        return sorted(COMMANDS.keys())

    def get_command(self, ctx, name):
        if name not in COMMANDS:
            raise click.UsageError(
                message=(
                    "'{}' is not an auger command.\n"
                    "Run 'auger help' for a list of available topics."
                ).format(name)
            )
        return COMMANDS[name].cli


@click.command('auger', cls=AugerCLI, context_settings=CONTEXT_SETTINGS)
@client.pass_client
def cli(ctx):
    """Auger command line interface."""
