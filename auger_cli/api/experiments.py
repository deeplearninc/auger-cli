# -*- coding: utf-8 -*-
import os

from auger_cli.utils import request_list, get_uid, load_dataframe_from_file, save_dict_to_csv, wait_for_object_state
from auger_cli.constants import REQUEST_LIMIT

from auger_cli.api import cluster_tasks
from auger_cli.api import projects
from auger_cli.api import trials
from auger_cli.api import experiment_sessions
from auger_cli.api import clusters
from auger_cli.api import pipelines
from auger_cli.api import predictions
from auger_cli.api import orgs

display_attributes = ['id', 'name',
                         'project_id', 'project_file_id', 'session', 'cluster' ]


def list(client, project_id, name):
    return request_list(client,
        'experiments',
        params={'project_id': project_id, 'name': name}
    )


def read(client, project_id = None, experiment_name = None, experiment_id = None):
    result = {}
    if experiment_id:
        result = client.call_hub_api(['experiments', 'read'],
            params={'id': experiment_id}
        )
    elif project_id and experiment_name:    
        experiments_list = client.call_hub_api(['experiments', 'list'],
            params={'name': experiment_name, 'project_id': project_id, 'limit': REQUEST_LIMIT}
        )
        if len(experiments_list) > 0:
            result = experiments_list[0]

    return result


def create(client, name, project_id, data_path):
    return client.call_hub_api(['experiments', 'create'],
        params={
            'id': "experiment_" + name + "_" + get_uid(),
            'name': name,
            'project_id': project_id,
            'data_path': data_path
        }
    )


def delete(client, experiment_id):
    experiment = client.call_hub_api(['experiments', 'delete'],
        params={'id': experiment_id}
    )

def update(client, experiment_id, name):
    return client.call_hub_api(['experiments', 'update'],
        params={
            'id': experiment_id,
            'name': name
        }
    )


def get_or_create(client, project_id):
    experiment_id, experiment_name = client.config.get_experiment()

    if experiment_id is not None:
        return read(client, experiment_id=experiment_id)

    experiment = read(client, project_id, experiment_name)
    if experiment.get('id') is not None:
        return experiment

    if len(client.config.get_evaluation_options()) == 0:
        return {}

    if len(client.config.get_evaluation_options().get('data_path', ''))==0:
        client.print_line("To create experiment {}, evaluation_options should contain data_path.".format(experiment_name))
        return {}

    client.print_line(
        'Experiment {} does not exist. Creating ...'.format(experiment_name))

    # search_space = create_cluster_task_ex(client, project_id,
    #     "auger_ml.tasks_queue.tasks.get_experiment_configs_task",
    #     {'augerInfo':{'experiment_id': None}}
    # )
    return create(
        client, experiment_name, project_id, client.config.get_evaluation_options()['data_path'])


def read_ex(client, experiment_id=None):
    if experiment_id is not None:
        experiment = read(client, experiment_id=experiment_id)
        project = projects.read(client, project_id=experiment.get('project_id'))
    else:    
        project = projects.get_or_create(client, create_if_not_exist=True)
        experiment = get_or_create(client, project['id'])

    result = experiment    
    if project.get('cluster_id'):
        result['cluster'] = clusters.read(client, project.get('cluster_id'), clusters.display_attributes)

    if client.config.get_experiment_session_id():    
        result['session'] = experiment_sessions.read(client, client.config.get_experiment_session_id(), ['id', 'status', 'datasource_name', 'model_type'])

    return result

def run(client):
    client.config.delete_session_file()

    project_id = projects.start(client, create_if_not_exist=True)

    experiment = get_or_create(client, project_id)

    org = orgs.read(client)
    result = {}
    if not org.get('is_jupyter_enabled'):
        project_file = wait_for_object_state(client,
            endpoint=['project_files', 'read'],
            params={'id': experiment['project_file_id'], 'project_id': project_id},
            first_status='processing',
            progress_statuses=[
                'processing'
            ]
        )

        params = {
            'project_id': project_id,
            'experiment_id': experiment['id'],
            'status': 'preprocess', 
            'model_settings' : {'evaluation_options': client.config.get_evaluation_options()}, 
            'model_type': client.config.get_model_type()            
        }
        session = experiment_sessions.create(client, params)

        result['experiment_session_id'] = session['id']
    else:        
        task_args = client.config.get_evaluation_options()
        task_args['augerInfo'] = {'experiment_id': experiment['id']}

        result = cluster_tasks.create_ex(
            client, project_id,
            "auger_ml.tasks_queue.evaluate_api.run_cli_evaluate_task", task_args
        )

    result['project_id'] = project_id
    client.config.update_session_file(result)

    return result

def stop(client):
    org = orgs.read(client)
    if not org.get('is_jupyter_enabled'):
        experiment_sessions.update(client, experiment_session_id=client.config.get_experiment_session_id(), status='interrupted')
    else:    
        experiment_id, experiment_name = client.config.get_experiment()
        cluster_tasks.create_ex(
            client, client.config.get_project_id(),
            "auger_ml.tasks_queue.evaluate_api.stop_evaluate_task",
            {'augerInfo': {'experiment_id': experiment_id,
                           'experiment_session_id': client.config.get_experiment_session_id()}}
        )

def read_leaderboard(client, experiment_session_id=None):
    from collections import OrderedDict

    if experiment_session_id is None:
        experiment_session_id = client.config.get_experiment_session_id()

    trials_list = trials.list(client, experiment_session_id)

    leaderboard = []
    for trial in trials_list:
        leaderboard.append({
            trial.get('score_name'): trial.get('score_value'),
            'eval_time(sec)': "{0:.2f}".format(trial.get('raw_data').get('evaluation_time')),
            'id': trial.get('id'),
            'algorithm_name': trial.get('raw_data').get('algorithm_name')
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
            raise Exception(
                'There is no trials for the experiment: %s.' % (name))

        client.print_line('Use best trial to export model: {}'.format(res[0]))

        trial_id = res[0]['id']

    project_id = projects.start(client, create_if_not_exist= False)
    experiment_id, experiment_name = client.config.get_experiment()

    task_args = {
        'augerInfo': {'experiment_id': experiment_id, 'experiment_session_id': client.config.get_experiment_session_id()},
        "export_model_uid": trial_id
    }

    if deploy:
        cluster_tasks.create_ex(client, project_id,
                                            "auger_ml.tasks_queue.tasks.promote_pipeline_task", task_args
                                            )
        client.print_line("Waiting for deploy of pipeline: %s"%trial_id)
        wait_for_object_state(client,
            endpoint=['pipelines', 'read'],
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
        model_path = cluster_tasks.create_ex(client, project_id,
                                            "auger_ml.tasks_queue.tasks.export_grpc_model_task", task_args)
                
        client.print_line("Model exported to remote file: %s"%model_path)
        return projects.download_file(client, project_id, model_path, "models")

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
    df = load_dataframe_from_file(file)
    result = predict_by_records(client, df.values.tolist(), df.columns.get_values().tolist(), pipeline_id, trial_id)

    if save_to_file:
        predict_path = os.path.splitext(file)[0] + "_predicted.csv"
        save_dict_to_csv(result, predict_path)

        return predict_path

    return result
        
def monitor_leaderboard(client, name):
    pass
