import unittest
import os

from auger_cli.config import AugerConfig

class TestConfig(unittest.TestCase):

    def test_config_create(self):
        config = AugerConfig(config_dir="tests/fixtures/test_experiment")

        self.assertEqual(config.experiment_name, "test_experiment")


    def test_config_create2(self):
        config_settings = {'evaluation_options':{'feature_columns':['sepal_length', 'sepal_width']}}
        config = AugerConfig(config_dir="tests/fixtures/test_experiment", 
            config_settings=config_settings)

        self.assertEqual(config.experiment_name, "test_experiment")
        self.assertEqual(config.get_evaluation_options().get('featureColumns'), 
            config_settings.get('evaluation_options').get('feature_columns'))
        self.assertEqual(config.get_evaluation_options().get('data_path'), 
            'files/iris_data_sample.csv')

    def test_update_session_file(self):
        config = AugerConfig(config_dir="tests/fixtures/test_experiment")
        settings = {'test': 123}
        config.update_session_file(settings)

        self.assertTrue(os.path.isfile(config.exp_session_path))
        self.assertEqual(config.config_session, settings)

    def test_get_space_definition(self):
        config = AugerConfig()

        res = config.get_space_definition()
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 6, 'non_mt': 4}))

        res = config.get_space_definition({'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer']})
        self.assertEqual(res, ({'batch': 0, 'seq': 1}, {'mt': 6, 'non_mt': 4}))
        
        res = config.get_space_definition({'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer']})
        self.assertEqual(res, ({'batch': 1, 'seq': 0}, {'mt': 6, 'non_mt': 4}))

        res = config.get_space_definition({'optimizers_names': 
            [
                'auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer',
                'auger_ml.optimizers.pso_optimizer.PSOOptimizer',
                'auger_ml.optimizers.warmstart_optimizer.WarmStartOptimizer'
            ]})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 6, 'non_mt': 4}))

        res = config.get_space_definition({'model_type': 'classification'})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 6, 'non_mt': 4}))

        res = config.get_space_definition({'model_type': 'regression'})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 5, 'non_mt': 5}))

        res = config.get_space_definition({'model_type': 'timeseries'})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 5, 'non_mt': 6}))

        res = config.get_space_definition({'search_space': {'sklearn.linear_model.LogisticRegression': {}}})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 1, 'non_mt': 0}))

        res = config.get_space_definition({'search_space': {'sklearn.linear_model.LogisticRegression': {}, 'auger_ml.algorithms.svm.SVC':{}}})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 1, 'non_mt': 1}))

        res = config.get_space_definition({'search_space': {'sklearn.linear_model.LogisticRegression': {}, 'xgboost.XGBClassifier':{}}})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 2, 'non_mt': 0}))

        res = config.get_space_definition({'search_space': {'auger_ml.algorithms.svm.SVC':{}}})
        self.assertEqual(res, ({'batch': 1, 'seq': 1}, {'mt': 0, 'non_mt': 1}))

    def test_get_worker_types(self):
        config = AugerConfig()

        res = config.get_worker_types({"instance_type":'c5.large', "worker_nodes_count": 3},None)
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 3}})

        res = config.get_worker_types({"instance_type":'c5.2xlarge', "worker_nodes_count": 3},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer'],
            }
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 4}, '3': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=3', 'worker_count': 5}, '2': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=2', 'worker_count': 1}})

        res = config.get_worker_types({"instance_type":'c5.xlarge', "worker_nodes_count": 3},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 3}})
        res = config.get_worker_types({"instance_type":'c5.xlarge', "worker_nodes_count": 3},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}, 'auger_ml.algorithms.svm.LinearSVC':{}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 3}})

        res = config.get_worker_types({"instance_type":'c5.4xlarge', "worker_nodes_count": 6},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer', 'auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
            }
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 8}, '7': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=7', 'worker_count': 10}, '6': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=6', 'worker_count': 2}})

        res = config.get_worker_types({"instance_type":'c5.xlarge', "worker_nodes_count": 3},
            {'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 9}})

        res = config.get_worker_types({"instance_type":'c5.xlarge', "worker_nodes_count": 3},
            {'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}, 'sklearn.linear_model.LogisticRegression': {}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 3}, '2': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=2', 'worker_count': 3}})

        res = config.get_worker_types({"instance_type":'c5.4xlarge', "worker_nodes_count": 10},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer'],
            }
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 10}, '14': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=14', 'worker_count': 10}})

        res = config.get_worker_types({"instance_type":'c5.4xlarge', "worker_nodes_count": 10},
            {'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
             'search_space':{'sklearn.linear_model.LogisticRegression': {}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 10}, '14': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=14', 'worker_count': 10}})

        res = config.get_worker_types({"instance_type":'c5.xlarge', "worker_nodes_count": 30},
            {'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}, 'sklearn.linear_model.LogisticRegression': {}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 30}, '2': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=2', 'worker_count': 30}})

        res = config.get_worker_types({"instance_type":'c5.4xlarge', "worker_nodes_count": 50},
            {'optimizers_names': ['auger_ml.optimizers.de_optimizer.DEOptimizer'],
            }
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 50}, '14': {'worker_args': '--queues evaluate_trials_mt --auger-worker-cpu=14', 'worker_count': 50}})

        res = config.get_worker_types({"instance_type":'c5.4xlarge', "worker_nodes_count": 30},
            {'optimizers_names': ['auger_ml.optimizers.hyperopt_async_optimizer.HyperoptAsyncOptimizer'],
             'search_space':{'auger_ml.algorithms.svm.SVC':{}}}
        )
        self.assertEqual(res, {'1': {'worker_args': '--queues evaluate_trials,augerml_api', 'worker_count': 450}})
