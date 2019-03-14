# -*- coding: utf-8 -*-

from auger_cli.utils import request_list, wait_for_object_state

display_attributes = [
    'id', 'status'
]


def read(client, prediction_id, attributes=None):
    result = client.call_hub_api('get_prediction', {'id': prediction_id})

    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

def create(client, pipeline_id, records, features, wait=True):
    params={
        'pipeline_id': pipeline_id,
        'records': records,
        'features': features
    }
    prediction = client.call_hub_api('create_prediction', {'payload': params})

    if wait:
        wait_for_object_state(client,
            method='get_prediction',
            params={'id': prediction['id']},
            first_status=prediction['status'],
            progress_statuses=[
                'requested', 'running'
            ]
        )

    return prediction['id']

