# -*- coding: utf-8 -*-

import click
import os

from ...constants import SERVICE_YAML_PATH, PROJECT_FILES_PATH
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
    with open(SERVICE_YAML_PATH) as f:
        definition = f.read()

    with ctx.coreapi_action():
        project_id = ctx.client.action(
            ctx.document,
            ['projects', 'read'],
            params={'name': project}
        )['data']['id']

    # remove old project files
    # get list and remove listed files in loop (as list is limited)
    while True:
        with ctx.coreapi_action():
            file_list = ctx.client.action(
                ctx.document,
                ['project_files', 'list'],
                params={'project_id': project_id}
            )['data']
        if len(file_list) == 0:
            break
        for item in file_list:
            with ctx.coreapi_action():
                ctx.client.action(
                    ctx.document,
                    ['project_files', 'delete'],
                    params={'id': item['id'], 'project_id': project_id}
                )

    # deploy project files
    for dirpath, _, filenames in os.walk(PROJECT_FILES_PATH, followlinks=True):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            content = open(filepath, 'rb').read()
            try:
                content = content.decode('utf-8')
            except UnicodeDecodeError:
                print_line(
                    'Warning: Cannot deploy binary file ({}).'.format(
                        filepath
                    ),
                    err=True
                )
                continue
            assert filepath.startswith('{}/'.format(PROJECT_FILES_PATH))
            with ctx.coreapi_action():
                ctx.client.action(
                    ctx.document,
                    ['project_files', 'create'],
                    params={
                        'name': filepath[len(PROJECT_FILES_PATH) + 1:],
                        'content': content,
                        'project_id': project_id
                    }
                )

    # deploy project itself
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
