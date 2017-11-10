# -*- coding: utf-8 -*-

import click
from .app_config import AppConfig
from .docker_client import DockerClient
from .utils import urlparse


class ClusterConfig(object):

    def __init__(
            self, ctx, app=None, cluster_id=None,
            cluster_dict=None):
        self.app_config = None
        self.docker_client = None
        self.cluster_dict = None
        self.registry_dict = {}
        self.cluster_dict = ClusterConfig.fetch(ctx, cluster_id)
        self.registry_dict = self.cluster_dict['registry']
        self._init_config(app)
        if self.app_config.loaded():
            self.docker_client = DockerClient(
                app=self.app_config.get('app'),
                hostname=self.app_config.get('registry_host'),
                username=self.registry_dict.get('login'),
                password=self.registry_dict.get('password')
            )

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

    def _init_config(self, app):
        self.app_config = AppConfig(
            app=app,
            cluster_id=self.cluster_dict.get('id'),
            internal_url=self.registry_dict.get('internal_url'),
            registry_host=urlparse(self.registry_dict.get('url')).hostname
        )
