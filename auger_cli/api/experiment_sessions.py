# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list

display_attributes = ['id', 'project_id', 'experiment_id', 'status', 'datasource_name', 'model_type']
display_list_attributes = ['id', 'status', 'datasource_name', 'created_at', 'model_type']


def list(client, project_id, experiment_id):
    return request_list( client,
        'experiment_sessions',
        params={'project_id': project_id, 'experiment_id': experiment_id, 'limit': 10}
    )


def read(client, experiment_session_id, attributes=None):
    result = client.call_hub_api(['experiment_sessions', 'read'], params={'id': experiment_session_id})

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

