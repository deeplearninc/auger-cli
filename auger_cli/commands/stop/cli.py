# -*- coding: utf-8 -*-

import click

from ..clusters.api import list_clusters, delete_cluster
from ..projects.api import list_projects, delete_project
from ...client import pass_client


@click.command(short_help='Stop project.')
@click.argument('project')
@pass_client
def stop_group(auger_client, project):
    for p in list_projects(auger_client):
        if p['name'] == project:
            delete_project(auger_client, project)
            break

    ok = True
    # call to list is to avoid race condition with delete_cluster
    for c in list(list_clusters(auger_client)):
        if c['status'] != 'terminated' and c['name'] == project:
            if not delete_cluster(auger_client, cluster_id=c['id'], wait=True):
                ok = False
    if not ok:
        raise click.ClickException('Failed to delete cluster.')
