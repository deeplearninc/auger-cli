from auger_cli.utils import request_list

display_attributes = ['id', 'description']

def list(client):
    return request_list(client, 'instance_types', params={})
