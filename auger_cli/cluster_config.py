# -*- coding: utf-8 -*-

from .project_config import ProjectConfig
from .docker_client import DockerClient
from .utils import urlparse


class ClusterConfig(object):

    def __init__(
            self, ctx, project=None, cluster_id=None,
            cluster_dict=None):
        self.project_config = None
        self.docker_client = None
        self.cluster_dict = None
        self.registry_dict = {}
        self.cluster_dict = ClusterConfig.fetch(ctx, cluster_id)
        self.registry_dict = self.cluster_dict['registry']
        self._init_config(project)
        if self.project_config.loaded():
            self.docker_client = DockerClient(
                project=self.project_config.get('project'),
                hostname=self.project_config.get('registry_host'),
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
        self.project_config.save()

    def _init_config(self, project):
        self.project_config = ProjectConfig(
            project=project,
            cluster_id=self.cluster_dict.get('id'),
            internal_url=self.registry_dict.get('internal_url'),
            registry_host=urlparse(self.registry_dict.get('url')).hostname
        )
