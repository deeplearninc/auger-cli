from auger_cli.utils import urlparse, b64encode, b64decode
from auger_cli.constants import DEFAULT_API_URL


def login(client, email, password, url=DEFAULT_API_URL):
    client.clear_credentials()
    client.setup_client(url)

    res = client.call_hub_api_ex('create_token', {'email': email, 'password': password})
    client.setup_client(url, res['data']['token'])


def logout(client):
    client.clear_credentials()
