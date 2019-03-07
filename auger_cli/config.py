from ruamel import yaml
import os
import io

from .formatter import print_line
from .utils import remove_file

class AugerConfig(object):
    def __init__(self):
        self.config = {}
        self.config_session = {}    
        self.experiment_name = None

        if os.path.isfile(".auger_experiment_session.yml"):
            print_line('Loading {} from current directory ...'.format("auger_experiment.yml"))

            with open("auger_experiment.yml", 'r') as stream:
                self.config = yaml.safe_load(stream)

            self.experiment_name = self.config.get("experiment")
            if self.experiment_name is None:
                self.experiment_name = os.path.basename(os.getcwd())
                print_line('Experiment name taken from current directory name: {}'.format(self.experiment_name))
            else:
                print_line('Experiment name taken from auger_experiment.yml: {}'.format(self.experiment_name))

            if os.path.isfile(".auger_experiment_session.yml"):
                with open(".auger_experiment_session.yml", 'r') as stream:
                    self.config_session = yaml.safe_load(stream)
            
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

    def get_evaluation(self):
        return self.config.get('evaluation_options', {})            

    def update_session_file(self, result):
        with io.open(".auger_experiment_session.yml", 'w', encoding='utf8') as outfile:
            yaml.safe_dump(result, outfile, allow_unicode=False)

    def delete_session_file(self):
        remove_file(".auger_experiment_session.yml")
        self.config_session = {}

    def get_experiment_session_id(self):
        return self.config_session.get('experiment_session_id')

    def get_cluster_settings(self):
        cluster = self.config.get("cluster", {})
        return {
            "worker_count" : cluster.get('worker_count', 2),
            "instance_type": cluster.get('instance_type', 'c5.large'),
            "kubernetes_stack": cluster.get('kubernetes_stack', 'stable'),
            "autoterminate_minutes": cluster.get('autoterminate_minutes', 30)
        }    

    def get_cluster_task(self):
        return self.config.get("cluster_task", {})
