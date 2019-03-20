# -*- coding: utf-8 -*-

import click
import click_spinner
import collections
import types
from contextlib import contextmanager

from .utils import camelize


@contextmanager
def progress_spinner(client):
    with click_spinner.spinner():
        yield


def print_plain_list(list_data):
    for object_data in iter(list_data):
        print_line(object_data)


def print_list(list_data, attributes):
    for object_data in iter(list_data):
        print_record(object_data, attributes)


def print_record(object_data, attributes=None, max_level=10):
    #print(object_data.keys())
    if attributes is None:
        attributes = object_data.keys()

    print_line('=======')
    width = len(max(attributes, key=len)) + 2
    for attrib in attributes:
        print_line(
            '{name:<{width}} {value}'.format(
                name=camelize(attrib) + ':',
                width=width,
                value=string_for_attrib(object_data.get(attrib), 0, max_level)
            )
        )
    print_line()


def print_line(line='', nl=True, err=False):
    click.echo(line, nl=nl, err=err)


def print_stream(client, params):
    doc = client.document

    def flatten(list):
        return [item for sublist in list for item in sublist]

    links = flatten(
        list(map(lambda link: list(link._data.values()), doc.data.values()))
    )
    link = list(filter(lambda link: 'stream_logs' in link.url, links))[0]
    # TODO: fix streaming (it's better to use websockets)
    # credentials = client.credentials
    # headers = client.headers
    # decoders = client.decoders

    # http_transport = HTTPTransport(credentials=credentials, headers=headers)
    # http_transport.stream_request(link, decoders, params=params)


def string_for_attrib(attrib, cur_level, max_level):
    if type(attrib) in (int, str) or cur_level>=max_level:
        return attrib

    if isinstance(attrib, collections.OrderedDict) or isinstance(attrib, dict):
        items = []
        for k, v in attrib.items():
            if type(k) == str and k != 'object':
                if isinstance(v, collections.OrderedDict) or isinstance(v, dict):
                    items.append('\n  {}: {}'.format(
                        camelize(k), string_for_attrib(v, cur_level+1, max_level)))
                else:
                    items.append('\n  {}: {}'.format(camelize(k), v))

        return ' '.join(items)
    else:
        return attrib


def print_header(myDict):
    header = ""
    for key, value in myDict.items():
        header += "{}:{}, ".format(key, value)

    print_line(header)


def print_table(myDict, attributes=None):
    if isinstance(myDict, types.GeneratorType):
        myDict = list(myDict)

    if myDict is None or len(myDict) == 0:
        return

    colList = attributes
    if not colList:
        colList = list(myDict[0].keys() if myDict else [])
    myList = [colList]  # 1st row = header
    for item in myDict:
        myList.append([str(item[col] or '') for col in colList])
    # maximun size of the col for each element
    colSize = [max(map(len, col)) for col in zip(*myList)]
    # insert seperating line before every line, and extra one for ending.
    for i in range(0, len(myList) + 1)[::-1]:
        myList.insert(i, ['-' * i for i in colSize])
    # two format for each content line and each seperating line
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    formatSep = '-+-'.join(["{{:<{}}}".format(i) for i in colSize])
    for item in myList:
        if item[0][0] == '-':
            print(formatSep.format(*item))
        else:
            print(formatStr.format(*item))
