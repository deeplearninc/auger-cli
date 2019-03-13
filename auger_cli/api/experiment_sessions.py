# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list

display_attributes = ['id', 'project_id', 'experiment_id', 'status', 'datasource_name', 'model_type', 'error']
display_list_attributes = ['id', 'status', 'datasource_name', 'created_at', 'model_type', 'error']


def list(client, project_id, experiment_id):
    return request_list( client,
        'experiment_sessions',
        params={'project_id': project_id, 'experiment_id': experiment_id, 'limit': 10}
    )


def read(client, experiment_session_id, attributes=None):
    result = client.call_hub_api(['experiment_sessions', 'read'], params={'id': experiment_session_id})
    if result.get('status') == 'error':
        result['error'] = result.get('model_settings', {}).get('errors')

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

def create(client, project_id, experiment_id):
    return client.call_hub_api(['experiment_sessions', 'create'], 
        params = {
            'project_id': project_id,
            'experiment_id': experiment_id    
        })

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

    return client.call_hub_api(['experiment_sessions', 'update'], params=params)

