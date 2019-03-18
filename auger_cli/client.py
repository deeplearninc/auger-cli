# -*- coding: utf-8 -*-

from contextlib import contextmanager
from auger.hub_api_client import HubApiClient
import os
import shutil

from .config import AugerConfig


class AugerClient(object):

    def __init__(self, config=None, url=None):
        self.config = config
        if self.config is None:
            self.config = AugerConfig()

        self.setup_client(url)

    def clear_credentials(self):
        self.config.clear_api_token()

    def call_hub_api_ex(self, method, params={}):
        params = params.copy()

        self.print_debug("API call: {}({})".format(method, params))
        if params.get('id') and not method.startswith('create_'):
            id = params['id']
            del params['id']
            return getattr(self.client, method)(id, **params)
        else:
            return getattr(self.client, method)(**params)

    def call_hub_api(self, method, params={}):
        result = self.call_hub_api_ex(method, params)

        if 'data' in result:
            return result['data']

        raise Exception("Call of HUB API method %s failed." % keys)

    def print_exception(self, exc):
        # TODO: support dev mode and print stacktrace
        if self.config.is_dev_mode():
            raise exc
        else:
            self.print_line(str(exc), err=True)

    def print_debug(self, line):        
        if self.config.is_dev_mode():
            self.print_line(line)

    def print_line(self, line='', nl=True, err=False):
        from .formatter import print_line as formatter_print_line

        # TODO: add some filtration
        formatter_print_line(line, nl, err)

    def setup_client(self, url, token=None, username=None):
        if url:
            self.config.set_api_url(url)

        if token:
            self.config.set_api_token(token)

        if username:
            self.config.set_api_username(username)

        self.client = HubApiClient(
            hub_app_url=self.config.get_api_url(),
            token=self.config.get_api_token()
        )
