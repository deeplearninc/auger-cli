# -*- coding: utf-8 -*-

class BaseStream():
    """
    Derived classes should implement get_strem(), returning IOStream-like object
    """
    def get_stream(self):
        raise NotImplemented

class ApiStream(BaseStream):
    def __init__(self, client):
        self.__client = client

    def get_stream(self, project_id):
        return self.__client.call_hub_api_ex('get_pod_logs', params={'project_id': project_id})

class WebSocketStream(BaseStream):
    # TODO: implement long-live websocket connection reader
    # def get_stream(self, client):
    pass
