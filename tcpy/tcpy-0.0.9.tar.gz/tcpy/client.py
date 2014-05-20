from connection import ClientConnection
from default import SERVER_DEFAULT, PORT_DEFAULT
from util import to_int


class TCPClient(object):
    """
    Abstracts connection to a server through a socket
    """

    def __init__(self, host=SERVER_DEFAULT, port=PORT_DEFAULT):
        self.host = host
        self.port = to_int(port)
        self._conn = ClientConnection(self.host, self.port)

    def connect(self):
        self._conn.connect()

    def send(self, data):
        self._conn.send(data)

    def recv(self):
        return self._conn.read()

    def disconnect(self):
        self._conn.finish()

    def execute(self, cmd, **params):
        params['cmd'] = cmd
        self.connect()
        self.send(params)
        res = self.recv()
        self.disconnect()
        return res
