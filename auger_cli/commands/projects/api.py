# -*- coding: utf-8 -*-

import click

from ...cluster_config import ClusterConfig
from ...formatter import command_progress_bar, print_record, print_line


project_attributes = [
    'id',
    'name',
    'status',
    'cluster_id',
    'created_at',
    'deploy_progress',
    'services_status',
    'jobs_status'
]


def list_projects(ctx):
    with ctx.coreapi_action():
        return ctx.client.action(ctx.document, ['projects', 'list'])


def create_project(ctx, project, organization_id):
    with ctx.coreapi_action():
        params = {
            'name': project,
            'organization_id': organization_id
        }
        result = ctx.client.action(
            ctx.document,
            ['projects', 'create'],
            params=params
        )
        print_record(result['data'], project_attributes)


def delete_project(ctx, project):
    with ctx.coreapi_action():
        ctx.client.action(
            ctx.document,
            ['projects', 'delete'],
            params={'name': project}
        )
        print_line('Deleted {}.'.format(project))


def deploy_project(ctx, project, cluster_id, wait):
    cluster_config = ClusterConfig(
        ctx,
        project=project,
        cluster_id=cluster_id
    )
    print_line('Setting up docker registry.')
    cluster_config.login()
    print_line('Preparing project to deploy.')
    cluster_config.docker_client.build()
    print_line('Deploying project. (This may take a few minutes.)')
    cluster_config.docker_client.push()
    definition = ''
    with open('.auger/service.yml') as f:
        definition = f.read()

    project_data = ctx.client.action(
        ctx.document,
        ['projects', 'deploy'],
        params={
            'name': project,
            'cluster_id': cluster_id,
            'definition': definition
        }
    )['data']
    print_record(project_data, project_attributes)
    if wait:
        return command_progress_bar(
            ctx=ctx,
            endpoint=['projects', 'read'],
            params={'name': project_data['name']},
            first_status=project_data['status'],
            progress_statuses=['undeployed', 'deploying', 'deployed'],
            desired_status='running'
        )
    else:
        print_line('Done.')


def launch_project_url(ctx, project):
    project = ctx.client.action(
        ctx.document,
        ['projects', 'read'],
        params={
            'name': project
        }
    )
    project_url = project['data']['url']
    return click.launch(project_url)
