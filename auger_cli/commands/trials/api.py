# -*- coding: utf-8 -*-
import os
import click

from ...formatter import print_line, print_record
from ...utils import request_list

trial_attributes = ['id', 'score_name', 'score_value', 'task_type', 'hyperparameter']


def list_trials(ctx, experiment_session_id):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'trials',
            params={'limit': 1000000000, 'experiment_session_id': experiment_session_id}
        )

def list_all_trials(auger_client, experiment_session_id):
    result = []
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['trials', 'list'],
            params={'experiment_session_id': experiment_session_id, 'limit': 1000000000}
        )['data']

    return result

def read_trial(auger_client, trial_id, experiment_session_id):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['trials', 'read'],
            params={'id': trial_id, 'experiment_session_id': experiment_session_id}
        )['data']
        print(result.keys())

    return result

