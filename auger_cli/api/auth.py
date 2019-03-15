
def login(client, email, password, url=None):
    if url is None:
        url = client.config.get_api_url()

    client.clear_credentials()
    client.setup_client(url)

    res = client.call_hub_api_ex('create_token', {'email': email, 'password': password})
    client.setup_client(url, res['data']['token'], email)


def logout(client):
    client.clear_credentials()

def whoami(client):
    if client.config.get_api_token() is None or len(client.config.get_api_token()) == 0:
        return None, None

    return client.config.get_api_username(), client.config.get_api_url()
