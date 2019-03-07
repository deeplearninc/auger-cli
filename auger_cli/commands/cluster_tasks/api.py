import json

from ...utils import request_list
from ...formatter import wait_for_task_result

cluster_task_attributes = ['id', 'cluster_id', 'project_id',
                           'status', 'name', 'args', 'result', 'exception']


def list_cluster_tasks(client, project_id):
    return request_list(client, 'cluster_tasks',
                        params={'project_id': project_id})


def read_cluster_task(client, cluster_task_id):
    return client.call_hub_api(['cluster_tasks', 'read'], params={'id': cluster_task_id})


def create_cluster_task_ex(client, project_id, name, args_python, wait=True):
    return create_cluster_task(client, project_id, name, json.dumps([args_python]), wait)


def create_cluster_task(client, project_id, name, args, wait=True):
    result = client.call_hub_api(
        ['cluster_tasks', 'create'],
        params={
            'project_id': project_id,
            'name': name,
            'args_encoded': args,
        }
    )

    if wait and 'id' in result:
        result = wait_for_task_result(
            auger_client=client,
            endpoint=['cluster_tasks', 'read'],
            params={'id': result['id']},
            first_status=result['status'],
            progress_statuses=[
                'pending', 'received', 'started', 'retry'
            ]
        )

    return result


def run_cluster_task(client, wait):
    from ..projects.api import start_project

    project_id = start_project(client, create_if_not_exist=True)
    cluster_task = client.config.get_cluster_task()

    create_cluster_task_ex(client, project_id, cluster_task.get(
        'name'), cluster_task.get('params'), wait)
