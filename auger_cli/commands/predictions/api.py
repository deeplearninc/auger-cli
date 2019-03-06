# -*- coding: utf-8 -*-

from ...formatter import command_progress_bar, print_record, print_line, wait_for_task_result
from ...utils import request_list

prediction_attributes = [
    'id', 'status'
]


def read_prediction(auger_client, prediction_id, attributes=None):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['predictions', 'read'],
            params={'id': prediction_id}
        )['data']
    
    #print(result.keys()) 
    if attributes:
        result = {k: result[k] for k in attributes if k in result}

    return result

def create_prediction(auger_client, pipeline_id, records, features, wait=True):
    with auger_client.coreapi_action():
        params={
            'pipeline_id': pipeline_id,
            'records': records,
            'features': features
        }
        prediction = auger_client.client.action(
            auger_client.document,
            ['predictions', 'create'],
            params= {'payload': params}, encoding='application/json', validate=False
        )['data']
        print(prediction)

        if wait:
            wait_for_task_result(
                auger_client=auger_client,
                endpoint=['predictions', 'read'],
                params={'id': prediction['id']},
                first_status=prediction['status'],
                progress_statuses=[
                    'requested', 'running'
                ]
            )
            
        return prediction['id']    

