# -*- coding: utf-8 -*-

import sys
import uuid
import os
import subprocess
import base64
import time

from .constants import REQUEST_LIMIT, API_POLL_INTERVAL

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


def b64encode(input_string):
    return base64.b64encode(input_string.encode('ascii')).decode('ascii')


def b64decode(input_string):
    return base64.b64decode(input_string).decode('ascii')


def wait_for_object_state(client, endpoint, params, first_status,
                  progress_statuses, poll_interval=API_POLL_INTERVAL):
    from .formatter import progress_spinner

    status = first_status
    last_status = ''
    result = {}
    while status in progress_statuses:
        if status != last_status:
            client.print_line('{}... '.format(camelize(status)))
            last_status = status

        with progress_spinner(client):
            while status == last_status:
                time.sleep(poll_interval)

                result = client.call_hub_api(endpoint, params=params)
                status = result.get('status', 'failure')

    client.print_line('{}... '.format(camelize(status)))
    if status == "failure" or status == 'error':
        raise Exception('API call {}({}) failed: {}'.format(result.get(
            'name', ""), result.get('args', ""), result.get("exception", "")))

    return result


def request_list(client, what, params):
    offset = params.get('offset', 0)
    limit = params.get('limit', REQUEST_LIMIT)
    p = params.copy()
    while limit > 0:
        p['offset'] = offset
        p['limit'] = limit
        response = client.call_hub_api_ex([what, 'list'], params=p)
        if not 'data' in response or not 'meta' in response:
            raise Exception("Read list of %s failed."%what)

        # print(response['meta'])
        # print(response['data'][0].keys())

        for item in response['data']:
            yield item

        received = len(response['data'])
        offset += received
        limit -= received
        if offset >= response['meta']['pagination']['total']:
            break


def get_uid():
    return uuid.uuid4().hex[:15].upper()


def download_remote_file(local_path, remote_path):
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


def save_dict_to_csv(data, predict_path):
    import pandas as pd

    df_predict = pd.DataFrame.from_dict(data)
    df_predict.to_csv(predict_path, index=False, encoding='utf-8')


def load_dataframe_from_file(path, features=None, nrows=None):
    import pandas as pd

    extension = path
    data_compression = 'infer'

    csv_with_header = True
    header = 0 if csv_with_header else None
    prefix = None if csv_with_header else 'c'

    try:
        return pd.read_csv(
            path,
            encoding='utf-8',
            escapechar="\\",
            usecols=features,
            na_values=['?'],
            header=header,
            prefix=prefix,
            sep=',',
            nrows=nrows,
            low_memory=False,
            compression=data_compression
        )
    except Exception as e:
        return pd.read_csv(
            path,
            encoding='utf-8',
            escapechar="\\",
            usecols=features,
            na_values=['?'],
            header=header,
            prefix=prefix,
            sep='|',
            nrows=nrows,
            low_memory=False,
            compression=data_compression
        )
