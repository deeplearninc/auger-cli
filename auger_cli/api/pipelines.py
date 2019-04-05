# -*- coding: utf-8 -*-

from auger_cli.utils import request_list
from auger_cli.constants import REQUEST_LIMIT


display_attributes = ['id', 'status', 'lambda_package_s3_path', 'datasource_manifest_name', 'error_message', 'project_id', 'organization_id'] #, 'trial']


def list(client, organization_id, experiment_id, active):
    params = {}
    if organization_id:
        params['organization_id'] = organization_id
    if experiment_id:
        params['experiment_id'] = experiment_id
    if active:
        params['active'] = active

    return request_list(client, 'pipelines', params=params)


def read(client, pipeline_id, attributes=None):
    result = client.call_hub_api('get_pipeline', {'id': pipeline_id})

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result


def create(client, params):
    return client.call_hub_api('create_pipeline', params)

def update(client, params):
    return client.call_hub_api('update_pipeline', params)
