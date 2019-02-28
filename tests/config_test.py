import unittest
import os

from auger_cli.auger_config import AugerConfig


class TestConfig(unittest.TestCase):

    def test_config_create(self):
        os.chdir("./tests/fixtures/test_experiment")
        config = AugerConfig()

        # self.assertEqual(0, result.exit_code)
        # self.assertTrue(
        #     result.output.endswith('You are now logged in on localhost as valid@auger.ai.\n')
        # )

    def test_update_ids_file(self):
        config = AugerConfig()
        config.update_ids_file({'test': 123})
