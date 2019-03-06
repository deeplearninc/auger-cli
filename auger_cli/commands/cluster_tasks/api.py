import json

from ...utils import request_list
from ...formatter import wait_for_task_result
from ...auger_config import AugerConfig

cluster_task_attributes = ['id', 'cluster_id', 'project_id',
                           'status', 'name', 'args', 'result', 'exception']


def list_cluster_tasks(auger_client, project_id):
    return request_list(auger_client, 'cluster_tasks',
                        params={'project_id': project_id})


def create_cluster_task_ex(auger_client, project_id, name, args_python, wait=True):
    return create_cluster_task(auger_client, project_id, name, json.dumps([args_python]), wait)

def create_cluster_task(auger_client, project_id, name, args, wait=True):
    result = auger_client.client.action(
        auger_client.document,
        ['cluster_tasks', 'create'],
        params={
            'project_id': project_id,
            'name': name,
            'args_encoded': args,
        }
    )['data']
    if wait and 'id' in result:
        result = wait_for_task_result(
            auger_client=auger_client,
            endpoint=['cluster_tasks', 'read'],
            params={'id': result['id']},
            first_status=result['status'],
            progress_statuses=[
                'pending', 'received', 'started', 'retry'
            ]
        )
    return result

def run_cluster_task(ctx, wait):
    from ..projects.api import start_project

    ctx.config = AugerConfig()

    project_id = start_project(ctx, create_if_not_exist=True)
    cluster_task = ctx.config.get_cluster_task()

    create_cluster_task_ex(ctx, project_id, cluster_task.get('name'), cluster_task.get('params'), wait)
