import sys
from base import WebSocketDataFilter


class BroadcastMessageFilter(WebSocketDataFilter):

    @classmethod
    def filter(cls, web_socket_instance, data):
        sys.stdout.writelines("--RAWDATA--\n%s\n" % data)
        sys.stdout.flush()
