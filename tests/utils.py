
from auger_cli.config import AugerConfig
from auger_cli.client import AugerClient


def init_test_api_client(obj):
    client = AugerClient(AugerConfig(config_dir="tests/fixtures/test_experiment", 
        config_settings={'login_config_path': "tests/fixtures/test_experiment"}))

    obj.client = client
    return client
