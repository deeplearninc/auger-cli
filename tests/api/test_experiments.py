import unittest
import os
import mock

from auger_cli.api import experiments
from auger_cli.client import AugerClient
from auger_cli import constants
from tests.utils import init_test_api_client


class TestExperiments(unittest.TestCase):

    def test_read(self):
        init_test_api_client(self)

        def call_hub_api_ex(self, keys, params=None, validate=True, overrides=None,
                        action=None, encoding=None, transform=None):
            assert keys == ['experiments', 'read']
            assert params == {'id': 'exp1'}

            return {'data': {}}

        with mock.patch.object(AugerClient, 'call_hub_api_ex', call_hub_api_ex):
            res = experiments.read(self.client, experiment_id='exp1')
            print(res)
