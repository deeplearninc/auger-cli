# -*- coding: utf-8 -*-

import click
import os

from ...constants import SERVICE_YAML_PATH, PROJECT_FILES_PATH
from ...cluster_config import ClusterConfig
from ...formatter import command_progress_bar, print_record, print_line
from ...utils import request_list


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


def list_projects(auger_client):
    return request_list(auger_client, 'projects')


def create_project(auger_client, project, organization_id):
    with auger_client.coreapi_action():
        params = {
            'name': project,
            'organization_id': organization_id
        }
        result = auger_client.client.action(
            auger_client.document,
            ['projects', 'create'],
            params=params
        )
        print_record(result['data'], project_attributes)


def delete_project(auger_client, project):
    with auger_client.coreapi_action():
        auger_client.client.action(
            auger_client.document,
            ['projects', 'delete'],
            params={'name': project}
        )
        print_line('Deleted {}.'.format(project))


def deploy_project(auger_client, project, cluster_id, wait):
    cluster_config = ClusterConfig(
        auger_client,
        project=project,
        cluster_id=cluster_id
    )
    print_line('Setting up docker registry.')
    cluster_config.login()
    print_line('Preparing project to deploy.')
    cluster_config.docker_client.build()
    print_line('Deploying project. (This may take a few minutes.)')
    cluster_config.docker_client.push()

    project_id = None
    for p in list_projects(auger_client):
        if p['name'] == project:
            project_id = p['id']
            break
    if project_id is None:
        raise click.ClickException('Failed to find project ({}).'.format(
            project
        ))

    # remove old project files
    # get list and remove listed files in loop (as list is limited in size)
    while True:
        file_list = auger_client.client.action(
            auger_client.document,
            ['project_files', 'list'],
            params={'project_id': project_id}
        )['data']
        if len(file_list) == 0:
            break
        for item in file_list:
            auger_client.client.action(
                auger_client.document,
                ['project_files', 'delete'],
                params={
                    'id': item['id'],
                    'project_id': project_id
                }
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
            auger_client.client.action(
                auger_client.document,
                ['project_files', 'create'],
                params={
                    'name': filepath[len(PROJECT_FILES_PATH) + 1:],
                    'content': content,
                    'project_id': project_id
                }
            )

    # deploy project itself
    project_data = auger_client.client.action(
        auger_client.document,
        ['projects', 'deploy'],
        params={
            'name': project,
            'cluster_id': cluster_id,
            'definition': open(SERVICE_YAML_PATH, 'r').read()
        }
    )['data']
    print_record(project_data, project_attributes)

    if wait:
        return command_progress_bar(
            auger_client=auger_client,
            endpoint=['projects', 'read'],
            params={'name': project_data['name']},
            first_status=project_data['status'],
            progress_statuses=['undeployed', 'deploying', 'deployed'],
            desired_status='running'
        )
    else:
        print_line('Done.')


def launch_project_url(auger_client, project):
    project = auger_client.client.action(
        auger_client.document,
        ['projects', 'read'],
        params={
            'name': project
        }
    )
    project_url = project['data']['url']
    return click.launch(project_url)
