# -*- coding: utf-8 -*-

import click

from . import client

from auger_cli.commands.auth.cli import auth_group
from auger_cli.commands.clusters.cli import clusters_group
from auger_cli.commands.help.cli import help_group
from auger_cli.commands.instances.cli import instances_group
from auger_cli.commands.orgs.cli import orgs_group
from auger_cli.commands.projects.cli import projects_group
from auger_cli.commands.schema.cli import schema_group
from auger_cli.commands.start.cli import start_group
from auger_cli.commands.stop.cli import stop_group
from auger_cli.commands.cluster_tasks.cli import cluster_tasks_group

CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGER')
COMMANDS = {
    'auth':      auth_group,
    'clusters':  clusters_group,
    'cluster_tasks':  cluster_tasks_group,
    'help':      help_group,
    'instances': instances_group,
    'orgs':      orgs_group,
    'projects':  projects_group,
    'schema':    schema_group,
    'start':     start_group,
    'stop':      stop_group
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
        return COMMANDS[name]


@click.command('auger', cls=AugerCLI, context_settings=CONTEXT_SETTINGS)
@client.pass_client
def cli(ctx):
    """Auger command line interface."""
