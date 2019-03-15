# -*- coding: utf-8 -*-

from auger_cli.utils import request_list
from auger_cli.constants import REQUEST_LIMIT


display_attributes = ['id', 'name', 'main_bucket', 'status']


def list(client):
    return request_list(client, 'organizations', params={})


def read(client, org_name=None, org_id=None):
    result = {}

    if org_name is None and org_id is None:
        org_id, org_name = client.config.get_org()
        if org_id is None and len(org_name) == 0:
            for org in list(client):
                org_name = org.get('name', "")
                org_id = org.get('id')
                break

        if org_id is None:
            org = read(client, org_name)
            org_id = org.get('id')

    if org_id:
        result = client.call_hub_api('get_organization', {'id': org_id})
    elif org_name:
        orgs_list = client.call_hub_api('get_organizations', {
            'name': org_name,
            'limit': REQUEST_LIMIT
        })

        if len(orgs_list) > 0:
            result = orgs_list[0]

    return result
