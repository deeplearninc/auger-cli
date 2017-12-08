# -*- coding: utf-8 -*-

from .constants import COREAPI_SCHEMA_PATH, DEFAULT_COREAPI_URL
from contextlib import contextmanager
import coreapi
import coreapi_cli.main as coreapi_cli
from coreapi.codecs import JSONCodec, TextCodec
from coreapi.compat import force_bytes
from .formatter import print_line
from openapi_codec import OpenAPICodec
import json
import os
import shutil
import sys
import click


def init_coreapi_cli():
    coreapi_cli.setup_paths()
    return coreapi_cli


class Client(object):
    _cached_document = None

    def __init__(self, url=DEFAULT_COREAPI_URL):
        self.coreapi_url = url
        self.coreapi_schema_url = self.coreapi_url + COREAPI_SCHEMA_PATH
        self.coreapi_cli = init_coreapi_cli()
        self.setup_client()

    def clear(self):
        shutil.rmtree(self.coreapi_cli.config_path)
        os.makedirs(self.coreapi_cli.config_path)

    @property
    def document(self):
        """Load the schema from cache if available."""
        if not self.credentials:
            print_line('Please login to Auger and try again.')
            sys.exit(1)

        if not self._cached_document:
            self._cached_document = self.coreapi_cli.get_document()
            if self._cached_document is None:
                self.fetch_document(url=self.coreapi_schema_url)
        return self._cached_document

    @contextmanager
    def coreapi_action(self):
        try:
            yield
        except coreapi.exceptions.ErrorMessage as exc:
            print_line(exc)
            sys.exit(1)
        except coreapi.exceptions.LinkLookupError as exc:
            print_line(exc)
            sys.exit(1)
        except coreapi.exceptions.ParseError as exc:
            print_line('Error connecting to {0}'.format(self.coreapi_url))
            sys.exit(1)

    def get_credentials(self):
        return self.coreapi_cli.get_credentials()

    def fetch_document(self, url):
        self._cached_document = self.client.get(url, format='openapi')
        self.coreapi_cli.set_document(self._cached_document)

    def setup_client(self):
        self.credentials = self.coreapi_cli.get_credentials()
        self.headers = self.coreapi_cli.get_headers()
        self.transports = coreapi.transports.HTTPTransport(
            credentials=self.credentials,
            headers=self.headers,
        )
        self.decoders = [OpenAPICodec(), JSONCodec(), TextCodec()]
        self.client = coreapi.Client(
            decoders=self.decoders,
            transports=[self.transports]
        )

    def set_credentials(self, credentials):
        with open(self.coreapi_cli.credentials_path, 'wb') as store:
            store.write(force_bytes(json.dumps(credentials)))


pass_client = click.make_pass_decorator(Client, ensure=True)
