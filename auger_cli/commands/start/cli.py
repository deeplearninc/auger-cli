# -*- coding: utf-8 -*-

import click

from ..clusters.api import create_cluster
from ..projects.api import (
    create_project,
    deploy_project,
    launch_project_url
)
from ...client import pass_client


@click.command(short_help='Start project.')
@click.argument('project')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the project will use.'
)
@pass_client
def cli(ctx, project, organization_id):
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
        raise click.ClickException('Failed to create cluster.')

    ok = deploy_project(
        ctx,
        project=project,
        cluster_id=clusters_create_result.cluster_id,
        wait=True
    )
    if not ok:
        raise click.ClickException('Failed to deploy project.')

    launch_project_url(ctx, project)
