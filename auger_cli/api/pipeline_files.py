# -*- coding: utf-8 -*-

from auger_cli.utils import request_list
from auger_cli.constants import REQUEST_LIMIT


display_attributes = ['id', 'signed_s3_model_path', 'signed_s3_model_path_status', 'error_message',
                      's3_model_path_status', 'trial_id', 'model_path_status','experiment_session_id',
                      'signed_s3_model_path_status']

def list(client, organization_id, experiment_id, experiment_session_id):
    params = {}
    if organization_id:
        params['organization_id'] = organization_id
    if experiment_id:
        params['experiment_id'] = experiment_id
    if experiment_session_id:
        params['experiment_session_id'] = experiment_session_id

    return request_list(client, 'pipeline_files', params=params)


def read(client, pipeline_id, attributes=None):
    result = client.call_hub_api('get_pipeline_files', {'id': pipeline_file_id})

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result


def create(client, params):
    return client.call_hub_api('create_pipeline_file', params)

