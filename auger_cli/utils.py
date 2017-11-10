# -*- coding: utf-8 -*-

import click
import collections
import time


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

def clusters_command_progress_bar(ctx, cluster_id, first_status, in_progress_statuses, desired_status):
    status = first_status
    last_status = ''
    while status in in_progress_statuses:
        if status != last_status:
            click.echo('\n%s..' % status, nl=False)
            last_status = status
        click.echo('.', nl=False)
        time.sleep(1)
        status = ctx.client.action(
            ctx.document,
            ['clusters', 'read'],
            params={
                'id': cluster_id
            }
        )['data']['status']
    click.echo()
    click.echo(status)
    return status == desired_status

def apps_command_progress_bar(ctx, app_id, first_status, in_progress_statuses, desired_status):
    status = first_status
    last_status = ''
    while status in in_progress_statuses:
        if status != last_status:
            click.echo('\n%s..' % status, nl=False)
            last_status = status
        click.echo('.', nl=False)
        time.sleep(1)
        apps = ctx.client.action(
            ctx.document,
            ['apps', 'list']
        )['data']
        app = None
        for a in apps:
            if a['id'] == app_id:
                app = a
                break
        status = app['status']
    click.echo()
    click.echo(status)
    return status == desired_status
