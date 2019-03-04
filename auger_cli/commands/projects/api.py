# -*- coding: utf-8 -*-

import click
import os

from ...formatter import command_progress_bar, print_record, print_line, wait_for_task_result
from ...utils import request_list, download_remote_file
from ...auger_config import AugerConfig

from ..clusters.api import create_cluster
from ..orgs.api import (
    read_org,
    list_orgs_full
)
from ..cluster_tasks.api import (
    create_cluster_task_ex,
)

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


def read_project(auger_client, name):
    result = {}
    with auger_client.coreapi_action():
        res = auger_client.client.action(
            auger_client.document,
            ['projects', 'list'],
            params={'name': name, 'limit': 10}
        )['data']
        if len(res) > 0:
            result = res[0]
        
    return result

def read_project_withorg(auger_client, name, organization_id):
    result = {}
    with auger_client.coreapi_action():
        res = auger_client.client.action(
            auger_client.document,
            ['projects', 'list'],
            params={'name': name, 'limit': 10, 'organization_id': organization_id}
        )['data']
        if len(res) > 0:
            result = res[0]
        
    return result

def read_project_byid(auger_client, project_id):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['projects', 'read'],
            params={'id': project_id}
        )['data']
        
    return result

def list_projects(auger_client):
    # request_list requires some limit and we use one big enough
    return request_list(auger_client, 'projects', params={'limit': 1000000000})


def create_project(auger_client, project, organization_id):
    params = {
        'name': project,
        'organization_id': organization_id
    }
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['projects', 'create'],
            params=params
        )
    print_record(result['data'], project_attributes)

    return result['data']

def delete_project(auger_client, project):
    with auger_client.coreapi_action():
        auger_client.client.action(
            auger_client.document,
            ['projects', 'delete'],
            params={'name': project}
        )
        print_line('Deleted {}.'.format(project))


def get_or_create_project(ctx, create_if_not_exist=False, project_id=None):
    if project_id is None:
        project_id = ctx.config.get_project_id()
    if project_id is not None:
        return read_project_byid(ctx, project_id)

    project_name = ctx.config.get_project_name()

    org_id, org_name = ctx.config.get_org()
    if org_id is None and len(org_name) == 0:
        orgs = list_orgs_full(ctx)
        if orgs is not None and len(orgs) > 0:
            org_name = orgs[0].get('name', "")
            org_id = orgs[0].get('id')

        if len(org_name) == 0:    
            raise click.ClickException('To create project: %s, you should have at least one organization.'%project_name)

    if org_id is None:    
        org = read_org(ctx, org_name)
        if org.get('id') is None:
            raise click.ClickException('To create project: %s, organization %s should exist.'%(project_name, org_name))
        org_id = org['id']    
            
    project = read_project_withorg(ctx, project_name, org_id)
    if project.get('id') is not None:
        return project

    if create_project:    
        project = create_project(ctx, project_name, org_id)
        return project

    raise click.ClickException("Project %s does not exist."%project_name)

def start_project(ctx, create_if_not_exist=False, project_id=None):
    project = get_or_create_project(ctx, create_if_not_exist=create_if_not_exist, project_id=project_id)

    if project.get('cluster_id') is None or project['status'] == 'undeployed':
        clusters_create_result = create_cluster(
            ctx,
            organization_id=project['organization_id'],
            project_id=project['id'],
            worker_count=ctx.config.get_cluster_settings()['worker_count'],
            instance_type=ctx.config.get_cluster_settings()['instance_type'],
            kubernetes_stack=ctx.config.get_cluster_settings()['kubernetes_stack'],
            wait=True
        )

        if not clusters_create_result.ok:
            raise click.ClickException('Failed to create cluster.')

    wait_for_task_result(
        auger_client=ctx,
        endpoint=['projects', 'read'],
        params={'id': project['id']},
        first_status=project['status'],
        progress_statuses=[
            'undeployed', 'deployed', 'deploying'
        ],
        poll_interval=10
    )

    return project['id']

def download_project_file(ctx, project_id, remote_path, local_path):
    ctx.config = AugerConfig()

    start_project(ctx, project_id=project_id)

    s3_model_path = create_cluster_task_ex(ctx, project_id, 
        "pipeline_functions.packager.tasks.upload_file", remote_path
    )
    print(s3_model_path)

    s3_signed_model_path = create_cluster_task_ex(ctx, project_id, 
        "pipeline_functions.packager.tasks.generate_presigned_url", s3_model_path
    )
    print(s3_signed_model_path)

    download_remote_file(ctx, local_path, s3_signed_model_path)


def launch_project_url(auger_client, project):
    return click.launch(read_project(auger_client, project)['url'])
