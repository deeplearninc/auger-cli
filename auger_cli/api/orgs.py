# -*- coding: utf-8 -*-

from auger_cli.formatter import print_line, print_record
from auger_cli.utils import request_list
from auger_cli.constants import REQUEST_LIMIT


org_attributes = ['id', 'name', 'main_bucket', 'status']


def list_orgs(ctx):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'organizations',
            params={}
        )

def list_orgs_full(auger_client):
    with auger_client.coreapi_action():
        return auger_client.client.action(
            auger_client.document,
            ['organizations', 'list'],
            params={'limit': REQUEST_LIMIT}
        )['data']


def read_org(auger_client, name):
    with auger_client.coreapi_action():
        res = auger_client.client.action(
            auger_client.document,
            ['organizations', 'list'],
            params={'name': name, 'limit': REQUEST_LIMIT}
        )['data']
        if len(res) > 0:
            return res[0]
        
        return {}

def create_org(ctx, name, access_key, secret_key):
    params = {'name': name}
    if all((access_key, secret_key)):
        params['access_key'] = access_key
        params['secret_key'] = secret_key
    with ctx.coreapi_action():
        org = ctx.client.action(
            ctx.document,
            ['organizations', 'create'],
            params=params
        )
        print_record(org['data'], org_attributes)


def delete_org(ctx, organization_id):
    with ctx.coreapi_action():
        orgs = ctx.client.action(
            ctx.document,
            ['organizations', 'delete'],
            params={
                'id': organization_id
            }
        )
        org = orgs['data']
        if org['id'] == int(organization_id):
            print_line("Deleting {0}.".format(org['name']))


def update_org(ctx, access_key, secret_key, organization_id):
    with ctx.coreapi_action():
        org = ctx.client.action(
            ctx.document,
            ['organizations', 'update'],
            params={
                'id': organization_id,
                'access_key': access_key,
                'secret_key': secret_key
            }
        )
        print_record(org['data'], org_attributes)
