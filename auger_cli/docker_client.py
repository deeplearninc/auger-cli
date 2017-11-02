# -*- coding: utf-8 -*-

import docker
import errno
import os


class DockerClient(dict):
    _dockerfile_path = '.auger/Dockerfile'

    def __init__(
                self, username=None,
                password=None, hostname=None, app=None):
        super(DockerClient, self).__init__()
        self.client = docker.from_env()
        self['app'] = app
        self['username'] = username
        self['password'] = password
        self['hostname'] = hostname

    def build(self):
        self.client.images.build(
            dockerfile=self._dockerfile(),
            tag='{}/{}'.format(self['hostname'], self['app'])
        )

    def deploy(self):
        pass

    def login(self):
        self.client.login(
            username=self['username'],
            password=self['password'],
            registry=self['hostname'],
            reauth=True
        )

    def push(self):
        pass

    def tag(self):
        pass

    def _dockerfile(self):
        if os.path.isfile(self._dockerfile_path):
            return self._dockerfile_path
        else:
            raise os.FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                self._dockerfile_path
            )
