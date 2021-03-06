# -*- coding: utf-8 -*-
import os
import shutil
import subprocess
from zipfile import ZipFile

from auger_cli.utils import request_list, get_uid, load_records_from_file, save_dfjson_to_csv, wait_for_object_state, download_remote_file, save_records_to_csv
from auger_cli.constants import REQUEST_LIMIT

from auger_cli.api import cluster_tasks
from auger_cli.api import projects
from auger_cli.api import trials
from auger_cli.api import experiment_sessions
from auger_cli.api import clusters
from auger_cli.api import pipelines
from auger_cli.api import pipeline_files
from auger_cli.api import predictions
from auger_cli.api import orgs

display_attributes = ['id', 'name',
                         'project_id', 'project_file_id', 'session', 'cluster' ]


def list(client, project_id, name):
    if project_id is None:
        project_id = projects.get_or_create(client).get('id')

    return request_list(client,
        'experiments',
        params={'project_id': project_id, 'name': name}
    )


def read(client, project_id = None, experiment_name = None, experiment_id = None):
    result = {}
    if experiment_id:
        result = client.call_hub_api('get_experiment', {'id': experiment_id})
    elif project_id and experiment_name:
        experiments_list = client.call_hub_api('get_experiments', {
            'name': experiment_name,
            'project_id': project_id,
            'limit': REQUEST_LIMIT
        })
        
        if len(experiments_list) > 0:
            for item in experiments_list:
                if item['name'] == experiment_name:
                    result = item
                    break

                if item['name'] == experiment_name.replace('_', '-'):
                    result = item
                    break

    return result


def create(client, name, project_id, data_path):
    return client.call_hub_api('create_experiment', {
        'id': "experiment_" + name + "_" + get_uid(),
        'name': name,
        'project_id': project_id,
        'data_path': data_path
    })


def delete(client, experiment_id):
    experiment = client.call_hub_api('delete_experiment', {'id': experiment_id})


def get_or_create(client, project_id):
    experiment_id, experiment_name = client.config.get_experiment()
    experiment = read(client, 
        project_id = project_id, experiment_name = experiment_name, experiment_id=experiment_id)

    if experiment.get('id'):
        project_file = wait_for_object_state(client,
            method='get_project_file',
            params={'id': experiment['project_file_id'], 'project_id': project_id},
            first_status='processing',
            progress_statuses=[
                'processing'
            ]
        )
        if project_file.get('status') != 'processed':
            client.call_hub_api('delete_project_file', {
                    'id': project_file['id']
                })
            delete(client, experiment['id'])            
            experiment = {}

    if not experiment.get('id'):        
        client.print_line(
            'Experiment {} does not exist. Creating ...'.format(experiment_name))

        if len(client.config.get_evaluation_options().get('data_path', ''))==0:
            raise Exception("To create experiment {}, evaluation_options should contain data_path.".format(experiment_name))

        experiment = create( client, 
            experiment_name, project_id, client.config.get_evaluation_options()['data_path'])

    project_file = wait_for_object_state(client,
        method='get_project_file',
        params={'id': experiment['project_file_id'], 'project_id': project_id},
        first_status='processing',
        progress_statuses=[
            'processing'
        ]
    )
    if project_file.get('status') != 'processed':
        raise Exception("Experiment data file cannot be loaded: %s"%project_file)

    return experiment

def read_ex(client, experiment_id=None):
    if experiment_id is not None:
        experiment = read(client, experiment_id=experiment_id)
        project = projects.read(client, project_id=experiment.get('project_id'))
    else:
        project = projects.get_or_create(client, create_if_not_exist=True)
        #experiment = get_or_create(client, project['id'])
        experiment_id, experiment_name = client.config.get_experiment()
        experiment = read(client, 
            project_id = project['id'], experiment_name = experiment_name)


    result = experiment
    if project.get('cluster_id'):
        result['cluster'] = clusters.read(client, project.get('cluster_id'), clusters.display_attributes)

    if client.config.get_experiment_session_id():
        try:
            result['session'] = experiment_sessions.read(client, client.config.get_experiment_session_id(), ['id', 'status', 'datasource_name', 'model_type'])
        except:
            pass

    return result

def read_settings(client):
    evaluation_options = None
    if client.config.get_experiment_session_id():
        evaluation_options = experiment_sessions.read(client, 
            client.config.get_experiment_session_id()).get('model_settings', {}).get('evaluation_options')

    return client.config.get_settings_yml(evaluation_options)

def read_search_space(client):
    project_id, new_cluster, is_single_tenant = projects.start(client, create_if_not_exist=True)
    experiment = get_or_create(client, project_id)

    configs = cluster_tasks.create_ex(
        client, project_id,
        "auger_ml.tasks_queue.tasks.get_experiment_configs_task", {'augerInfo': {'experiment_id': experiment['id']}}
    )
    result = {
        'default_optimizer_names': configs['global_config_dict']['global']['optimizers'],
        'all_optimizer_names': [*configs['optimizers_space']],
        'default_algorithms': {
            'classification': [*configs['user_config_dict']['model_group']['classification']['learning_algorithms']],
            'regression': [*configs['user_config_dict']['model_group']['regression']['learning_algorithms']],
            'timeseries': [*configs['user_config_dict']['model_group']['timeseries']['learning_algorithms']],
        },
        'all_algorithms': {
            'classification': configs['classifier_config_dict']['classification']['learning_algorithms'],
            'regression': configs['regressor_config_dict']['regression']['learning_algorithms'],
            'timeseries': configs['timeseries_config_dict']['timeseries']['learning_algorithms'],
            }
    }

    return result

def run(client):    
    client.config.delete_session_file()

    project_id, new_cluster, is_single_tenant = projects.start(client, create_if_not_exist=True)
    experiment = get_or_create(client, project_id)

    params = {
        'project_id': project_id,
        'experiment_id': experiment['id'],
        #'status': 'preprocess',
        'model_settings' : {'evaluation_options': client.config.get_evaluation_options()},
        'model_type': client.config.get_model_type()
    }
    session = experiment_sessions.create(client, params)
    experiment_sessions.update(client, session['id'], status='preprocess')

    result = { 
        'experiment_session_id': session['id'],
        'project_id': project_id
    }
    client.config.update_session_file(result)

    return result


def stop_cluster(client):
    projects.stop_cluster(client)


def restart_cluster(client, run_experiment=True):
    stop_cluster(client)
    if run_experiment:
        run(client)
    else:
        project_id, new_cluster, is_single_tenant = projects.start(client, create_if_not_exist=True)

def stop(client):
    org = orgs.read(client)
    experiment_sessions.update(client, experiment_session_id=client.config.get_experiment_session_id(), status='interrupted')

def read_leaderboard(client, experiment_session_id=None):
    from collections import OrderedDict

    if experiment_session_id is None:
        experiment_session_id = client.config.get_experiment_session_id()

    trials_list = trials.list(client, experiment_session_id)

    leaderboard = []
    for trial in trials_list:
        optimizer_name = trial.get('raw_data').get('optimizer_name')
        if optimizer_name:
            optimizer_name = optimizer_name.split('.')[-1]

        leaderboard.append({
            trial.get('score_name'): trial.get('score_value'),
            'time(sec)': "{0:.2f}".format(trial.get('raw_data').get('evaluation_time')),
            'id': trial.get('id'),
            'algorithm': trial.get('raw_data').get('algorithm_name', '').split('.')[-1],
            'optimizer': optimizer_name
        })

    leaderboard.sort(key=lambda t: t[trial.get('score_name')], reverse=True)

    exp_session = experiment_sessions.read(client, experiment_session_id)
    #print(exp_session.get('model_settings', {}).keys())
    info = OrderedDict({
        'Start': exp_session.get('model_settings', {}).get('start_time'),
        'Status': exp_session.get('status'),
        'Completed': exp_session.get('model_settings', {}).get('completed_evaluations'),
        'Max count': exp_session.get('model_settings', {}).get('total_evaluations'),
        'Error': exp_session.get('error'),
    })

    return leaderboard, info


def export_model(client, trial_id, deploy=False):
    if trial_id is None:
        res, info = read_leaderboard(client)
        if len(res) == 0:
            experiment_id, experiment_name = client.config.get_experiment()
            raise Exception(
                'There is no trials for the experiment: %s.' % (experiment_name))

        client.print_line('Use best trial to export model: {}'.format(res[0]))

        trial_id = res[0]['id']

    models_path = client.config.get_models_path()
    if not deploy:
        exported_model_path = os.path.join(models_path, 'export_{}.zip'.format(trial_id))
        if os.path.exists(exported_model_path):
            return exported_model_path
        
    project_id, new_cluster, is_single_tenant = projects.start(client, create_if_not_exist=False)
    experiment = get_or_create(client, project_id)

    task_args = {
        'augerInfo': {'experiment_id': experiment['id'], 'experiment_session_id': client.config.get_experiment_session_id()},
        "export_model_uid": trial_id
    }
    org = orgs.read(client)

    if deploy:
        params = {
            'trial_id': trial_id
        }
        pipeline = pipelines.create(client, params)
        trial_id = pipeline['id']

        client.print_line("Waiting for deploy of pipeline: %s"%trial_id)
        wait_for_object_state(client,
            method='get_pipeline',
            params={'id': trial_id},
            first_status='creating_files',
            progress_statuses=[
                'creating_files', 'packaging', 'deploying'
            ],
            poll_interval=10
        )

        pipeline = pipelines.read(client, trial_id)
        client.print_line("Pipeline {} status: {}; error: {}".format(pipeline.get('id'), pipeline.get('status'), pipeline.get('error_message')))
        return trial_id
    else:
        params = {
            'trial_id': trial_id
        }
        pipeline_file = pipeline_files.create(client, params)
        
        client.print_line("Waiting for download of pipeline: %s" % trial_id)
        pipeline_file = wait_for_object_state(client,
            method='get_pipeline_file',
            params={'id': pipeline_file['id']},
            first_status='not_requested',
            progress_statuses=[
                'not_requested', 'pending'
            ],
            poll_interval=2,
            status_name='s3_model_path_status'
        )
        client.print_line("Model S3 path: %s" %
                          pipeline_file)
        return download_remote_file('models', pipeline_file['signed_s3_model_path'])

    return None

def undeploy_model(client, pipeline_id):
    if not pipeline_id:
            raise Exception(
                'There is no pipeline_id passed.'
            )
    
    params = {
        'status': 'undeploying',
        'id': pipeline_id
    }

    pipelines.update(client, params)

    client.print_line("Waiting for undeploy of pipeline: %s" % pipeline_id)
    wait_for_object_state(client,
                          method='get_pipeline',
                          params={'id': pipeline_id},
                          first_status='ready',
                          progress_statuses=[
                              'ready', 'undeploying'
                          ],
                          poll_interval=2
                          )
    return None

def predict_by_records(client, records, features, pipeline_id=None, trial_id=None):
    if pipeline_id is None:
        pipeline_id = export_model(client, trial_id, deploy=True)

    pipeline = pipelines.read(client, pipeline_id)
    if pipeline.get('status') != 'ready':
        raise Exception("Pipeline is not ready or has issues. Try to create another one.")

    prediction_id = predictions.create(client, pipeline_id, records, features)
    return predictions.read(client, prediction_id).get('result')

def predict_by_file(client, file, pipeline_id=None, trial_id=None, save_to_file=False):
    records, features = load_records_from_file(file)
    result = predict_by_records(client, records, features, pipeline_id, trial_id)

    if save_to_file:
        predict_path = os.path.splitext(file)[0] + "_predicted.csv"
        save_records_to_csv(result, predict_path)

        return predict_path

    return result

def predict_remotly(client, file, trial_id, threshold, save_to_file=False):
    records, features = load_records_from_file(file)
    trial = trials.read(client, trial_id, experiment_session_id=None)

    project_id, new_cluster, is_single_tenant = projects.start(client, create_if_not_exist=False)
    experiment = get_or_create(client, project_id)

    path_to_model = cluster_tasks.create_ex(client, project_id,
        "auger_ml.tasks_queue.tasks.export_model_task",
        {
            'trial_data': trial.get('raw_data'),
            'augerInfo': {'experiment_id': experiment['id']}
        }
    )
    result = cluster_tasks.create_ex(client, project_id,
        "auger_ml.tasks_queue.tasks.predict_by_model_task",
        {
            'model_path': path_to_model, 
            'path_to_predict': None, 
            'records': records,
            'features': features, 
            'predict_value_num': None, 
            'threshold': threshold,
            'augerInfo': {'experiment_id': experiment['id']}
        }
    )

    if save_to_file:
        predict_path = os.path.splitext(file)[0] + "_predicted.csv"
        save_dfjson_to_csv(result, predict_path)

        return predict_path

    return result

def monitor_leaderboard(client, name):
    pass

def predict_by_file_locally(client, file, trial_id=None, save_to_file=False, 
    pull_docker=False, threshold=None, locally=False):
    docker_tag = client.config.get_cluster_settings()['kubernetes_stack']

    zip_path = export_model(client, trial_id, deploy=False)
    target_path = os.path.splitext(zip_path)[0]
    folder_existed = os.path.exists(target_path)

    if not folder_existed:
        with ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(target_path)

    filename = os.path.basename(file)
    data_path = os.path.dirname(file)
    target_filename = os.path.splitext(filename)[0]
    args = ""
    if threshold:
        args += " --threshold={threshold}".format(threshold=threshold)

    if locally:
        command = "python %s/client.py --model_path=%s/model --path_to_predict=%s"%(target_path,target_path,file)
    else:    
        if pull_docker:
            command = 'docker pull deeplearninc/auger-ml-worker:{docker_tag}'.format(docker_tag=docker_tag)
            client.print_debug(command)
            subprocess.check_call(command, shell=True)

        args += " --path_to_predict=./model_data/{filename}".format(filename=filename)

        command = (r"docker run "
                    "-v {pwd}/{model_path}:/var/src/auger-ml-worker/exported_model "
                    "-v {pwd}/{data_path}:/var/src/auger-ml-worker/model_data "
                    "deeplearninc/auger-ml-worker:{docker_tag} python "
                    "./exported_model/client.py").format(
                        model_path=target_path,
                        data_path=data_path,
                        docker_tag=docker_tag,
                        pwd=os.getcwd()
                  )

    command += args            
    client.print_debug(command)
    subprocess.check_call(command, shell=True)
    if not folder_existed:
        shutil.rmtree(target_path, ignore_errors=True)
        
    return os.path.join(data_path, "{}_predicted.csv".format(target_filename))
