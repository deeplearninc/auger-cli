# -*- coding: utf-8 -*-

import click

from ...cli import pass_client
from ...formatter import print_line


@click.command('schema', short_help='Display current Auger schema.')
@pass_client
def schema_group(client):
    with client.cli_error_handler():
        client.fetch_document(url=client.document.url)
        client.print_line(client.document)
