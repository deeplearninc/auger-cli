# -*- coding: utf-8 -*-

import click
import sys

from .clusters.api import (
    list_clusters,
    create_cluster,
    delete_cluster
)
from .projects.api import (
    list_projects,
    create_project,
    delete_project,
    deploy_project,
    launch_project_url
)
from ..client import pass_client
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
    create_project(
        ctx,
        project=project,
        organization_id=organization_id
    )

    clusters_create_result = create_cluster(
        ctx,
        name=project,
        organization_id=organization_id,
        worker_count=1,
        instance_type='t2.medium',
        wait=True
    )

    if not clusters_create_result.ok:
        sys.exit(1)

    ok = deploy_project(
        ctx,
        project=project,
        cluster_id=clusters_create_result.cluster_id,
        wait=True
    )
    if not ok:
        sys.exit(1)

    launch_project_url(ctx, project)
    sys.exit(0)


@click.command(short_help='Stop project.')
@click.argument('project')
@pass_client
def stop(ctx, project):
    projects = list_projects(ctx)['data']

    found = False
    for p in projects:
        if p['name'] == project:
            found = True
    if found:
        delete_project(ctx, project)

    ok = True
    for c in list_clusters(ctx)['data']:
        if c['status'] != 'terminated' and c['name'] == project:
            if not delete_cluster(ctx, cluster_id=c['id'], wait=True):
                ok = False
    sys.exit(0 if ok else 1)


cli.add_command(start)
cli.add_command(stop)
