# -*- coding: utf-8 -*-

from coreapi.transports import HTTPTransport
from coreapi.transports import http as coreapi_http
import click
import click_spinner
import collections
import time

from .constants import API_POLL_INTERVAL
from .utils import camelize


def command_progress_bar(
        auger_client, endpoint, params, first_status,
        progress_statuses, desired_status, poll_interval=API_POLL_INTERVAL):
    status = first_status
    last_status = ''
    while status in progress_statuses:
        if status != last_status:
            print_line('{}... '.format(camelize(status)))
            last_status = status
        with click_spinner.spinner():
            while status == last_status:
                time.sleep(poll_interval)
                status = auger_client.client.action(
                    auger_client.document,
                    endpoint,
                    params=params
                )['data']['status']
    print_line('{}.'.format(camelize(desired_status)))
    return status == desired_status


def wait_for_task_result(
        auger_client, endpoint, params, first_status,
        progress_statuses, poll_interval=API_POLL_INTERVAL):
    status = first_status
    last_status = ''
    result = {}
    while status in progress_statuses:
        if status != last_status:
            print_line('{}... '.format(camelize(status)))
            last_status = status
        with click_spinner.spinner():
            while status == last_status:
                time.sleep(poll_interval)
                result = auger_client.client.action(
                    auger_client.document,
                    endpoint,
                    params=params
                )['data']

                status = result['status']
    
    print_line('{}... '.format(camelize(status)))
    if status == "failure":
        raise click.ClickException('API call {}({}) failed: {}'.format(result.get('name', ""), result.get('args', ""), result.get("exception", "")))

    return result.get('result')

def print_list(list_data, attributes):
    for object_data in iter(list_data):
        print_record(object_data, attributes)


def print_record(object_data, attributes):
    print_line('=======')
    width = len(max(attributes, key=len)) + 2
    for attrib in attributes:
        print_line(
            '{name:<{width}} {value}'.format(
                name=camelize(attrib) + ':',
                width=width,
                value=string_for_attrib(object_data.get(attrib))
            )
        )
    print_line()


def print_line(line='', nl=True, err=False):
    click.echo(line, nl=nl, err=err)


def print_stream(ctx, params):
    # Patch HTTPTransport to handle streaming responses
    def stream_request(self, link, decoders,
                       params=None, link_ancestors=None, force_codec=False):
        session = self._session
        method = coreapi_http._get_method(link.action)
        encoding = coreapi_http._get_encoding(link.encoding)
        params = coreapi_http._get_params(
            method, encoding, link.fields, params
        )
        url = coreapi_http._get_url(link.url, params.path)
        headers = coreapi_http._get_headers(
            url, decoders, self.credentials
        )
        headers.update(self.headers)

        request = coreapi_http._build_http_request(
            session, url, method, headers, encoding, params
        )

        with session.send(request, stream=True) as response:
            print(response)
            for line in response.iter_lines():
                line = line.decode('utf-8')
                if line != 'ping':
                    print(line)

    HTTPTransport.stream_request = stream_request
    # Patch done

    doc = ctx.document

    def flatten(list):
        return [item for sublist in list for item in sublist]

    links = flatten(
        list(map(lambda link: list(link._data.values()), doc.data.values()))
    )
    link = list(filter(lambda link: 'stream_logs' in link.url, links))[0]
    credentials = ctx.credentials
    headers = ctx.headers
    decoders = ctx.decoders

    http_transport = HTTPTransport(credentials=credentials, headers=headers)
    http_transport.stream_request(link, decoders, params=params)


def string_for_attrib(attrib):
    if type(attrib) in (int, str):
        return attrib

    if isinstance(attrib, collections.OrderedDict) or isinstance(attrib, dict):
        items = []
        for k, v in attrib.items():
            if type(k) == str and k != 'object':
                if isinstance(v, collections.OrderedDict) or isinstance(v, dict): 
                    items.append('\n  {}: {}'.format(camelize(k), string_for_attrib(v)))
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
    colList = attributes
    if not colList: 
        colList = list(myDict[0].keys() if myDict else [])
    myList = [colList] # 1st row = header
    for item in myDict: 
        myList.append([str(item[col] or '') for col in colList])
    #maximun size of the col for each element
    colSize = [max(map(len,col)) for col in zip(*myList)]
    #insert seperating line before every line, and extra one for ending. 
    for i in  range(0, len(myList)+1)[::-1]:
         myList.insert(i, ['-' * i for i in colSize])
    #two format for each content line and each seperating line
    formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    formatSep = '-+-'.join(["{{:<{}}}".format(i) for i in colSize])
    for item in myList: 
        if item[0][0] == '-':
            print(formatSep.format(*item))
        else:
            print(formatStr.format(*item))        
