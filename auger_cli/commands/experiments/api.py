# -*- coding: utf-8 -*-
import os
import json
import click

from ...formatter import print_line, print_record
from ...utils import request_list, get_uid
from ...FSClient import FSClient
from ..cluster_tasks.api import (
    create_cluster_task,
)
from ..clusters.api import create_cluster

from ..projects.api import (
    read_project_withorg,
    create_project,
    read_project_byid
)

from ..orgs.api import (
    read_org,
    list_orgs_full
)

experiment_attributes = ['id', 'name', 'project_id', 'project_file_id', 'status']


def list_experiments(ctx, project_id, name):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'experiments',
            params={'limit': 1000000000, 'project_id': project_id, 'name': name}
        )

def create_experiment(ctx, name, project_id, data_path):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'create'],
            params={
                'id': "experiment_"+name+"_"+get_uid(),
                'name': name, 
                'project_id': project_id,
                'data_path': data_path
            }
        )
        return experiment['data']

    return {}    

def delete_experiment(ctx, experiment_id):
    with ctx.coreapi_action():
        experiments = ctx.client.action(
            ctx.document,
            ['experiments', 'delete'],
            params={
                'id': experiment_id
            }
        )
        experiment = experiments['data']
        if experiment['id'] == int(experiment_id):
            print_line("Deleting {0}.".format(experiment['name']))


def update_experiment(ctx, experiment_id, name):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'update'],
            params={
                'id': experiment_id,
                'name': name
            }
        )
        print_record(experiment['data'], experiment_attributes)

def read_experiment_byid(auger_client, experiment_id):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['experiments', 'read'],
            params={'id': experiment_id}
        )['data']
        
    return result

def read_experiment(auger_client, project_id, name):
    result = {}
    with auger_client.coreapi_action():
        res = auger_client.client.action(
            auger_client.document,
            ['experiments', 'list'],
            params={'name': name, 'project_id': project_id, 'limit': 10}
        )['data']
        if len(res) > 0:
            result = res[0]
        
    return result

def get_or_create_project(ctx, exp_file, name):
    if exp_file.get('project_id', None) is not None:
        return read_project_byid(ctx, exp_file['project_id'])

    project_name = exp_file.get('project_name', '')
    if len(project_name) == 0:
        project_name = os.path.basename(name)

    org_name = exp_file.get('organization', '')
    org_id = None
    if len(org_name) == 0:
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

    project = create_project(ctx, project_name, org_id)
    return project

def get_or_create_experiment(ctx, exp_file, project_id, name):
    if exp_file.get('experiment_id', None) is not None:
        return read_experiment_byid(ctx, exp_file['experiment_id'])

    experiment_name = exp_file.get('experiment_name', '')
    if len(experiment_name) == 0:
        experiment_name = os.path.basename(name)

    experiment = read_experiment(ctx, project_id, experiment_name)
    if experiment.get('id') is not None:
        return experiment

    # search_space = create_cluster_task(ctx, project_id, 
    #     "auger_ml.tasks_queue.tasks.get_experiment_configs_task", 
    #     json.dumps([{'augerInfo':{'experiment_id': None}}])
    # )
    experiment = create_experiment(ctx, experiment_name, project_id, exp_file['evaluation_options']['data_path'])
    return experiment

def run_experiment(ctx, name):
    file_name = name
    if not file_name.endswith(".json"):
        file_name += ".json"

    exp_file = FSClient().readJSONFile(os.path.abspath(file_name))
    project = get_or_create_project(ctx, exp_file, name)
    project_id = project['id']
    if project.get('cluster') is None:
        clusters_create_result = create_cluster(
            ctx,
            name=project['name'],
            organization_id=project['organization_id'],
            worker_count=2,
            instance_type='c5.large',
            kubernetes_stack='experimental',
            wait=True
        )

        if not clusters_create_result.ok:
            raise click.ClickException('Failed to create cluster.')

    experiment = get_or_create_experiment(ctx, exp_file, project_id, name)
    print(experiment)
    experiment_id = experiment['id']

    task_args = exp_file.get('evaluation_options', {})
    task_args['augerInfo'] = {'experiment_id': experiment_id}

    # result = create_cluster_task(ctx, project_id, 
    #     "auger_ml.tasks_queue.evaluate_api.run_cli_evaluate_task", 
    #     json.dumps([task_args])
    # )

    # result = create_cluster_task(ctx, project_id, 
    #     "auger_ml.tasks_queue.tasks.list_project_files_task", 
    #     json.dumps([{"augerInfo": {"experiment_id": None, "dataset_manifest_id": None}}])
    # )



