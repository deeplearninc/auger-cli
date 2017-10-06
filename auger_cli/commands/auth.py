# -*- coding: utf-8 -*-

from auger_cli import constants
from auger_cli.cli import pass_client
from auger_cli.client import Client
from coreapi.compat import b64encode
import click
import sys


if sys.version_info[0] < 3:
    from urlparse import urlparse
    input = raw_input
else:
    from urllib.parse import urlparse


@click.group('auth', short_help='Authentication with Auger.')
@pass_client
def cli(ctx):
    pass


@click.command(short_help='Login to auger.')
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
def login(ctx, debug, url, username, password):
    # clear existing credentials
    if ctx.obj is not None:
        ctx.obj.clear()

    # extract host name from server URL
    parsed = urlparse(url)
    host = parsed.hostname
    creds_string = "{0}:{1}".format(username, password)
    header = 'Basic ' + b64encode(creds_string)

    # reload client
    credentials = {}
    credentials[host] = header
    ctx.obj = Client(url)
    ctx.obj.set_credentials(credentials)
    ctx.obj.setup_client()

    with ctx.obj.coreapi_action():
        ctx.obj.client.action(
            ctx.obj.document,
            ['organizations', 'list']
        )

        print(
            "You are now logged in on {0} as {1}.".format(
                host, username
            )
        )

        if debug:
            print(ctx.obj.document)


@click.command(short_help='Logout from Auger.')
@click.pass_context
def logout(ctx):
    ctx.obj.clear()
    click.echo('You are now logged out.')


cli.add_command(login)
cli.add_command(logout)
