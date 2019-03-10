import pytest

from auger_cli.config import AugerConfig
from auger_cli.client import AugerClient


@pytest.fixture(scope="class")
def test_api_client(request):
    client = AugerClient(AugerConfig(config_dir="tests/fixtures/test_experiment", 
        config_settings={'login_config_path': "tests/fixtures/test_experiment"}))

    request.cls.client = client
    return client
