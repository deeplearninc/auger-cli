# -*- coding: utf-8 -*-

import click

from ... import constants
from ...cli import pass_client
from .api import auth_login, auth_whoami, auth_logout

@click.group('auth', short_help='Authentication with Auger.')
@click.pass_context
def auth_group(ctx):
    pass


@click.command(short_help='Login to Auger.')
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
@pass_client
def login(client, url, username, password):
    with client.cli_error_handler():
        auth_login(client, url, username, password)

        client.print_line(
            "You are now logged in on {0} as {1}.".format(
                client.coreapi_url, username
            )
        )


@click.command(short_help='Logout from Auger.')
@pass_client
def logout(client):
    with client.cli_error_handler():
        auth_logout(client)
        client.print_line('You are now logged out.')


@click.command(short_help='Display the current logged in user.')
@pass_client
def whoami(client):
    with client.cli_error_handler():
        username, host = auth_whoami(client)
        if username and host:
            client.print_line('{} on {}'.format(username, host))
        else:
            client.print_line("You are not logged in.")


auth_group.add_command(login)
auth_group.add_command(logout)
auth_group.add_command(whoami)
