# -*- coding: utf-8 -*-

from .constants import COREAPI_SCHEMA_PATH, DEFAULT_COREAPI_URL
from contextlib import contextmanager
import coreapi
import coreapi_cli.main as coreapi_cli
from coreapi.codecs import JSONCodec, TextCodec
from coreapi.compat import force_bytes
from openapi_codec import OpenAPICodec
import json
import os
import shutil

from .config import AugerConfig


class AugerClient(object):

    def __init__(self, url=DEFAULT_COREAPI_URL):
        self._cached_document = None
        self.setup_client(url)

    def clear_credentials(self):
        shutil.rmtree(self.coreapi_cli.config_path)
        os.makedirs(self.coreapi_cli.config_path)

    @property
    def document(self):
        """Load the schema from cache if available."""
        if not self.credentials:
            raise Exception('Please login to Auger and try again.')

        if not self._cached_document:
            self._cached_document = self.coreapi_cli.get_document()
            if self._cached_document is None:
                self.fetch_document(url=self.coreapi_schema_url)
        return self._cached_document

    def call_hub_api_ex(self, keys, params=None, validate=True, overrides=None,
                        action=None, encoding=None, transform=None):
        return self.client.action(self.document, keys, params, validate, overrides,
                                  action, encoding, transform)

    def call_hub_api(self, keys, params=None, validate=True, overrides=None,
                     action=None, encoding=None, transform=None):
        result = self.call_hub_api_ex(keys, params, validate, overrides,
                                      action, encoding, transform)
        if 'data' in result:
            return result['data']

        raise Exception("Call of HUB API method %s failed." % keys)

    def print_exception(self, exc):
        # TODO: support dev mode and print stacktrace
        if self.config.is_dev_mode():
            raise exc
        else:
            self.print_line(str(exc), err=True)

    def print_line(self, line='', nl=True, err=False):
        from .formatter import print_line as formatter_print_line

        # TODO: add some filtration
        formatter_print_line(line, nl, err)

    def get_credentials(self):
        return self.coreapi_cli.get_credentials()

    def fetch_document(self, url):
        self._cached_document = self.client.get(url, format='openapi')
        self.coreapi_cli.set_document(self._cached_document)

    def setup_client(self, url):
        self.coreapi_url = url
        self.coreapi_schema_url = self.coreapi_url + COREAPI_SCHEMA_PATH

        coreapi_cli.setup_paths()
        self.coreapi_cli = coreapi_cli

        self.credentials = self.coreapi_cli.get_credentials()
        self.headers = self.coreapi_cli.get_headers()

        self.config = AugerConfig()

        def test_callback(res):
            # pass
            print(res.url)

        self.transports = coreapi.transports.HTTPTransport(
            credentials=self.credentials,
            headers=self.headers,
            request_callback=test_callback
        )
        self.decoders = [OpenAPICodec(), JSONCodec(), TextCodec()]
        self.client = coreapi.Client(
            decoders=self.decoders,
            transports=[self.transports]
        )

    def set_credentials(self, credentials):
        with open(self.coreapi_cli.credentials_path, 'wb') as store:
            store.write(force_bytes(json.dumps(credentials)))
