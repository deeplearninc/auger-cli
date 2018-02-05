# -*- coding: utf-8 -*-

from ...formatter import print_line, print_record


org_attributes = ['id', 'name', 'main_bucket', 'status']


def list_orgs(ctx):
    with ctx.coreapi_action():
        return ctx.client.action(
            ctx.document,
            ['organizations', 'list']
        )['data']


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
