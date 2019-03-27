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

    def get_models_path(self):
        return self.config.get('models_path', 'models')
        
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

    def get_model_type(self, evaluation_options = None):
        if evaluation_options is None:
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

    def get_space_definition(self, evaluation_options=None):
        MT_ALGOS = ['XGB', 'LGBM', 'ExtraTrees', 'RandomForest', 'CatBoost', 'LogisticRegression']
        SEQ_OPTIMIZERS = ['RandomSearchOptimizer', 'NelderMeadOptimizer', 'DEOptimizer', 'PSOOptimizer', 'LIPOOptimizer']

        result = []
        #Default settings
        optimizers = {"seq": 1, "batch": 1}
        algorithms = {'mt': 6, 'non_mt': 4}

        if evaluation_options is not None:
            if evaluation_options.get('optimizers_names'):
                optimizers = {"seq": 0, "batch": 0}
                non_batch = 1 if 'auger_ml.optimizers.warmstart_optimizer.WarmStartOptimizer' in evaluation_options['optimizers_names'] else 0
                for seq_name in SEQ_OPTIMIZERS:
                    for opt_name in evaluation_options['optimizers_names']:
                        if seq_name in opt_name:
                            optimizers['seq'] = optimizers['seq'] + 1
                        
                optimizers['batch'] = len(evaluation_options['optimizers_names']) - optimizers['seq'] - non_batch

            if not evaluation_options.get('search_space'):
                if evaluation_options.get('model_type'):
                    model_type = self.get_model_type(evaluation_options)
                    if model_type == 'classification':
                        algorithms = {'mt': 6, 'non_mt': 4}
                    elif model_type == 'regression':
                        algorithms = {'mt': 5, 'non_mt': 5}
                    elif model_type == 'timeseries':
                        algorithms = {'mt': 5, 'non_mt': 6}
            else:
                algorithms = {'mt': 0, 'non_mt': 0}
                for mt_name in MT_ALGOS:
                    for algo_name in evaluation_options['search_space'].keys():
                        if mt_name in algo_name:
                            algorithms['mt'] = algorithms['mt'] + 1

                algorithms['non_mt'] = len(evaluation_options['search_space']) - algorithms['mt']

        return optimizers, algorithms

    def get_worker_types(self, cluster, evaluation_options=None):
        INSTANCE_TYPES = {
            'c5.large': '2xCPU 4.0 GB RAM',
            'c5.xlarge': '4xCPU 8.0 GB RAM',
            'c5.2xlarge': '8xCPU 16.0 GB RAM',
            'c5.4xlarge': '16xCPU 32.0 GB RAM',
            'c5.9xlarge': '36xCPU 72.0 GB RAM',
            'c5.18xlarge': '72xCPU 144.0 GB RAM',
            'r5.large': '2xCPU 16.0 GB RAM',
            'r5.xlarge': '4xCPU 32.0 GB RAM',
            'r5.2xlarge': '8xCPU 64.0 GB RAM',
            'r5.4xlarge': '16xCPU 128.0 GB RAM',
            'r5.12xlarge': '48xCPU 384.0 GB RAM',
            'r5.24xlarge': '96xCPU 768.0 GB RAM',
            'p3.2xlarge': '8xCPU 61.0 GB RAM'
        }
        def _divide(n1, n2):
            main_count = n1//n2
            last_count = main_count+n1%n2
            return main_count, last_count

        cpu_node = int(INSTANCE_TYPES[cluster['instance_type']].split('x')[0])-1
        nodes_count = cluster['worker_nodes_count']

        optimizers, algorithms = self.get_space_definition(evaluation_options)
        print(optimizers, algorithms)

        optimizers_count = optimizers['seq'] + optimizers['batch']
        workers = { '1': {
            'worker_count': max(optimizers_count*algorithms['non_mt'], 1), 
            'worker_args': '--queues evaluate_trials,augerml_api'
        }}
        
        mt_workers = optimizers_count*algorithms['mt']
        cpu_count = cpu_node * nodes_count - 1 #One cpu worker minimum
        print("cpu_count:%s, mt_workers: %s, non_mt_workers: %s"%(cpu_count, mt_workers, workers['1']['worker_count']))

        if cpu_count <= mt_workers + workers['1']['worker_count']:
            workers['1']['worker_count'] = cpu_count + 1
            return workers

        #Distribute workers by nodes evenly:
        node_workers, last_node_workers = _divide(mt_workers + workers['1']['worker_count'], nodes_count)
        print("node_workers: %s, last_node_workers: %s"%(node_workers, last_node_workers))
        if node_workers == 0:
            if optimizers['batch'] > 0:
                if mt_workers == 0:
                    node_workers = last_node_workers = cpu_node
                else:
                    #node_workers, last_node_workers = _divide(cpu_node,2)
                    node_workers = last_node_workers = 1
            else:
                node_workers = last_node_workers = 1

        nodes = []
        for i in range(0, nodes_count):
            nodes.append({'1': {'worker_count': node_workers}})

        nodes[-1] = {'1': {'worker_count': last_node_workers}}
        print(nodes)

        #Adjust mt workes cpus:
        if mt_workers > 0:
            mt_workers_per_node, last_mt_workers_per_node = _divide(mt_workers, nodes_count)
            if mt_workers_per_node == 0:
                mt_workers_per_node = 1
                last_mt_workers_per_node = 1

            print(mt_workers_per_node, last_mt_workers_per_node)
            for i in range(0, nodes_count):
                cur_mt_workers = mt_workers_per_node if i < nodes_count-1 else last_mt_workers_per_node
                if cur_mt_workers > 0:
                    if nodes[i]['1']['worker_count'] == 1:
                        nodes[i]['1']['worker_count'] += 1

                    mt_cpus, last_mt_cpus = _divide(cpu_node-(nodes[i]['1']['worker_count']-cur_mt_workers), cur_mt_workers)
                    print(mt_cpus, last_mt_cpus)
                    if not str(mt_cpus) in nodes[i]:
                        nodes[i][str(mt_cpus)] = {'worker_count':0}    
                    nodes[i][str(mt_cpus)]['worker_count'] += cur_mt_workers-1
                    nodes[i]['1']['worker_count'] -= cur_mt_workers-1

                    if not str(last_mt_cpus) in nodes[i]:
                        nodes[i][str(last_mt_cpus)] = {'worker_count':0}
                    nodes[i][str(last_mt_cpus)]['worker_count'] += 1
                    nodes[i]['1']['worker_count'] -= 1

            print(nodes)            

        #Calc workers cpu:
        workers = {}
        for item in nodes:
            for item_cpu, value in item.items():
                if not item_cpu in workers:
                    workers[item_cpu] = {'worker_count': 0}

                workers[item_cpu]['worker_count'] += value['worker_count']
                
        #Assign workers args:
        for worker_cpu, params in workers.items():
            if worker_cpu == '1':
                params['worker_args'] = '--queues evaluate_trials,augerml_api'
            else:
                params['worker_args'] = "--queues evaluate_trials_mt --auger-worker-cpu=%s"%worker_cpu

        return workers    
        # return [
        #     {'cpu_count': 1, 'worker_count': 2, 'worker_args': '--queues evaluate_trials,augerml_api'},
        #     {'cpu_count': 2, 'worker_count': 2, 'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=2'},
        #     {'cpu_count': 3, 'worker_count': 1, 'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=3'},        
        # ]

    def get_cluster_settings(self):
        cluster = self.config.get("cluster", {})
        #Deprecated worker_count
        if 'worker_count' in cluster:
            worker_nodes_count = cluster['worker_count']
        else:
            worker_nodes_count = cluster.get('worker_nodes_count', 2)
                
        res = {
            "worker_nodes_count": worker_nodes_count,
            "instance_type": cluster.get('instance_type', 'c5.large'),
            "kubernetes_stack": cluster.get('kubernetes_stack', 'stable'),
            "autoterminate_minutes": cluster.get('autoterminate_minutes', 30)
        }
        if cluster.get('workers_per_node_count') is not None:
            res["workers_per_node_count"] = cluster['workers_per_node_count']

        return res
            
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
