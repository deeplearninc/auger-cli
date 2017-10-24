# -*- coding: utf-8 -*-

from auger_cli.cli import pass_client
from auger_cli.utils import print_formatted_list, print_formatted_object
import click
from coreapi.transports import HTTPTransport
from coreapi.transports import http as coreapi_http
import webbrowser


attributes = [
    'id',
    'name',
    'attached',
    'status',
    'cluster_id',
    'created_at'
]


@click.group(
    'apps',
    invoke_without_command=True,
    short_help='Manage Auger Apps.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        apps = ctx.obj.client.action(
            ctx.obj.document,
            ['apps', 'list']
        )
        print_formatted_list(
            list_data=apps['data'],
            attributes=attributes
        )
    else:
        pass


@click.command(short_help='Create a new Auger app.')
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
    help='Optional cluster the app will be deployed to.'
)
@click.option(
    '--organization-id',
    '-o',
    type=click.INT,
    required=True,
    help='Organization for the app.'
)
@pass_client
def create(ctx, app, cluster_id, organization_id):
    params = {
        'name': app,
        'organization_id': organization_id
    }
    if cluster_id is not None:
        params['cluster_id'] = cluster_id
    result = ctx.client.action(
        ctx.document,
        ['apps', 'create'],
        params=params
    )
    print_formatted_object(result['data'], attributes)


@click.command(
    short_help='Delete an app from Auger Hub. This cannot be undone.'
)
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app to delete.'
)
@pass_client
def delete(ctx, app):
    ctx.client.action(
        ctx.document,
        ['apps', 'delete'],
        params={'name': app}
    )
    click.echo('Deleted {}.'.format(app))


@click.command(short_help='Deploy an app to a cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app to deploy.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the app will be deployed to.'
)
@pass_client
def deploy(ctx, app, cluster_id):
    definition = ''
    with open('.docker/service.yml') as f:
        definition = f.read()

    result = ctx.client.action(
        ctx.document,
        ['apps', 'deploy'],
        params={
            'name': app,
            'cluster_id': cluster_id,
            'definition': definition
        }
    )
    print_formatted_object(result['data'], attributes)


@click.command(short_help='Display app logs.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app.'
)
@click.option(
    '--tail',
    '-t',
    type=click.BOOL,
    is_flag=True,
    help='Stream logs to console.'
)
@pass_client
def logs(ctx, app, tail):
    if tail:
        params = {
            'name': app
        }
        _stream_logs(ctx, params)
    else:
        result = ctx.client.action(
            ctx.document,
            ['apps', 'logs'],
            params={
                'name': app
            }
        )
        click.echo(result)


@click.command(short_help='Open application in a browser.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    help='Name of application to open.'
)
@pass_client
def open_app(ctx, app):
    apps = ctx.client.action(
        ctx.document,
        ['apps', 'list']
    )
    for _, app_data in iter(apps.items()):
        print(app_data[0])
        if app_data[0]['name'] == app:
            app_url = app_data[0]['url']
            return webbrowser.open_new_tab(app_url)


@click.command(short_help='Undeploy an app from the cluster.')
@click.option(
    '--app',
    '-a',
    type=click.STRING,
    required=True,
    help='Name of the app to undeploy.'
)
@pass_client
def undeploy(ctx, app):
    ctx.client.action(
        ctx.document,
        ['apps', 'undeploy'],
        params={'name': app}
    )
    click.echo('Undeployed {}.'.format(app))


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

    def flatten(list):
        return [item for sublist in list for item in sublist]

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
cli.add_command(deploy)
cli.add_command(logs)
cli.add_command(open_app, name='open')
cli.add_command(undeploy)
