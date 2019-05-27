# -*- coding: utf-8 -*-

class BaseStream():
    """
    Derived classes should implement get_strem(), returning IOStream-like object
    """
    def get_stream(self):
        raise NotImplemented

class ApiStream(BaseStream):
    def __init__(self, client, limit=10000):
        self.__client = client
        self.__limit = limit

    def get_stream(self, project_id):
        # return self.__client.call_hub_api_ex('get_pod_logs', params={'project_id': project_id})
        offset = 0
        while True:
            page = self.__client.call_hub_api_ex('get_pod_logs', params={'project_id': project_id, 'limit': self.__limit, 'offset': offset})
            yield page
            pagination = page['meta']['pagination']
            offset += self.__limit
            if pagination['total'] <= offset:
                break


class WebSocketStream(BaseStream):
    # TODO: implement long-live websocket connection reader
    # def get_stream(self, client):
    pass
