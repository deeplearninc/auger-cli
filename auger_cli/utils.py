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


def request_list(auger_client, what, params):
    offset = params.get('offset', 0)
    limit = params['limit']  # limit is mandatory key in params
    p = params.copy()
    while limit >= 0:
        p['offset'] = offset
        p['limit'] = limit
        with auger_client.coreapi_action():
            response = auger_client.client.action(
                auger_client.document,
                [what, 'list'],
                params=p
            )
        for item in response['data']:
            yield item
        assert offset == int(response['meta']['pagination']['offset'])
        received = len(response['data'])
        assert received == response['meta']['pagination']['count']
        assert received <= limit
        offset += received
        limit -= received
        if offset >= response['meta']['pagination']['total']:
            break
