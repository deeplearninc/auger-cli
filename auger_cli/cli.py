# -*- coding: utf-8 -*-

import click
from .cluster_config import ClusterConfig
from .client import Client
import os
import sys


CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGER')
pass_client = click.make_pass_decorator(Client, ensure=True)
pass_cluster = click.make_pass_decorator(ClusterConfig, ensure=True)


class AugerCLI(click.MultiCommand):
    cmd_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'commands')
    )

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(AugerCLI.cmd_folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        if sys.version_info[0] == 2:
            name = name.encode('ascii', 'replace')
        mod = __import__(
            'auger_cli.commands.' + name, None, None, ['cli']
        )
        return mod.cli


@click.command('auger', cls=AugerCLI, context_settings=CONTEXT_SETTINGS)
@pass_client
def cli(ctx):
    """Auger command line interface."""
