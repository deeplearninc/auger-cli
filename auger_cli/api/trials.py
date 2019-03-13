# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list


display_attributes = ['id', 'score_name', 'score_value', 'task_type', 'hyperparameter']


def list(client, experiment_session_id):
    return request_list(client, 'trials', params={'experiment_session_id': experiment_session_id})

def read(client, trial_id, experiment_session_id):
    return client.call_hub_api(['trials', 'read'], params={'id': trial_id, 'experiment_session_id': experiment_session_id})

