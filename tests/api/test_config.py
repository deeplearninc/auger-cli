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
