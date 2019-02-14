
from ...utils import request_list

cluster_task_attributes = ['id', 'cluster_id', 'project_id',
                           'status', 'name', 'args', 'result', 'exception']


def list_cluster_tasks(auger_client, project_id):
    # request_list requires some limit and we use one big enough
    return request_list(auger_client, 'cluster_tasks',
                        params={'limit': 1000000000, 'project_id': project_id})


class CreateResult(object):

    def __init__(self, ok, cluster_task_id):
        self.ok = ok
        self.cluster_task_id = cluster_task_id


def create_cluster_task(auger_client, project_id, name, args):
    result = None
    cluster_task = auger_client.client.action(
        auger_client.document,
        ['cluster_tasks', 'create'],
        params={
            'project_id': project_id,
            'name': name,
            'args': args,
        }
    )['data']

    # print_record(cluster_task, attributes)
    # if wait:
    #     ok = command_progress_bar(
    #         auger_client=auger_client,
    #         endpoint=['cluster_tasks', 'read'],
    #         params={'id': cluster_task['id']},
    #         first_status=cluster_task['status'],
    #         progress_statuses=[
    #             'pending', 'received', 'retry'
    #         ],
    #         desired_status='started'
    #     )
    #     result = CreateResult(ok, cluster_task['id'])

    result = CreateResult(True, cluster_task['id'])
    return result
