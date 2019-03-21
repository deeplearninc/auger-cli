from ruamel import yaml
import os
import io
import json

from .formatter import print_line
from .utils import remove_file, camelize, merge_dicts, to_snake_name, remove_nones_from_dict
from auger_cli import constants
from .constants import REQUEST_LIMIT, API_POLL_INTERVAL

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
        self._translate_config_names(self.config.get('evaluation_options', {}))

        default_config_path = '{home}/.auger'.format(home=os.getenv("HOME"))
        login_config_path = self.config.get('login_config_path', default_config_path)
        self.config['login_config_path'] = os.path.abspath(login_config_path)
        self.credentials_path = os.path.join(self.config['login_config_path'], 'credentials')

    def _translate_config_names(self, evaluation_options, to_camel_case=True):
        camel_cases_props = ['featureColumns', 'targetFeature', 'categoricalFeatures', 'labelEncodingFeatures', 'datetimeFeatures',
                             'timeSeriesFeatures', 'binaryClassification', 'crossValidationFolds', 'splitOptions', 'scoreNames']

        if to_camel_case:
            for name, value in evaluation_options.items():
                camelize_name = camelize(name, join_string="")
                if camelize_name in camel_cases_props:
                    del evaluation_options[name]
                    evaluation_options[camelize_name] = value
        else:
            for name in camel_cases_props:
                if name in evaluation_options:
                    snake_name = to_snake_name(name)
                    evaluation_options[snake_name] = evaluation_options[name]
                    del evaluation_options[name]

    def is_dev_mode(self):
        return self.config.get('dev_mode', False)

    def get_login_config_path(self):
        return self.config.get('login_config_path', None)

    def get_api_poll_interval(self, poll_interval=None):
        if poll_interval:
            return poll_interval

        return self.config.get('api_poll_interval', constants.API_POLL_INTERVAL)

    def get_api_request_limit(self, request_limit=None):
        if request_limit:
            return request_limit

        return self.config.get('api_request_limit', constants.REQUEST_LIMIT)

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
        return remove_nones_from_dict(self.config.get('evaluation_options', {}))

    def get_settings_yml(self, evaluation_options):
        from collections import OrderedDict

        result = self.config
        result['cluster'] = self.get_cluster_settings()

        if evaluation_options:
            result['evaluation_options'] = evaluation_options
        else:
            result['evaluation_options'] = self.get_evaluation_options()

        for name, params in result['evaluation_options'].get('search_space', {}).items():
            result['evaluation_options']['search_space'][name] = json.dumps(params)

        props_to_remove = ['search_space_ensembles', 'split_to_folds_files', 'start_time', 'originalFeaturesCount']
        for prop in props_to_remove:
            if prop in result['evaluation_options']:
                del result['evaluation_options'][prop]

        if 'originalFeatureColumns' in result['evaluation_options']:        
            result['evaluation_options']['feature_columns'] = result['evaluation_options']['originalFeatureColumns']
            del result['evaluation_options']['originalFeatureColumns']

        self._translate_config_names(result['evaluation_options'], to_camel_case=False)

        return yaml.safe_dump(result, allow_unicode=False, default_flow_style = False)    

    def get_model_type(self):
        evaluation_options = self.config.get('evaluation_options', {})
        if 'model_type' in evaluation_options:
            return evaluation_options['model_type']

        model_type = "regression"
        if evaluation_options.get('classification', False):
            model_type = "classification"
        elif len(evaluation_options.get('timeSeriesFeatures', [])) > 0:
            model_type = "timeseries"

        return model_type

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

    def clear_api_token(self):
        self.set_api_token('')

    def get_api_token(self):
        return self.get_credential_key('token')

    def set_api_token(self, token):
        self.set_credentials_key('token', token)

    def get_api_url(self):
        url = self.get_credential_key('url')
        if url is None:
            url = self.config.get('api_url', constants.DEFAULT_API_URL)

        return url

    def get_api_username(self):
        return self.get_credential_key('username')

    def set_api_url(self, url):
        if url:
            self.set_credentials_key('url', url)

    def set_api_username(self, username):
        if username:
            self.set_credentials_key('username', username)

    def set_credentials_key(self, key, value):
        self.ensure_credentials_file()

        with open(self.credentials_path, 'r') as file:
            content = json.loads(file.read())

        content[key] = value

        with open(self.credentials_path, 'w') as file:
            file.write(json.dumps(content))

    def get_credential_key(self, key):
        self.ensure_credentials_file()

        with open(self.credentials_path, 'r') as file:
            content = json.loads(file.read())
            return content.get(key)

    def ensure_credentials_file(self):
        file = self.credentials_path
        dir = os.path.dirname(file)

        if not os.path.exists(dir):
            os.makedirs(dir)

        if not os.path.exists(file):
            with open(file, 'w') as file:
                file.write('{}')
