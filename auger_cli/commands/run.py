# -*- coding: utf-8 -*-

import click
import re
import sys

from .lib.lib import (
    clusters_list,
    clusters_create,
    clusters_delete,
    projects_list,
    projects_create,
    projects_delete,
    projects_deploy,
    projects_open
)
from ..cli import pass_client
from ..cluster_config import ClusterConfig
from ..formatter import print_record


@click.group(
    'run',
    invoke_without_command=True,
    short_help='Run project.'
)
@click.pass_context
def cli(ctx):
    pass


@click.command(short_help='Start project.')
@click.argument('project')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the project will use.'
)
@pass_client
def start(ctx, project, organization_id):
    projects_create(
        ctx,
        project=project,
        organization_id=organization_id
    )

    clusters_create_result = clusters_create(
        ctx,
        name=project,
        organization_id=organization_id,
        worker_count=1,
        instance_type='t2.medium',
        wait=True
    )

    if not clusters_create_result.ok:
        sys.exit(1)

    projects_deploy_ok = projects_deploy(
        ctx,
        project=project,
        cluster_id=clusters_create_result.cluster_id,
        wait=True
    )
    if not projects_deploy_ok:
        sys.exit(1)

    projects_open(ctx, project)
    sys.exit(0)


@click.command(short_help='Stop project.')
@click.argument('project')
@pass_client
def stop(ctx, project):
    projects = projects_list(ctx)['data']

    found = False
    for p in projects:
        if p['name'] == project:
            found = True
    if found:
        projects_delete(ctx, project)

    ok = True
    for c in clusters_list(ctx)['data']:
        if c['status'] != 'terminated' and c['name'] == project:
            if not clusters_delete(ctx, cluster_id=c['id'], wait=True):
                ok = False
    sys.exit(0 if ok else 1)


@click.command(short_help='Show project configuration.')
@click.argument('project')
@pass_client
def show(ctx, project):
    for c in clusters_list(ctx)['data']:
        if c['status'] != 'terminated' and c['name'] == project:
            project = ClusterConfig(
                ctx,
                project=project,
                cluster_id=c['id']
            ).project_config
            registry = ClusterConfig.fetch(ctx, cluster_id=c['id'])[
                'registry'
            ]
            print_record(
                {
                    'cluster_id': project['cluster_id'],
                    'registry_host': project['registry_host'],
                    'login': registry.get('login'),
                    'password': registry.get('password')
                },
                ['cluster_id', 'registry_host', 'login', 'password']
            )


cli.add_command(start)
cli.add_command(stop)
cli.add_command(show)
