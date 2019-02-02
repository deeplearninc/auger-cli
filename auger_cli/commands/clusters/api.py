# -*- coding: utf-8 -*-

from ...cluster_config import ClusterConfig
from ...formatter import command_progress_bar, print_record, print_line
from ...utils import request_list


cluster_attributes = [
    'name',
    'id',
    'organization_id',
    'status',
    'seconds_since_created',
    'uptime_seconds',
    'worker_nodes_count',
    'ip_address',
    'instance_type',
    'kubernetes_stack'
]


def list_clusters(auger_client):
    # request_list requires some limit and we use one big enough
    return request_list(auger_client, 'clusters', params={'limit': 1000000000})


class CreateResult(object):
    def __init__(self, ok, cluster_id):
        self.ok = ok
        self.cluster_id = cluster_id


def create_cluster(
        auger_client, name, organization_id,
        worker_count, instance_type, kubernetes_stack, wait):
    with auger_client.coreapi_action():
        cluster = auger_client.client.action(
            auger_client.document,
            ['clusters', 'create'],
            params={
                'name': name,
                'organization_id': organization_id,
                'worker_nodes_count': worker_count,
                'instance_type': instance_type,
                'kubernetes_stack': kubernetes_stack
            }
        )['data']
        ClusterConfig(
            auger_client,
            cluster_dict=cluster,
            cluster_id=cluster['id']
        )
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
                desired_status='running'
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
                    desired_status='terminated'
                )
