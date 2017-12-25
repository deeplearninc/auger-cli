# -*- coding: utf-8 -*-

import docker
import errno
import os

from .constants import DOCKERFILE_PATH
from . import shell


class DockerClient(dict):
    def __init__(
            self, username=None, password=None, hostname=None, project=None):
        super(DockerClient, self).__init__()
        self.client = docker.from_env(timeout=600)
        self['project'] = project
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
        if os.path.isfile(DOCKERFILE_PATH):
            return DOCKERFILE_PATH
        else:
            raise errno.FileNotFoundError(
                errno.ENOENT,
                os.strerror(errno.ENOENT),
                DOCKERFILE_PATH
            )

    def _image_name(self):
        return '{}/{}'.format(self['hostname'], self['project'])
