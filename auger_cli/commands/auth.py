# -*- coding: utf-8 -*-

import base64
import click

from .. import constants
from ..client import pass_client, Client
from ..formatter import print_line
from ..utils import urlparse
from coreapi.compat import b64encode


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
    print_line('You are now logged out.')


@click.command(short_help='Display the current logged in user.')
@click.pass_context
def whoami(ctx):
    creds = ctx.obj.get_credentials()
    for host, cred in creds.items():
        decoded = base64.b64decode(cred.split(' ')[1]).decode('utf8')
        username = decoded.split(':')[0]
        print_line('{} on {}'.format(username, host))


cli.add_command(login)
cli.add_command(logout)
cli.add_command(whoami)
