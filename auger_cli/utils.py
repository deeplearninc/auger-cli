# -*- coding: utf-8 -*-

import click
import collections
from .constants import API_POLL_INTERVAL
import time
import sys


def camelize(snake_cased_string):
    parts = snake_cased_string.split('_')
    return " ".join((x.upper() if len(x) < 4 else x.title()) for x in parts)


def print_line(line, nl=True):
    click.echo(line, nl=nl)


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


def urlparse(*args, **kwargs):
    if sys.version_info[0] < 3:
        from urlparse import urlparse
        input = raw_input
    else:
        from urllib.parse import urlparse
    return urlparse(*args, **kwargs)


def clusters_command_progress_bar(
        ctx, cluster_id, first_status, in_progress_statuses, desired_status):
    status = first_status
    last_status = ''
    while status in in_progress_statuses:
        if status != last_status:
            click.echo('\n{}...'.format(camelize(status), nl=False))
            last_status = status
        click.echo('.', nl=False)
        time.sleep(API_POLL_INTERVAL)
        status = ctx.client.action(
            ctx.document,
            ['clusters', 'read'],
            params={
                'id': cluster_id
            }
        )['data']['status']
    click.echo('\n{}.'.format(camelize(status)))
    return status == desired_status


def projects_command_progress_bar(
        ctx, name, first_status, in_progress_statuses, desired_status):
    status = first_status
    last_status = ''
    while status in in_progress_statuses:
        if status != last_status:
            click.echo('{}...'.format(camelize(status), nl=False))
            last_status = status
        click.echo('.', nl=False)
        time.sleep(API_POLL_INTERVAL)
        project = ctx.client.action(
            ctx.document,
            ['projects', 'read'],
            params={
                'name': name
            }
        )['data']
        status = project['status']
    click.echo('\n{}.'.format(camelize(status)))
    return status == desired_status
