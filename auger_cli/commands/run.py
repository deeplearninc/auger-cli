# -*- coding: utf-8 -*-

from .lib.lib import clusters_create, projects_create, projects_deploy
from ..cli import pass_client
from ..cluster_config import ClusterConfig
from ..formatter import (
    command_progress_bar,
    print_line,
    print_list,
    print_record
)
import click
import subprocess
import sys
import time


attributes = [
    'name',
    'id',
    'organization_id',
    'status',
    'seconds_since_created',
    'uptime_seconds',
    'worker_nodes_count',
    'instance_type',
    'ip_address'
]


@click.group(
    'run',
    invoke_without_command=True,
    short_help='Run application.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        with ctx.obj.coreapi_action():
            print('UGU')
    else:
        pass


@click.command(short_help='Start application.')
@click.argument('project')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the cluster will use.'
)
@pass_client
def start(ctx, project, organization_id):
    clusters_create_result = clusters_create(ctx, name='for-%s-%d' % (project, int(time.time())),
                                             organization_id=organization_id, worker_count=1,
                                             instance_type='t2.medium', wait=True)
    if not clusters_create_result.ok:
        sys.exit(1)

    projects_create(ctx, project=project, organization_id=organization_id)

    projects_deploy_ok = projects_deploy(ctx, project=project, cluster_id=clusters_create_result.cluster_id,
                                         wait=True)
    if not projects_deploy_ok:
        sys.exit(1)

    sys.exit(0)


@click.command(short_help='Stop application.')
@click.argument('project')
@pass_client
def stop(ctx, project):
    result = subprocess.run(['auger', 'clusters', 'delete', '--wait', 'for-%s' % project])
    if result.returncode != 0:
        sys.exit(result.returncode)


cli.add_command(start)
cli.add_command(stop)
