# -*- coding: utf-8 -*-

from ...cluster_config import ClusterConfig
from ...formatter import command_progress_bar, print_record, print_line


cluster_attributes = [
    'name',
    'id',
    'organization_id',
    'status',
    'seconds_since_created',
    'uptime_seconds',
    'worker_nodes_count',
    'ip_address',
    'instance_type'
]


def list_clusters(ctx):
    return ctx.client.action(ctx.document, ['clusters', 'list'])


class CreateResult(object):
    def __init__(self, ok, cluster_id):
        self.ok = ok
        self.cluster_id = cluster_id


def create_cluster(
        ctx, name, organization_id,
        worker_count, instance_type, wait):
    with ctx.coreapi_action():
        cluster = ctx.client.action(
            ctx.document,
            ['clusters', 'create'],
            params={
                'name': name,
                'organization_id': organization_id,
                'worker_nodes_count': worker_count,
                'instance_type': instance_type
            }
        )['data']
        ClusterConfig(
            ctx,
            cluster_dict=cluster,
            cluster_id=cluster['id']
        )
        print_record(cluster, cluster_attributes)
        if wait:
            ok = command_progress_bar(
                ctx=ctx,
                endpoint=['clusters', 'read'],
                params={'id': cluster['id']},
                first_status=cluster['status'],
                progress_statuses=[
                    'waiting', 'provisioning', 'bootstrapping'
                ],
                desired_status='running'
            )
            return CreateResult(ok, cluster['id'])


def delete_cluster(ctx, cluster_id, wait):
    with ctx.coreapi_action():
        cluster = ctx.client.action(
            ctx.document,
            ['clusters', 'delete'],
            params={
                'id': cluster_id
            }
        )['data']
        if cluster['id'] == int(cluster_id):
            print_line("Deleting {}.".format(cluster['name']))
            if wait:
                return command_progress_bar(
                    ctx=ctx,
                    endpoint=['clusters', 'read'],
                    params={'id': cluster['id']},
                    first_status=cluster['status'],
                    progress_statuses=[
                        'running', 'terminating'
                    ],
                    desired_status='terminated'
                )
