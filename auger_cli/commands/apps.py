# -*- coding: utf-8 -*-

from auger_cli.cli import camelize, pass_client
import click
from coreapi.transports import HTTPTransport
from coreapi.transports import http as coreapi_http


@click.group(
    'apps',
    invoke_without_command=True,
    short_help='Manage Auger Apps.'
)
@click.option(
    'cluster_id',
    '-c',
    type=click.INT
)
@click.pass_context
def cli(ctx, cluster_id):
    if ctx.invoked_subcommand is None and cluster_id is not None:
        apps = ctx.obj.client.action(
            ctx.obj.document,
            ['apps', 'list'],
            params={
                'cluster_id': cluster_id
            }
        )
        for app in iter(apps['data']):
            _print_app(app)
    elif ctx.invoked_subcommand is None:
        click.echo('Please specify a --cluster-id or see details with --help.')
    else:
        pass


@click.command(short_help='Attach an app to a cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app to create.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the app will be deployed to.'
)
@pass_client
def create(ctx, app, cluster_id):
    result = ctx.client.action(
        ctx.document,
        ['apps', 'create'],
        params={
            'id': app,
            'cluster_id': cluster_id
        }
    )
    ip_address = ctx.client.action(
        ctx.document,
        ['clusters', 'read'],
        params={
            'id': cluster_id
        }
    )['data']['ip_address']
    ctx.setup_app_repo(app, ip_address)
    _print_app(result['data'])


@click.command(short_help='Delete an app from the cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app to delete.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the app will be deleted from.'
)
@pass_client
def delete(ctx, app, cluster_id):
    ctx.client.action(
        ctx.document,
        ['apps', 'delete'],
        params={
            'id': app,
            'cluster_id': cluster_id
        }
    )
    click.echo('Deleted {}.'.format(app))


@click.command(short_help='Display app logs.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.STRING,
    required=True,
    help='Cluster for the app.'
)
@click.option(
    '--tail',
    '-t',
    type=click.BOOL,
    is_flag=True,
    help='Stream logs to console.'
)
@pass_client
def logs(ctx, app, cluster_id, tail):
    if tail:
        params = {
            'id': app,
            'cluster_id': cluster_id
        }
        _stream_logs(ctx, params)
    else:
        result = ctx.client.action(
            ctx.document,
            ['apps', 'logs'],
            params={
                'id': app,
                'cluster_id': cluster_id
            }
        )
        click.echo(result)


@click.command(short_help='Display app details.')
@click.argument('id')
@pass_client
def show(ctx, id):
    app = ctx.client.action(
        ctx.document,
        ['apps', 'read'],
        params={
            'id': id
        }
    )
    _print_app(app['data'])


def _print_app(app_dict):
    attributes = [
        'id',
        'url',
        'created_at'
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                camelize(attrib),
                app_dict[attrib],
                width=width
            )
        )
    click.echo()


def _stream_logs(ctx, params):
    # Patch HTTPTransport to handle streaming responses
    def stream_request(self, link, decoders,
                       params=None, link_ancestors=None, force_codec=False):
        session = self._session
        method = coreapi_http._get_method(link.action)
        encoding = coreapi_http._get_encoding(link.encoding)
        params = coreapi_http._get_params(
            method, encoding, link.fields, params
        )
        url = coreapi_http._get_url(link.url, params.path)
        headers = coreapi_http._get_headers(url, decoders, self.credentials)
        headers.update(self.headers)

        request = coreapi_http._build_http_request(
            session, url, method, headers, encoding, params
        )

        with session.send(request, stream=True) as response:
            print(response)
            for line in response.iter_lines():
                line = line.decode('utf-8')
                if line != 'ping':
                    print(line)

    HTTPTransport.stream_request = stream_request
    # Patch done

    doc = ctx.document

    def flatten(list): return [item for sublist in list for item in sublist]
    links = flatten(
        list(map(lambda link: list(link._data.values()), doc.data.values()))
    )
    link = list(filter(lambda link: 'stream_logs' in link.url, links))[0]
    credentials = ctx.credentials
    headers = ctx.headers
    decoders = ctx.decoders

    http_transport = HTTPTransport(credentials=credentials, headers=headers)
    http_transport.stream_request(link, decoders, params=params)


cli.add_command(create)
cli.add_command(delete)
cli.add_command(logs)
cli.add_command(show)
