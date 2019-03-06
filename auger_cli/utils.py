# -*- coding: utf-8 -*-

import sys
import uuid
import os
import subprocess

from .constants import REQUEST_LIMIT


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
    limit = params.get('limit', REQUEST_LIMIT)
    p = params.copy()
    while limit > 0:
        p['offset'] = offset
        p['limit'] = limit
        with auger_client.coreapi_action():
            response = auger_client.client.action(
                auger_client.document,
                [what, 'list'],
                params=p
            )
        #print(response['meta'])    
        print(response['data'][0].keys())

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


def get_uid():
    return uuid.uuid4().hex[:15].upper()


def download_remote_file(ctx, local_path, remote_path):
    from urllib.request import urlopen
    from urllib.parse import urlparse, parse_qs
    import shutil

    #print("Downloading file from url: %s"%remote_path)

    with urlopen(remote_path) as response:
        # print(response)
        # print(response.info())
        contentDisp = response.getheader('Content-Disposition')
        contentType = response.getheader('Content-Type')
        fileext = ''
        if contentType is not None and len(contentType) > 0:
            if contentType == 'application/x-gzip':
                fileext = '.gz'
            elif contentType == 'text/csv':
                fileext = '.csv'
            elif contentType == 'binary/octet-stream':
                fileext = '.zip'

        filename = ''
        if contentDisp is not None and len(contentDisp) > 0:
            items = contentDisp.split(';')
            for item in items:
                item = item.strip()
                if item.startswith("filename=\""):
                    filename = item[10:-1]
                    break
                elif item.startswith("filename="):
                    filename = item[9:]
                    break

        if len(filename) == 0:
            uri = urlparse(remote_path)
            params = parse_qs(uri.query)
            if len(params.get('id', [])) > 0:
                filename = params['id'][0] + fileext
            else:
                if len(uri.path) > 0 and len(os.path.basename(uri.path)) > 0:
                    filename = os.path.basename(uri.path)
                else:
                    filename = get_uid() + fileext

        local_file_path = os.path.join(local_path, filename)
        print("Download file to: %s" % local_file_path)

        create_parent_folder(local_file_path)
        #urlretrieve(remote_path, local_file_path)
        with open(local_file_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)

def create_parent_folder(path):
    parent = os.path.dirname(path)

    try:
        os.makedirs(parent)
    except OSError:
        pass

def remove_file(path, wild=False):
    try:

        if wild:
            for fl in glob.glob(path):
                os.remove(fl)
        else:
            os.remove(path)
    except OSError:
        pass

def shell_call(args, input_string='', silent=False):
    input_bytes = (input_string.strip() + '\n').encode('utf-8')
    if silent:
        return subprocess.check_call(
            args,
            input=input_bytes,
            cwd=os.path.curdir,
            env=os.environ.copy()
        )
    else:
        return subprocess.check_output(
            args,
            input=input_bytes,
            cwd=os.path.curdir,
            env=os.environ.copy(),
            shell=True,
            stderr=subprocess.STDOUT
        )
