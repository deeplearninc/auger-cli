import json

from auger_cli.utils import request_list, wait_for_object_state


display_attributes = ['id', 'cluster_id', 'project_id',
                           'status', 'name', 'args', 'result', 'exception']

def list(client, project_id):
    return request_list(client, 'cluster_tasks',
                        params={'project_id': project_id})


def read(client, cluster_task_id):
    return client.call_hub_api('get_cluster_task', {'id': cluster_task_id})


def create(client, project_id, name, args, wait=True):
    result = client.call_hub_api('create_cluster_task', {
        'project_id': project_id,
        'name': name,
        'args_encoded': args,
    })

    if wait and 'id' in result:
        result = wait_for_object_state(client,
            method='get_cluster_task',
            params={'id': result['id']},
            first_status=result['status'],
            progress_statuses=[
                'pending', 'received', 'started', 'retry'
            ]
        ).get('result')

    return result


def create_ex(client, project_id, name, args_python, wait=True):
    return create(client, project_id, name, json.dumps([args_python]), wait)


def run(client, wait):
    from auger_cli.api import projects

    project_id = projects.start(client, create_if_not_exist=True)
    cluster_task = client.config.get_cluster_task()

    create_ex(client, project_id, cluster_task.get(
        'name'), cluster_task.get('params'), wait)
