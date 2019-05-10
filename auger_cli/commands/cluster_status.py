import click

from auger_cli.cli_client import pass_client
from auger_cli.formatter import print_list, print_record, print_table
from auger_cli.api import cluster_status


@click.group(
    'cluster_status',
    invoke_without_command=True,
    short_help='Display cluster CPU and Memory usage.'
)
@click.option(
    '--cluster-id',
    '-c',
    type=click.INT,
    required=False,
    help='Cluster ID.'
)
@click.pass_context
def cluster_status_group(ctx, cluster_id):
    if ctx.invoked_subcommand is None:
        with ctx.obj.cli_error_handler():
            result = cluster_status.read_ex(ctx.obj, cluster_id)
            print_table(result['memory'])
            print_table(result['cpu'])
    else:
        pass
