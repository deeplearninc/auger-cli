# -*- coding: utf-8 -*-

import os

from auger_cli.utils import request_list, download_remote_file, wait_for_object_state
from auger_cli.constants import REQUEST_LIMIT

from auger_cli.api import clusters
from auger_cli.api import orgs
from auger_cli.api import cluster_tasks
from auger_cli.api import experiment_sessions

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


def list(client, org_id=None):
    params = {}
    if org_id:
        params = {'organization_id': org_id}

    return request_list(client, 'projects', params=params)


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
            for item in projects_list:
                if item['name'] == project_name:
                    result = item

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
            cluster_config=client.config.get_cluster_settings()
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

def read_leaderboard(client):
    from datetime import datetime
    from auger_cli.formatter import print_list

    #Get running projects
    org_id = orgs.read(client).get('id')
    list_projects = list(client, org_id=org_id)
    running_projects = []
    for item in list_projects:
        if item.get('status') == 'running':
            running_projects.append(item)

    leaderboard = []
    for item in running_projects:
        exp_sessions = [res for res in experiment_sessions.list(client, project_id = item.get('id'), experiment_id=None, limit=100)]
        exp_sessions.sort(key=lambda t: t.get('created_at'), reverse=True)

        running_session = {}
        completed_sessions = 0
        for exp_session in exp_sessions:
            if exp_session.get('status') == 'started' and len(running_session) == 0:
                running_session = exp_session

            if exp_session.get('status') == 'completed':    
                completed_sessions+=1

        session_time = 0        
        dt_format = '%Y-%m-%dT%H:%M:%S.%fZ'
        if running_session.get('created_at'):
            session_time = int((datetime.utcnow()-datetime.strptime(running_session.get('created_at'), dt_format)).total_seconds()/60.0)

        data_name = running_session.get('model_settings', {}).get('evaluation_options', {}).get('data_name','')
        if len(data_name) == 0:
            data_name = os.path.basename(running_session.get('model_settings', {}).get('evaluation_options', {}).get('data_path',''))
            
        leaderboard.append({
            'id': item.get('id'),
            'name': item.get('name'),
            'status': item.get('status'),
            'session_id': running_session.get('id'),
            'session_time': session_time,
            'session_trials': running_session.get('model_settings', {}).get('completed_evaluations'),
            'completed': completed_sessions,
            'data_name': data_name,
        })
            
    return leaderboard
