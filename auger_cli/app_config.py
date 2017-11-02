# -*- coding: utf-8 -*-

from git import Repo
import os


class AppConfig(dict):
    _section = 'auger'

    def __init__(
                self, app=None, cluster_id=None, internal_url=None,
                organization_id=None, registry_host=None):
        super(AppConfig, self).__init__()
        self['app'] = app
        self['cluster_id'] = cluster_id
        self['internal_url'] = internal_url
        self['organization_id'] = organization_id
        self['registry_host'] = registry_host
        self._repo = Repo(os.path.curdir)

    def loaded(self):
        if None in self.values():
            return False
        else:
            return True

    def load(self):
        with self._repo.config_reader() as cr:
            if cr.has_section(self._section):
                for key, value in cr.items(self._section):
                    self[key] = value
        return self

    def save(self):
        with self._repo.config_writer() as cw:
            if not cw.has_section(self._section):
                cw.add_section(self._section)
            for key, value in list(self.items()):
                if value is not None:
                    cw.set_value(self._section, key, value)
        return self
