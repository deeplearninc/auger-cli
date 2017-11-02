# -*- coding: utf-8 -*-

from .app_config import AppConfig
from .docker_client import DockerClient
from .utils import urlparse


class ClusterConfig(object):

    def __init__(
                self, ctx, app=None,
                cluster_id=None, cluster_dict=None):
        self.app_config = None
        self.docker_client = None
        # Try to load from cached config
        self.app_config = AppConfig().load()
        if not self.app_config.loaded():
            cluster_dict = ClusterConfig.fetch(ctx, cluster_id)
            self._init_config(cluster_dict, app)
        self.docker_client = DockerClient(**self.app_config)

    @staticmethod
    def fetch(ctx, cluster_id):
        cluster_data = ctx.client.action(
            ctx.document,
            ['clusters', 'read'],
            params={
                'id': cluster_id
            }
        )
        return cluster_data['data']

    def login(self):
        self.docker_client.login()

    def save(self):
        self.app_config.save()

    def _init_config(self, cluster_dict, app):
        registry_dict = cluster_dict['registry']
        self.app_config = AppConfig(
            cluster_id=cluster_dict.get('id'),
            internal_url=registry_dict.get('internal_url'),
            organization_id=cluster_dict.get('organization_id'),
            registry_host=urlparse(registry_dict.get('url')).hostname
        )
