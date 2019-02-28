# -*- coding: utf-8 -*-
import os
import click

from ...formatter import print_line, print_record
from ...utils import request_list

experiment_session_attributes = ['id', 'project_id', 'experiment_id', 'status']


def list_experiment_sessions(ctx, project_id, experiment_id):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'experiment_sessions',
            params={'limit': 1000000000, 'project_id': project_id, 'experiment_id': experiment_id}
        )


def read_experiment_session(auger_client, experiment_session_id):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['experiment_sessions', 'read'],
            params={'id': experiment_session_id}
        )['data']
    return result

