from ruamel import yaml
import os
import io

from .formatter import print_line
from .utils import remove_file, camelize, merge_dicts
from auger_cli import constants


class AugerConfig(object):

    def __init__(self, config_dir=None, config_settings={}):
        self.config = {}
        self.config_session = {}
        self.experiment_name = None
        self.config_dir = config_dir

        if self.config_dir is None or len(self.config_dir) == 0:
            self.config_dir = os.getcwd()

        self.config_dir = os.path.abspath(self.config_dir)    
        self.config_yml_path = os.path.join(self.config_dir, 'auger_experiment.yml')
        self.exp_session_path = os.path.join(
            self.config_dir, '.auger_experiment_session.yml')
        if os.path.isfile(self.config_yml_path):
            print_line('Loading config file {}'.format(self.config_yml_path))

            with open(self.config_yml_path, 'r') as stream:
                self.config = yaml.safe_load(stream)

            self.experiment_name = self.config.get("experiment")
            if self.experiment_name is None:
                self.experiment_name = os.path.basename(self.config_dir)
                print_line('Experiment name taken from configuration directory name: {}'.format(
                    self.experiment_name))
            else:
                print_line('Experiment name taken from auger_experiment.yml: {}'.format(
                    self.experiment_name))

            if os.path.isfile(self.exp_session_path):
                with open(self.exp_session_path, 'r') as stream:
                    self.config_session = yaml.safe_load(stream)

        merge_dicts(self.config, config_settings)
        self._translate_config_names()

        if self.config.get('login_config_path', None):
            self.config['login_config_path'] = os.path.abspath(self.config['login_config_path'])
            
    def _translate_config_names(self):
        camel_cases_props = ['featureColumns', 'targetFeature', 'categoricalFeatures', 'labelEncodingFeatures', 'datetimeFeatures',
                             'timeSeriesFeatures', 'binaryClassification', 'crossValidationFolds', 'splitOptions']

        evaluation_options = self.config.get('evaluation_options', {})
        for name, value in evaluation_options.items():
            camelize_name = camelize(name, join_string="")
            if camelize_name in camel_cases_props:
                del evaluation_options[name]
                evaluation_options[camelize_name] = value

    def is_dev_mode(self):
        return self.config.get('dev_mode', False)

    def get_hub_url(self):
        return self.config.get('hub_url', constants.DEFAULT_COREAPI_URL)

    def get_login_config_path(self):
        return self.config.get('login_config_path', None)

    def get_project_id(self):
        if self.config.get('project_id') is not None:
            return self.config['project_id']

        return self.config_session.get('project_id')

    def get_project_name(self):
        if len(self.config.get('project', '')) > 0:
            return self.config.get('project')

        return self.experiment_name

    def get_org(self):
        return self.config.get('organization_id'), self.config.get('organization', '')

    def get_experiment(self):
        experiment_id = self.config.get('experiment_id')
        if experiment_id is None:
            experiment_id = self.config_session.get('experiment_id')

        return experiment_id, self.experiment_name

    def get_evaluation_options(self):
        return self.config.get('evaluation_options', {})

    def update_session_file(self, result):
        with io.open(self.exp_session_path, 'w', encoding='utf8') as outfile:
            yaml.safe_dump(result, outfile, allow_unicode=False)
            self.config_session = result

    def delete_session_file(self):
        remove_file(self.exp_session_path)
        self.config_session = {}

    def get_experiment_session_id(self):
        return self.config_session.get('experiment_session_id')

    def get_cluster_settings(self):
        cluster = self.config.get("cluster", {})
        return {
            "worker_count": cluster.get('worker_count', 2),
            "instance_type": cluster.get('instance_type', 'c5.large'),
            "kubernetes_stack": cluster.get('kubernetes_stack', 'stable'),
            "autoterminate_minutes": cluster.get('autoterminate_minutes', 30)
        }

    def get_cluster_task(self):
        return self.config.get("cluster_task", {})
