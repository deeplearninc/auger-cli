import json

from ...utils import request_list
from ...formatter import wait_for_task_result

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
