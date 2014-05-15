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
        self.conn = ClientConnection(self.host, self.port)

    def send(self, data):
        self.conn.send(data)

    def recv(self):
        return self.conn.read()

    def execute(self, cmd=None, **params):
        if not cmd:
            raise Exception("No command provided to execute function!")

        params['cmd'] = cmd
        self.conn.connect()
        self.send(params)
        res = self.recv()
        self.conn.finish()
        return res
