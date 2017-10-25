# -*- coding: utf-8 -*-

from .app_config import AppConfig
from .docker_client import DockerClient


class ClusterConfig(dict):

    def __init__(self, cluster_dict={}):
        if cluster_dict:
            registry_dict = cluster_dict['registry']
            self.docker_client = DockerClient(registry_dict)
            self.app_config = AppConfig(
                cluster_id=cluster_dict['id'],
                internal_url=registry_dict['internal_url'],
                organization_id=cluster_dict['organization_id'],
                registry_url=self.docker_client.registry_info['hostname']
            )

    def login(self):
        self.docker_client.login()

    def save(self):
        self.login()
        self.app_config.save()
