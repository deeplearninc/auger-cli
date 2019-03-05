# -*- coding: utf-8 -*-

from ...formatter import command_progress_bar, print_record, print_line
from ...utils import request_list


cluster_attributes = [
    'id',
    'status',
    'project_name',
    'worker_nodes_count',
    'instance_type',
    'total_memory_mb',
    'kubernetes_stack'
    'name',
    'organization_id',
    'error_message',
    'seconds_since_created',
    # 'uptime_seconds',
    # 'ip_address',
]


def list_clusters(auger_client, organization_id=None):
    if organization_id is not None:
        return request_list(auger_client, 'clusters', params={'organization_id': organization_id})
    else:    
        return request_list(auger_client, 'clusters', params={})


def read_cluster(auger_client, cluster_id, attributes=None):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['clusters', 'read'],
            params={'id': cluster_id}
        )['data']
    
    #print(result.keys()) 
    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

class CreateResult(object):
    def __init__(self, ok, cluster_id):
        self.ok = ok
        self.cluster_id = cluster_id


def create_cluster(
        auger_client, organization_id, project_id,
        worker_count, instance_type, kubernetes_stack, autoterminate_minutes, wait):
    with auger_client.coreapi_action():
        params={
            'organization_id': organization_id,
            'project_id': project_id,
            'worker_nodes_count': worker_count,
            'instance_type': instance_type,
            'kubernetes_stack': kubernetes_stack,
            'autoterminate_minutes': autoterminate_minutes
        }
        cluster = auger_client.client.action(
            auger_client.document,
            ['clusters', 'create'],
            params= params
        )['data']
        print_record(cluster, cluster_attributes)

        if wait:
            ok = command_progress_bar(
                auger_client=auger_client,
                endpoint=['clusters', 'read'],
                params={'id': cluster['id']},
                first_status=cluster['status'],
                progress_statuses=[
                    'waiting', 'provisioning', 'bootstrapping'
                ],
                desired_status='running',
                poll_interval=10
            )
            return CreateResult(ok, cluster['id'])


def delete_cluster(auger_client, cluster_id, wait):
    with auger_client.coreapi_action():
        cluster = auger_client.client.action(
            auger_client.document,
            ['clusters', 'delete'],
            params={
                'id': cluster_id
            }
        )['data']
        if cluster['id'] == int(cluster_id):
            print_line("Deleting {}.".format(cluster['name']))
            if wait:
                return command_progress_bar(
                    auger_client=auger_client,
                    endpoint=['clusters', 'read'],
                    params={'id': cluster['id']},
                    first_status=cluster['status'],
                    progress_statuses=[
                        'running', 'terminating'
                    ],
                    desired_status='terminated',
                    poll_interval=10
                )
