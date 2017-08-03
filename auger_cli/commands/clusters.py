# -*- coding: utf-8 -*-

from auger_cli.cli import camelize, pass_client
import click
from coreapi.transports import HTTPTransport
from coreapi.transports import http as coreapi_http


@click.group(
    'clusters',
    invoke_without_command=True,
    short_help='Manage Auger Clusters.'
)
@click.pass_context
def cli(ctx):
    if ctx.invoked_subcommand is None:
        clusters = ctx.obj.client.action(
            ctx.obj.document,
            ['clusters', 'list']
        )
        for cluster in iter(clusters['data']):
            click.echo(
                "{: >4}. {} ({}) (up {} sec)".format(
                    cluster['id'],
                    cluster['name'],
                    cluster['status'],
                    cluster['uptime_seconds']
                )
            )
    else:
        pass


@click.command(short_help='Create a new cluster.')
@click.argument('name')
@click.option(
    '--organization-id',
    '-o',
    required=True,
    help='Organization the cluster will use.'
)
@click.option(
    '--worker-count',
    '-c',
    default=1,
    help='Number of worker nodes to create.'
)
@click.option(
    '--instance-type',
    '-i',
    default='t2.medium',
    help='Instance type for the worker nodes.'
)
@pass_client
def create(ctx, name, organization_id, worker_count, instance_type):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'create'],
        params={
            'name': name,
            'organization_id': organization_id,
            'worker_nodes_count': worker_count,
            'node_instance_type': instance_type
        }
    )
    _print_cluster(cluster['data'])


@click.command(short_help='Terminate a cluster.')
@click.argument('cluster_id')
@pass_client
def delete(ctx, cluster_id):
    clusters = ctx.client.action(
        ctx.document,
        ['clusters', 'delete'],
        params={
            'id': cluster_id
        }
    )
    cluster = clusters['data']
    if cluster['id'] == int(cluster_id):
        click.echo("Deleting {}.".format(cluster['name']))


@click.command(short_help='Display cluster details.')
@click.argument('cluster_id')
@pass_client
def show(ctx, cluster_id):
    cluster = ctx.client.action(
        ctx.document,
        ['clusters', 'read'],
        params={
            'id': cluster_id
        }
    )
    _print_cluster(cluster['data'])


@click.command(short_help='Display cluster logs.')
@click.argument('cluster_id')
@click.option(
    '--tail',
    '-t',
    is_flag=True,
    help='Stream logs continously.'
)
@pass_client
def logs(ctx, cluster_id, tail):
    params = {
        'id': cluster_id
    }
    if tail:
        _stream_logs(ctx, params)
    else:
        output = ctx.client.action(
            ctx.document,
            ['clusters', 'logs'],
            params=params
        )
        click.echo(output)


def _print_cluster(cluster_dict):
    attributes = [
        'id',
        'organization_id',
        'name',
        'status',
        'uptime_seconds',
        'worker_nodes_count',
        'node_instance_type',
        'ip_address',
        'deis_url',
        'kubernetes_url'
    ]
    width = len(max(attributes, key=len)) + 1
    for attrib in attributes:
        click.echo(
            "{0:<{width}}: {1}".format(
                camelize(attrib),
                cluster_dict[attrib],
                width=width
            )
        )


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
            for line in response.iter_lines():
                line = line.decode('utf-8')
                if line != 'ping':
                    print(line)

    HTTPTransport.stream_request = stream_request
    # Patch done

    doc = ctx.document

    def flatten(list): [item for sublist in list for item in sublist]
    links = flatten(
        list(
            map(
                lambda link: list(link._data.values()), doc.data.values()
            )
        )
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
