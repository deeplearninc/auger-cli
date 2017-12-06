# -*- coding: utf-8 -*-

import click

from ...cluster_config import ClusterConfig
from ...formatter import command_progress_bar, print_record, print_line

clusters_attributes = [
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


def clusters_list(ctx):
    return ctx.client.action(ctx.document, ['clusters', 'list'])


class ClustersCreateResult(object):
    def __init__(self, ok, cluster_id):
        self.ok = ok
        self.cluster_id = cluster_id


def clusters_create(
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
        print_record(cluster, clusters_attributes)
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
            return ClustersCreateResult(ok, cluster['id'])


def clusters_delete(ctx, cluster_id, wait):
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


projects_attributes = [
    'id',
    'name',
    'status',
    'cluster_id',
    'created_at',
    'deploy_progress',
    'services_status',
    'jobs_status'
]


def projects_list(ctx):
    with ctx.coreapi_action():
        return ctx.client.action(ctx.document, ['projects', 'list'])


def projects_create(ctx, project, organization_id):
    with ctx.coreapi_action():
        params = {
            'name': project,
            'organization_id': organization_id
        }
        result = ctx.client.action(
            ctx.document,
            ['projects', 'create'],
            params=params
        )
        print_record(result['data'], projects_attributes)


def projects_delete(ctx, project):
    with ctx.coreapi_action():
        ctx.client.action(
            ctx.document,
            ['projects', 'delete'],
            params={'name': project}
        )
        print_line('Deleted {}.'.format(project))


def projects_deploy(ctx, project, cluster_id, wait):
    cluster_config = ClusterConfig(
        ctx,
        project=project,
        cluster_id=cluster_id
    )
    print_line('Setting up docker registry.')
    cluster_config.login()
    print_line('Preparing project to deploy.')
    cluster_config.docker_client.build()
    print_line('Deploying project. (This may take a few minutes.)')
    cluster_config.docker_client.push()
    definition = ''
    with open('.auger/service.yml') as f:
        definition = f.read()

    project_data = ctx.client.action(
        ctx.document,
        ['projects', 'deploy'],
        params={
            'name': project,
            'cluster_id': cluster_id,
            'definition': definition
        }
    )['data']
    print_record(project_data, projects_attributes)
    if wait:
        return command_progress_bar(
            ctx=ctx,
            endpoint=['projects', 'read'],
            params={'name': project_data['name']},
            first_status=project_data['status'],
            progress_statuses=['undeployed', 'ready'],
            desired_status='running'
        )
    else:
        print_line('Done.')


def projects_open(ctx, project):
    project = ctx.client.action(
        ctx.document,
        ['projects', 'read'],
        params={
            'name': project
        }
    )
    project_url = project['data']['url']
    return click.launch(project_url)
