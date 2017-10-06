# -*- coding: utf-8 -*-

import collections


def camelize(snake_cased_string):
    parts = snake_cased_string.split('_')
    return " ".join((x.upper() if len(x) < 4 else x.title()) for x in parts)


def string_for_attrib(attrib):
    if type(attrib) in (int, str):
        return attrib
    elif type(attrib) is list:
        return attrib.join(',')
    if isinstance(attrib, collections.OrderedDict):
        return ' - '.join(
            [v for k, v in attrib.items() if k != 'object']
        )
    else:
        return attrib
