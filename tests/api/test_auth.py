import unittest
import os
import mock
import pytest

from auger_cli.api import auth
from auger_cli.client import AugerClient
from auger_cli import constants


pytestmark = pytest.mark.usefixtures('test_api_client')

class TestAuth(unittest.TestCase):

    def test_login(self):
        def call_hub_api_ex(self, keys, params=None, validate=True, overrides=None,
                        action=None, encoding=None, transform=None):
            assert keys == ['organizations', 'list']
            return {'data': {}}

        with mock.patch.object(AugerClient, 'call_hub_api_ex', call_hub_api_ex):
            auth.login(self.client, "user", "pwd", url=constants.TEST_COREAPI_URL)
