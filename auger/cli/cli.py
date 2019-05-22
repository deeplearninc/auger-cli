# -*- coding: utf-8 -*-

import click

from auger.cli.commands.auth import auth_group
from auger.cli.commands.clusters import clusters_group
from auger.cli.commands.help import help_group
from auger.cli.commands.instance_types import instance_types_group
from auger.cli.commands.orgs import orgs_group
from auger.cli.commands.projects import projects_group
from auger.cli.commands.pipelines import pipelines_group
from auger.cli.commands.experiments import experiments_group
from auger.cli.commands.experiment_sessions import experiment_sessions_group
from auger.cli.commands.trials import trials_group
from auger.cli.commands.cluster_tasks import cluster_tasks_group
from auger.cli.commands.cluster_status import cluster_status_group

CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGER')
COMMANDS = {
    'auth':      auth_group,
    'clusters':  clusters_group,
    'cluster_tasks':  cluster_tasks_group,
    'help':      help_group,
    'instance_types': instance_types_group,
    'orgs':      orgs_group,
    'projects':  projects_group,
    'experiments':  experiments_group,
    'experiment_sessions':  experiment_sessions_group,
    'pipelines':  pipelines_group,
    'trials':    trials_group,
    'cluster_status':   cluster_status_group,
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


from .cli_client import pass_client

@click.command('auger', cls=AugerCLI, context_settings=CONTEXT_SETTINGS)
@pass_client
def cli(ctx):
    """Auger command line interface."""

