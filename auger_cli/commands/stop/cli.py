# -*- coding: utf-8 -*-

import click

from ..clusters.api import list_clusters, delete_cluster
from ..projects.api import list_projects, delete_project
from ...client import pass_client


@click.command(short_help='Stop project.')
@click.argument('project')
@pass_client
def stop_group(ctx, project):
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
    if not ok:
        raise click.ClickException('Failed to delete cluster.')
