# -*- coding: utf-8 -*-

import docker
from .utils import urlparse


class DockerClient(object):

    def __init__(self, registry_dict={}, app=None):
        self.client = docker.from_env()
        self.app = app
        self.registry_info = self._parse_registry_info(registry_dict)

    def ls_images(self):
        return self.client.images.list()

    def login(self):
        self.client.login(
            username=self.registry_info['username'],
            password=self.registry_info['password'],
            registry=self.registry_info['hostname'],
            reauth=True
        )

    def _parse_registry_info(self, registry_dict):
        return {
            'hostname': urlparse(registry_dict['url']).hostname,
            'username': registry_dict['login'],
            'password': registry_dict['password']
        }
