# -*- coding: utf-8 -*-

import docker
import errno
import os
from . import shell


class DockerClient(dict):
    _dockerfile_path = '.auger/Dockerfile'

    def __init__(
            self, username=None, password=None, hostname=None, app=None):
        super(DockerClient, self).__init__()
        self.client = docker.from_env(timeout=300)
        self['app'] = app
        self['username'] = username
        self['password'] = password
        self['hostname'] = hostname

    def build(self):
        self.client.images.build(
            dockerfile=self._docker_path(),
            path='.',
            tag=self._image_name()
        )

    def deploy(self):
        pass

    def login(self):
        cmd = 'docker login --username {} --password-stdin {}'.format(
            self['username'],
            self['hostname']
        )
        shell.call(cmd, input_string=self['password'])

    def push(self):
        self.client.images.push(self._image_name())

    def tag(self):
        pass

    def _docker_path(self):
        if os.path.isfile(self._dockerfile_path):
            return self._dockerfile_path
        else:
            raise FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                self._dockerfile_path
            )

    def _image_name(self):
        return '{}/{}'.format(self['hostname'], self['app'])
