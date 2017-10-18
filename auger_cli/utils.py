# -*- coding: utf-8 -*-

import click
import collections


def camelize(snake_cased_string):
    parts = snake_cased_string.split('_')
    return " ".join((x.upper() if len(x) < 4 else x.title()) for x in parts)


def print_formatted_list(list_data, attributes):
    for object_data in iter(list_data):
        print_formatted_object(object_data, attributes)


def print_formatted_object(object_data, attributes):
    click.echo('=======')
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            '{name:<{width}}: {value}'.format(
                name=camelize(attrib),
                width=width,
                value=string_for_attrib(object_data[attrib])
            )
        )
    click.echo()


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
