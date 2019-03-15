# -*- coding: utf-8 -*-

import os

from auger_cli.utils import request_list, download_remote_file, wait_for_object_state
from auger_cli.constants import REQUEST_LIMIT

from auger_cli.api import clusters
from auger_cli.api import orgs
from auger_cli.api import cluster_tasks

display_attributes = [
    'id',
    'name',
    'status',
    'cluster_id',
    'created_at',
    'deploy_progress',
    'services_status',
    'jobs_status'
]


def list(client):
    return request_list(client, 'projects', params={})


def read(client, project_name=None, org_id=None, project_id=None):
    result = {}
    if project_id:
        result = client.call_hub_api('get_project', {'id': project_id})
    elif project_name:
        if org_id:
            projects_list = client.call_hub_api('get_projects', {
                'name': project_name,
                'limit': REQUEST_LIMIT,
                'organization_id': org_id
            })
        else:
            projects_list = client.call_hub_api('get_projects', {
                'name': project_name,
                'limit': REQUEST_LIMIT
            })

        if len(projects_list) > 0:
            result = projects_list[0]

    return result


def create(client, project, organization_id):
    return client.call_hub_api('create_project', {
        'name': project,
        'organization_id': organization_id
    })

def delete(client, project_id):
    client.call_hub_api('delete_project', {'id': project_id})


def get_or_create(client, create_if_not_exist=False, project_id=None):
    if project_id is None:
        project_id = client.config.get_project_id()
    if project_id is not None:
        return read(client, project_id=project_id)

    project_name = client.config.get_project_name()
    org_id = orgs.read(client).get('id')
    if org_id is None:
        raise Exception('To create project: %s, you should have at least one organization.'%project_name)

    project = read(client, project_name=project_name, org_id=org_id)
    if project.get('id') is not None:
        return project

    if create_if_not_exist:
        project = create(client, project_name, org_id)
        return project

    raise Exception("Project %s does not exist."%project_name)

def start(client, create_if_not_exist=False, project_id=None):
    project = get_or_create(client, create_if_not_exist=create_if_not_exist, project_id=project_id)

    if project.get('cluster_id') is None or project['status'] == 'undeployed':
        cluster = clusters.create( client,
            organization_id=project['organization_id'],
            project_id=project['id'],
            worker_count=client.config.get_cluster_settings()['worker_count'],
            instance_type=client.config.get_cluster_settings()['instance_type'],
            kubernetes_stack=client.config.get_cluster_settings()['kubernetes_stack'],
            autoterminate_minutes=client.config.get_cluster_settings()['autoterminate_minutes']
        )

        if not clusters.is_running(client, cluster):
            raise Exception('Failed to create cluster.')

    wait_for_object_state(client,
        method='get_project',
        params={'id': project['id']},
        first_status=project['status'],
        progress_statuses=[
            'undeployed', 'deployed', 'deploying'
        ],
        poll_interval=10
    )

    return project['id']

def download_file(client, project_id, remote_path, local_path):
    project_id = start(client, project_id=project_id)

    s3_model_path = cluster_tasks.create_ex(client, project_id,
        "pipeline_functions.packager.tasks.upload_file", remote_path
    )

    s3_signed_model_path = cluster_tasks.create_ex(client, project_id,
        "pipeline_functions.packager.tasks.generate_presigned_url", s3_model_path
    )
    client.print_line("Model S3 path: %s"%s3_signed_model_path)

    return download_remote_file(local_path, s3_signed_model_path)


def list_files(client, project_id, remote_path):
    project_id = start(client, project_id=project_id)

    task_args = {'augerInfo': {}}
    if remote_path:
        task_args = {'augerInfo': {'filesPath': remote_path}}

    return cluster_tasks.create_ex(client, project_id,
        "auger_ml.tasks_queue.tasks.list_project_files_task", task_args
    )
