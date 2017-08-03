# -*- coding: utf-8 -*-

from auger_cli import constants
from auger_cli.cli import AugerClient
from coreapi.compat import b64encode
import click
import coreapi_cli.main as coreapi_cli
import sys

if sys.version_info[0] < 3:
    from urlparse import urlparse
    input = raw_input
else:
    from urllib.parse import urlparse


@click.command('login', short_help='Login to auger.')
@click.option('--debug', is_flag=True, help='Show extra environment info.')
@click.option(
    '--username',
    '-u',
    default=None,
    prompt='username',
    type=click.STRING,
    help='Auger username.'
)
@click.password_option(
    '--password',
    '-p',
    prompt='password',
    confirmation_prompt=False,
    help='Auger password.'
)
@click.option('--url',
              default=constants.DEFAULT_COREAPI_URL,
              type=click.STRING,
              help='Auger API endpoint.')
@click.pass_context
def cli(ctx, debug, url, username, password):
    # clear existing credentials
    ctx.obj.clear()

    # extract host name from server URL
    parsed = urlparse(url)
    host = parsed.hostname
    creds_string = "{0}:{1}".format(username, password)
    header = 'Basic ' + b64encode(creds_string)

    # reload client
    credentials = coreapi_cli.get_credentials()
    credentials[host] = header
    coreapi_cli.set_credentials(credentials)
    ctx.obj = AugerClient(url)

    with ctx.obj.coreapi_action():
        ctx.obj.client.action(
            ctx.obj.document,
            ['organizations', 'list']
        )

        print(
            "You are now logged in on {0} as {1}".format(
                host, username
            )
        )

        if debug:
            print(ctx.obj.document)
