# -*- coding: utf-8 -*-

from auger_cli.utils import request_list, wait_for_object_state


display_attributes = [
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

def list(client, organization_id=None):
    params = {}
    if organization_id is not None:
        params={'organization_id': organization_id}
        
    return request_list(client, 'clusters', params=params)


def read(client, cluster_id, attributes=None):
    result = client.call_hub_api(['clusters', 'read'], params={'id': cluster_id})
    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result


def is_running(client, cluster):
    return cluster.get('status') == 'running'

def create(client, organization_id, project_id,
        worker_count, instance_type, kubernetes_stack, autoterminate_minutes, wait=True):
    params={
        'organization_id': organization_id,
        'project_id': project_id,
        'worker_nodes_count': worker_count,
        'instance_type': instance_type,
        'kubernetes_stack': kubernetes_stack,
        'autoterminate_minutes': autoterminate_minutes
    }
    cluster = client.call_hub_api(['clusters', 'create'], params= params)

    if wait and 'id' in cluster:
        cluster = wait_for_object_state(client,
            endpoint=['clusters', 'read'],
            params={'id': cluster['id']},
            first_status=cluster['status'],
            progress_statuses=[
                'waiting', 'provisioning', 'bootstrapping'
            ],
            poll_interval=10
        )

    return cluster    

def delete(client, cluster_id, wait=True):
    cluster = client.call_hub_api(['clusters', 'delete'], params={'id': cluster_id})
    if cluster.get('id') == int(cluster_id):
        client.print_line("Deleting {}.".format(cluster['name']))
        if wait:
            cluster = wait_for_object_state(client,
                endpoint=['clusters', 'read'],
                params={'id': cluster['id']},
                first_status=cluster['status'],
                progress_statuses=[
                    'running', 'terminating'
                ],
                poll_interval=10
            )
            return cluster.get('status') == 'terminated'

    return False        
