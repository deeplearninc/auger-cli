import unittest
import os
import mock

from auger_cli.api import experiments
from auger_cli.client import AugerClient
from tests.utils import init_test_api_client


class TestExperiments(unittest.TestCase):

    def test_read(self):
        init_test_api_client(self)

        def call_hub_api_ex(self, method, params=None):
            assert method == 'get_experiment'
            assert params == {'id': 'exp1'}

            return {'data': {}}

        with mock.patch.object(AugerClient, 'call_hub_api_ex', call_hub_api_ex):
            res = experiments.read(self.client, experiment_id='exp1')
            print(res)
