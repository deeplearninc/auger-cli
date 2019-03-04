import unittest
import os

from auger_cli.auger_config import AugerConfig

class TestConfig(unittest.TestCase):

    def test_config_create(self):
        cur_dir = os.getcwd()
        os.chdir("./tests/fixtures/test_experiment")
        config = AugerConfig()

        self.assertEqual(config.experiment_name, "test_experiment")

        os.chdir(cur_dir)

    def test_update_ids_file(self):
        cur_dir = os.getcwd()
        os.chdir("./tests/fixtures/test_experiment")

        config = AugerConfig()
        config.update_ids_file({'test': 123})

        self.assertTrue(os.path.isfile(".auger_experiment_ids.yml"))

        os.chdir(cur_dir)
