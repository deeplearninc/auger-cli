# -*- coding: utf-8 -*-

from ...formatter import print_line, print_record
from ...utils import request_list


experiment_attributes = ['id', 'name', 'project_id', 'project_file_id', 'status']


def list_experiments(ctx, project_id):
    with ctx.obj.coreapi_action():
        return request_list(
            ctx.obj,
            'experiments',
            params={'limit': 1000000000, 'project_id': project_id}
        )


def create_experiment(ctx, name, project_id):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'create'],
            params={
                'name': name, 
                'project_id': project_id
            }
        )
        print_record(experiment['data'], experiment_attributes)


def delete_experiment(ctx, experiment_id):
    with ctx.coreapi_action():
        experiments = ctx.client.action(
            ctx.document,
            ['experiments', 'delete'],
            params={
                'id': experiment_id
            }
        )
        experiment = experiments['data']
        if experiment['id'] == int(experiment_id):
            print_line("Deleting {0}.".format(experiment['name']))


def update_experiment(ctx, experiment_id, name):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'update'],
            params={
                'id': experiment_id,
                'name': name
            }
        )
        print_record(experiment['data'], experiment_attributes)
