from ..utils import urlparse, b64encode, b64decode

def login(client, url, username, password):
    client.clear_credentials()

    # extract host name from server URL
    parsed = urlparse(url)
    host = parsed.hostname
    creds_string = "{0}:{1}".format(username, password)
    header = 'Basic ' + b64encode(creds_string)

    # reload client
    credentials = {}
    credentials[host] = header
    client.set_credentials(credentials)
    client.setup_client(url)

    # make test call
    client.call_hub_api(['organizations', 'list'])

def logout(client):
    client.clear_credentials()

def whoami(client):
    username = None
    host = None
    creds = client.get_credentials()
    for host, cred in creds.items():
        decoded = b64decode(cred.split(' ')[1])
        username = decoded.split(':')[0]

    return username, host    
