from ruamel import yaml
import os
import io

from .formatter import print_line
from .FSClient import FSClient


class AugerConfig(object):
    def __init__(self):
        print_line('Loading {} from current directory ...'.format("auger_experiment.yml"))

        with open("auger_experiment.yml", 'r') as stream:
            self.config = yaml.safe_load(stream)

        self.experiment_name = self.config.get("experiment")
        if self.experiment_name is None:
            self.experiment_name = os.path.basename(os.getcwd())
            print_line('Experiment name taken from current directory name: {}'.format(self.experiment_name))
        else:
            print_line('Experiment name taken from auger_experiment.yml: {}'.format(self.experiment_name))

        self.config_ids = {}    
        if FSClient().isFileExists(".auger_experiment_ids.yml"):
            with open(".auger_experiment_ids.yml", 'r') as stream:
                self.config_ids = yaml.safe_load(stream)
            
    def get_project_id(self):
        if self.config.get('project_id') is not None:
            return self.config['project_id']

        return self.config_ids['project_id']

    def get_project_name(self):
        if len(self.config.get('project', '')) > 0:
            return self.config.get('project')

        return self.experiment_name    

    def get_org(self):
        return self.config.get('organization_id'), self.config.get('organization', '')    

    def get_experiment(self):
        experiment_id = self.config.get('experiment_id')
        if experiment_id is None:
            experiment_id = self.config_ids.get('experiment_id')
                   
        return experiment_id, self.experiment_name

    def get_evaluation(self):
        return self.config.get('evaluation_options', {})            

    def update_ids_file(self, result):
        with io.open(".auger_experiment_ids.yml", 'w', encoding='utf8') as outfile:
            yaml.dump(result, outfile)

    def get_experiment_session_id(self):
        return self.config_ids['experiment_session_id']

    def get_cluster_settings(self):
        return {
            "worker_count" : self.config.get('worker_count', 2),
            "instance_type": self.config.get('instance_type', 'c5.large'),
            "kubernetes_stack": self.config.get('kubernetes_stack', 'stable'),
            "automatic_termination": self.config.get('automatic_termination', "1 Hour")
        }    
