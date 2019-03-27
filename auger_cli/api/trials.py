# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list


display_attributes = ['id', 'score_name', 'score_value', 'task_type', 'algorithm_name', 'algorithm_params']


def list(client, experiment_session_id):
    return request_list(client, 'trials', params={'experiment_session_id': experiment_session_id})

def read(client, trial_id, experiment_session_id):
    if experiment_session_id is None:
        experiment_session_id = client.config.get_experiment_session_id()

    trial = client.call_hub_api('get_trial', {
      'id': trial_id,
      'experiment_session_id': experiment_session_id
    })

    trial['algorithm_name'] = trial['hyperparameter']['algorithm_name']
    trial['algorithm_params'] = trial['hyperparameter']['algorithm_params']

    return trial
