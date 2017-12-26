# -*- coding: utf-8 -*-

import sys


def camelize(snake_cased_string):
    parts = snake_cased_string.split('_')
    return " ".join((x.upper() if len(x) < 4 else x.title()) for x in parts)


def urlparse(*args, **kwargs):
    if sys.version_info[0] < 3:
        from urlparse import urlparse
        input = raw_input  # noqa: F841,F821
    else:
        from urllib.parse import urlparse
    return urlparse(*args, **kwargs)


def request_list(auger_client, what, params={}):
    offset = 0
    while True:
        p = {'offset': offset}
        assert 'limit' not in params
        assert 'offset' not in params
        p.update(params)
        response = auger_client.client.action(
            auger_client.document,
            [what, 'list'],
            params=p
        )
        for item in response['data']:
            yield item
        assert offset == int(response['meta']['pagination']['offset'])
        assert len(response['data']) == response['meta']['pagination']['count']
        offset += len(response['data'])
        if offset >= response['meta']['pagination']['total']:
            break
