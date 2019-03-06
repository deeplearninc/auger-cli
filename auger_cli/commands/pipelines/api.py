# -*- coding: utf-8 -*-

from ...formatter import print_line, print_record
from ...utils import request_list
from ...constants import REQUEST_LIMIT


pipeline_attributes = ['id', 'status', 'lambda_package_s3_path', 'datasource_manifest_name', 'error_message' 'project_id', 'organization_id', 'trial']


def list_pipelines(ctx, organization_id, experiment_id, active):
    params = {}
    if organization_id:
        params['organization_id'] = organization_id
    if experiment_id:
        params['experiment_id'] = experiment_id
    if active:
        params['active'] = active

    with ctx.coreapi_action():
        return request_list(
            ctx,
            'pipelines',
            params=params
        )


def read_pipeline(auger_client, pipeline_id, attributes=None):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['pipelines', 'read'],
            params={'id': pipeline_id}
        )['data']
        #print(result.keys())

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    #print(attributes)    
    return result
