# -*- coding: utf-8 -*-
import os
import click

from auger_cli.formatter import print_line, print_record
from auger_cli.utils import request_list

experiment_session_attributes = ['id', 'project_id', 'experiment_id', 'status', 'datasource_name', 'model_type']
experiment_session_list_attributes = ['id', 'status', 'datasource_name', 'created_at', 'model_type']


def list_experiment_sessions(ctx, project_id, experiment_id):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'experiment_sessions',
            params={'project_id': project_id, 'experiment_id': experiment_id, 'limit': 10}
        )


def read_experiment_session(auger_client, experiment_session_id, attributes=None):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['experiment_sessions', 'read'],
            params={'id': experiment_session_id}
        )['data']
        #print(result.keys())

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    #print(attributes)    
    return result

