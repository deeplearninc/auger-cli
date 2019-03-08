# -*- coding: utf-8 -*-
import os
import click

from auger_cli.formatter import print_line, print_record, wait_for_task_result
from auger_cli.utils import request_list, get_uid, load_dataframe_from_file, save_dict_to_csv
from auger_cli.config import AugerConfig
from auger_cli.constants import REQUEST_LIMIT

from auger_cli.api.cluster_tasks import (
    create_cluster_task_ex,
)

from auger_cli.api.projects import (
    read_project_withorg,
    create_project,
    read_project_byid,
    start_project,
    get_or_create_project,
    download_project_file
)

from auger_cli.api.trials import (
    list_trials
)
from auger_cli.api.experiment_sessions import (
    read_experiment_session,
    experiment_session_attributes
)
from auger_cli.api.clusters import read_cluster, cluster_attributes
from auger_cli.api.pipelines import read_pipeline, pipeline_attributes
from auger_cli.api.predictions import (
    read_prediction,
    create_prediction
)

experiment_attributes = ['id', 'name',
                         'project_id', 'project_file_id', 'session', 'cluster' ]


def list_experiments(ctx, project_id, name):
    with ctx.coreapi_action():
        return request_list(
            ctx,
            'experiments',
            params={'project_id': project_id, 'name': name}
        )


def create_experiment(ctx, name, project_id, data_path):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'create'],
            params={
                'id': "experiment_" + name + "_" + get_uid(),
                'name': name,
                'project_id': project_id,
                'data_path': data_path
            }
        )
        return experiment['data']

    return {}


def delete_experiment(ctx, experiment_id):
    with ctx.coreapi_action():
        experiments = ctx.client.action(
            ctx.document,
            ['experiments', 'delete'],
            params={
                'id': experiment_id
            }
        )
        experiment = experiments['data']
        if experiment['id'] == int(experiment_id):
            print_line("Deleting {0}.".format(experiment['name']))


def update_experiment(ctx, experiment_id, name):
    with ctx.coreapi_action():
        experiment = ctx.client.action(
            ctx.document,
            ['experiments', 'update'],
            params={
                'id': experiment_id,
                'name': name
            }
        )
        print_record(experiment['data'], experiment_attributes)


def read_experiment_byid(auger_client, experiment_id):
    result = {}
    with auger_client.coreapi_action():
        result = auger_client.client.action(
            auger_client.document,
            ['experiments', 'read'],
            params={'id': experiment_id}
        )['data']
    #print(result.keys())     
    return result


def read_experiment(auger_client, project_id, name):
    result = {}
    with auger_client.coreapi_action():
        res = auger_client.client.action(
            auger_client.document,
            ['experiments', 'list'],
            params={'name': name, 'project_id': project_id, 'limit': REQUEST_LIMIT}
        )['data']
        if len(res) > 0:
            result = res[0]

    return result


def get_or_create_experiment(ctx, project_id):
    experiment_id, experiment_name = ctx.config.get_experiment()

    if experiment_id is not None:
        return read_experiment_byid(ctx, experiment_id)

    experiment = read_experiment(ctx, project_id, experiment_name)
    if experiment.get('id') is not None:
        return experiment

    if len(ctx.config.get_evaluation()) == 0:
        return {}

    if len(ctx.config.get_evaluation().get('data_path', ''))==0:
        print_line("To create experiment {}, evaluation_options should contain data_path.".format(experiment_name))
        return {}

    print_line(
        'Experiment {} does not exist. Creating ...'.format(experiment_name))

    # search_space = create_cluster_task_ex(ctx, project_id,
    #     "auger_ml.tasks_queue.tasks.get_experiment_configs_task",
    #     {'augerInfo':{'experiment_id': None}}
    # )
    experiment = create_experiment(
        ctx, experiment_name, project_id, ctx.config.get_evaluation()['data_path'])
    return experiment


def read_experiment_info(auger_client, experiment_id):
    auger_client.config = AugerConfig()

    if experiment_id is not None:
        experiment = read_experiment_byid(auger_client, experiment_id)
        project = read_project_byid(auger_client, experiment.get('project_id'))
    else:    
        project = get_or_create_project(auger_client, create_if_not_exist=True)
        experiment = get_or_create_experiment(auger_client, project['id'])

    result = experiment    
    if project.get('cluster_id'):
        result['cluster'] = read_cluster(auger_client, project.get('cluster_id'), cluster_attributes)

    if auger_client.config.get_experiment_session_id():    
        result['session'] = read_experiment_session(auger_client, auger_client.config.get_experiment_session_id(), ['id', 'status', 'datasource_name', 'model_type'])

    return result

def run_experiment(ctx):
    ctx.config = AugerConfig()
    ctx.config.delete_session_file()

    project_id = start_project(ctx, create_if_not_exist=True)

    experiment = get_or_create_experiment(ctx, project_id)

    task_args = ctx.config.get_evaluation()
    task_args['augerInfo'] = {'experiment_id': experiment['id']}

    result = create_cluster_task_ex(
        ctx, project_id,
        "auger_ml.tasks_queue.evaluate_api.run_cli_evaluate_task", task_args
    )
    if result is None:
        result = {}

    result['project_id'] = project_id
    ctx.config.update_session_file(result)


def stop_experiment(ctx):
    config = AugerConfig()
    experiment_id, experiment_name = config.get_experiment()

    create_cluster_task_ex(
        ctx, config.get_project_id(),
        "auger_ml.tasks_queue.evaluate_api.stop_evaluate_task",
        {'augerInfo': {'experiment_id': experiment_id,
                       'experiment_session_id': config.get_experiment_session_id()}}
    )


def read_leaderboard_experiment(ctx, experiment_session_id):
    from collections import OrderedDict

    config = AugerConfig()
    if experiment_session_id is None:
        experiment_session_id = config.get_experiment_session_id()

    trials = list_trials(ctx, experiment_session_id)

    leaderboard = []
    for trial in trials:
        leaderboard.append({
            trial.get('score_name'): trial.get('score_value'),
            'eval_time(sec)': "{0:.2f}".format(trial.get('raw_data').get('evaluation_time')),
            'id': trial.get('id'),
            'algorithm_name': trial.get('raw_data').get('algorithm_name')
        })

    leaderboard.sort(key=lambda t: t[trial.get('score_name')], reverse=True)

    exp_session = read_experiment_session(ctx, experiment_session_id)
    #print(exp_session.get('model_settings', {}).keys())
    info = OrderedDict({
        'Start': exp_session.get('model_settings', {}).get('start_time'), 
        'Status': exp_session.get('status'), 
        'Completed': exp_session.get('model_settings', {}).get('completed_evaluations'),
        'Max count': exp_session.get('model_settings', {}).get('total_evaluations'),
    })

    return leaderboard, info


def export_model_experiment(ctx, trial_id, deploy=False):
    if trial_id is None:
        res, info = read_leaderboard_experiment(ctx)
        if len(res) == 0:
            raise click.ClickException(
                'There is no trials for the experiment: %s.' % (name))

        print_line('Use best trial to export model: {}'.format(res[0]))

        trial_id = res[0]['id']

    ctx.config = AugerConfig()
    project_id = start_project(ctx, create_if_not_exist= False)
    experiment_id, experiment_name = ctx.config.get_experiment()

    task_args = {
        'augerInfo': {'experiment_id': experiment_id, 'experiment_session_id': ctx.config.get_experiment_session_id()},
        "export_model_uid": trial_id
    }

    if deploy:
        create_cluster_task_ex(ctx, project_id,
                                            "auger_ml.tasks_queue.tasks.promote_pipeline_task", task_args
                                            )
        print("Waiting for deploy of pipeline: %s"%trial_id)
        wait_for_task_result(
            auger_client=ctx,
            endpoint=['pipelines', 'read'],
            params={'id': trial_id},
            first_status='creating_files',
            progress_statuses=[
                'creating_files', 'packaging', 'deploying'
            ],
            poll_interval=10
        )
        
        pipeline = read_pipeline(ctx, trial_id)        
        print("Pipeline {} status: {}; error: {}".format(pipeline.get('id'), pipeline.get('status'), pipeline.get('error_message')))
        return trial_id
    else:    
        model_path = create_cluster_task_ex(ctx, project_id,
                                            "auger_ml.tasks_queue.tasks.export_grpc_model_task", task_args
                                            )
        print(model_path)
        download_project_file(ctx, project_id, model_path, "models")


    return None


def predict_experiment(ctx, pipeline_id, trial_id, file):
    if pipeline_id is None:
        pipeline_id = export_model_experiment(ctx, trial_id, deploy=True)

    pipeline = read_pipeline(ctx, pipeline_id)
    if pipeline.get('status') != 'ready':
        print_line("Pipeline is not ready or has issues. Try to create another one.", err = True)
        print_record(pipeline, pipeline_attributes)
        return

    df = load_dataframe_from_file(file)

    prediction_id = create_prediction(ctx, pipeline_id, df.values.tolist(), df.columns.get_values().tolist())
    result = read_prediction(ctx, prediction_id)

    predict_path = os.path.splitext(file)[0] + "_predicted.csv"
    save_dict_to_csv(result.get('result', {}), predict_path)

    print("Predcition result saved to file: %s"%predict_path)

def monitor_leaderboard_experiment(ctx, name):
    pass
