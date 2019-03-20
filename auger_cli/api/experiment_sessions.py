# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list

display_attributes = ['id', 'project_id', 'experiment_id', 'status', 'model_type']
display_list_attributes = ['id', 'project_id', 'experiment_id', 'status', 'created_at', 'model_type']


def list(client, project_id, experiment_id, limit=10):
    return request_list(client, 'experiment_sessions', {
        'project_id': project_id,
        'experiment_id': experiment_id,
        'limit': limit
    })


def read(client, experiment_session_id, attributes=None):
    result = client.call_hub_api('get_experiment_session', {'id': experiment_session_id})
    if result.get('status') == 'error':
        result['error'] = result.get('model_settings', {}).get('errors')

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

def create(client, params):
    return client.call_hub_api('create_experiment_session', params)

def update(client, experiment_session_id, status=None, model_settings = None, model_type = None):
    params = {
        'id': experiment_session_id
    }
    if status is not None:
        params['status'] = status
    if model_settings is not None:
        params['model_settings'] = model_settings
    if model_type is not None:
        params['model_type'] = model_type

    return client.call_hub_api('update_experiment_session', params)

