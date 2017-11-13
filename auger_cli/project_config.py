# -*- coding: utf-8 -*-


class ProjectConfig(dict):

    def __init__(
            self, project=None, cluster_id=None, internal_url=None,
            registry_host=None):
        super(ProjectConfig, self).__init__()
        self['project'] = project
        self['cluster_id'] = cluster_id
        self['internal_url'] = internal_url
        self['registry_host'] = registry_host

    def loaded(self):
        if None in self.values():
            return False
        else:
            return True
