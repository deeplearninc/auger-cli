import unittest
import os
import mock

from auger_cli.api import auth
from auger_cli.client import AugerClient
from auger_cli import constants
from tests.utils import init_test_api_client

class TestAuth(unittest.TestCase):

    def test_login(self):
        init_test_api_client(self)
        def call_hub_api_ex(self, method, params={}):
            assert method == 'create_token'
            return {'data': {'token': 'topsecret'}}

        with mock.patch.object(AugerClient, 'call_hub_api_ex', call_hub_api_ex):
            auth.login(self.client, "user", "pwd", url=constants.TEST_API_URL)
