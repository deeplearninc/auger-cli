# -*- coding: utf-8 -*-

from ..cli import pass_client
from ..cluster_config import ClusterConfig
from ..utils import (
    print_formatted_list,
    print_formatted_object,
    print_line
)
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
    'projects',
    invoke_without_command=True,
    short_help='Manage Auger Projects.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        projects = ctx.obj.client.action(
            ctx.obj.document,
            ['projects', 'list']
        )
        print_formatted_list(
            list_data=projects['data'],
            attributes=attributes
        )
    else:
        pass


@click.command(short_help='Create a new Auger project.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to create.'
)
@click.option(
    '--organization-id',
    '-o',
    type=click.INT,
    required=True,
    help='Organization for the project.'
)
@pass_client
def create(ctx, project, organization_id):
    params = {
        'name': project,
        'organization_id': organization_id
    }
    result = ctx.client.action(
        ctx.document,
        ['projects', 'create'],
        params=params
    )
    print_formatted_object(result['data'], attributes)


@click.command(
    short_help='Delete an project from Auger Hub. This cannot be undone.'
)
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to delete.'
)
@pass_client
def delete(ctx, project):
    ctx.client.action(
        ctx.document,
        ['projects', 'delete'],
        params={'name': project}
    )
    click.echo('Deleted {}.'.format(project))


@click.command(short_help='Deploy an project to a cluster.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to deploy.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=True,
    help='Cluster the project will be deployed to.'
)
@pass_client
def deploy(ctx, project, cluster_id):
    cluster_config = ClusterConfig(
        ctx,
        project=project,
        cluster_id=cluster_id
    )
    print_line('Setting up docker registry.')
    cluster_config.login()
    print_line('Preparing project to deploy.')
    cluster_config.docker_client.build()
    print_line('Deploying project. (This may take a few minutes.)')
    cluster_config.docker_client.push()
    definition = ''
    with open('.auger/service.yml') as f:
        definition = f.read()

    result = ctx.client.action(
        ctx.document,
        ['projects', 'deploy'],
        params={
            'name': project,
            'cluster_id': cluster_id,
            'definition': definition
        }
    )
    print_formatted_object(result['data'], attributes)
    print_line('Done.')


@click.command(short_help='Display project logs.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project.'
)
@click.option(
    '--tail',
    '-t',
    type=click.BOOL,
    is_flag=True,
    help='Stream logs to console.'
)
@pass_client
def logs(ctx, project, tail):
    if tail:
        params = {
            'name': project
        }
        _stream_logs(ctx, params)
    else:
        result = ctx.client.action(
            ctx.document,
            ['projects', 'logs'],
            params={
                'name': project
            }
        )
        click.echo(result)


@click.command(short_help='Open project in a browser.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    help='Name of project to open.'
)
@pass_client
def open_project(ctx, project):
    projects = ctx.client.action(
        ctx.document,
        ['projects', 'list']
    )
    for _, project_data in iter(projects.items()):
        print(project_data[0])
        if project_data[0]['name'] == project:
            project_url = project_data[0]['url']
            return webbrowser.open_new_tab(project_url)


@click.command(short_help='Undeploy an project from the cluster.')
@click.option(
    '--project',
    '-p',
    type=click.STRING,
    required=True,
    help='Name of the project to undeploy.'
)
@pass_client
def undeploy(ctx, project):
    ctx.client.action(
        ctx.document,
        ['projects', 'undeploy'],
        params={'name': project}
    )
    click.echo('Undeployed {}.'.format(project))


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
cli.add_command(open_project, name='open')
cli.add_command(undeploy)
