# -*- coding: utf-8 -*-

import click
from contextlib import contextmanager
import auger_cli.constants as constants
import coreapi
import coreapi_cli.main as coreapi_cli
from coreapi.codecs import JSONCodec
from openapi_codec import OpenAPICodec
import logging
import os
import shutil
import sys
import subprocess
log = logging.getLogger("auger")


CONTEXT_SETTINGS = dict(auto_envvar_prefix='AUGER')


class AugerClient(object):
    _cached_document = None

    def __init__(self, url=constants.DEFAULT_COREAPI_URL):
        self.app_name = self._get_app_from_repo()
        self.coreapi_url = url
        self.coreapi_schema_url = self.coreapi_url + \
            constants.COREAPI_SCHEMA_PATH
        coreapi_cli.setup_paths()
        self.credentials = coreapi_cli.get_credentials()
        self.headers = coreapi_cli.get_headers()
        self.transports = coreapi.transports.HTTPTransport(
            credentials=self.credentials,
            headers=self.headers,
        )
        self.decoders = [OpenAPICodec(), JSONCodec()]
        self.client = coreapi.Client(
            decoders=self.decoders,
            transports=[self.transports]
        )

    def clear(self):
        shutil.rmtree(coreapi_cli.config_path)
        os.makedirs(coreapi_cli.config_path)

    @property
    def document(self):
        """Load the schema from cache if available."""

        if not self._cached_document:
            doc = coreapi_cli.get_document()
            if doc is None:
                self._cached_document = self.client.get(
                    self.coreapi_schema_url,
                    format='openapi'
                )
                coreapi_cli.set_document(self._cached_document)
            else:
                self._cached_document = doc
        return self._cached_document

    @contextmanager
    def coreapi_action(self):
        try:
            yield
        except coreapi.exceptions.ErrorMessage as exc:
            click.echo(exc.error)
            sys.exit(1)
        except coreapi.exceptions.LinkLookupError as exc:
            click.echo(exc.error)
            sys.exit(1)
        except coreapi.exceptions.ParseError as exc:
            click.echo('Error connecting to {0}'.format(self.coreapi_url))
            sys.exit(1)

    def call(self, command, show_stdout=False):
        res = subprocess.Popen(
            command,
            env=os.environ.copy(),
            cwd=os.path.curdir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        output, errors = res.communicate()
        if show_stdout:
            return output.decode().strip()
        else:
            return ''

    def log(self, msg, *args, **kwargs):
        log.info(msg, *args, **kwargs)

    @staticmethod
    def setup_logger(format='%(asctime)s %(name)s | %(message)s'):
        logging.basicConfig(
            stream=sys.stdout,
            datefmt='%H:%M:%S',
            format=format,
            level=logging.DEBUG
        )

    def _get_app_from_repo(self):
        repo_name = self.call(
            ['git', 'config', '--get', 'remote.deis.url'],
            show_stdout=True
        )
        basename = os.path.basename(repo_name)
        return os.path.splitext(basename)[0] if basename is not None else ''


pass_client = click.make_pass_decorator(AugerClient, ensure=True)


class AugerCLI(click.MultiCommand):
    cmd_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), 'commands')
    )

    def list_commands(self, ctx):
        rv = []
        for filename in os.listdir(AugerCLI.cmd_folder):
            if filename.endswith('.py') and not filename.startswith('__'):
                rv.append(filename[:-3])
        rv.sort()
        return rv

    def get_command(self, ctx, name):
        try:
            if sys.version_info[0] == 2:
                name = name.encode('ascii', 'replace')
            mod = __import__(
                'auger_cli.commands.' + name, None, None, ['cli']
            )
        except ImportError as e:
            print(name)
            print(str(e))
            return
        return mod.cli


@click.command('auger', cls=AugerCLI, context_settings=CONTEXT_SETTINGS)
@pass_client
def cli(ctx):
    """Auger command line interface."""
