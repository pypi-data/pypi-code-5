import re
import stomp
from stomp.exception import ConnectionClosedException, ConnectFailedException, NotConnectedException, ProtocolException


class MiddlewareError(Exception):

    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class Middleware(object):
    "Message Oriented Middleware"

    destination = "/queue/elasticsearch,solr"

    def __init__(self, host, port):
        self.connection = stomp.Connection(host_and_ports=[(host, port)])
        self.host = host
        self.port = port
        self.connect()

    def notify(self, event):
        data = event.to_json()
        if self.not_connected():
            reconnected = self.connect()
            if not reconnected:
                return False
        try:
            self.connection.send(data, destination=self.destination)
        except (ConnectionClosedException, ConnectFailedException, NotConnectedException, ProtocolException) as e:
            msg = "ActiveMQ at {0}:{1} unavailable due to {2}.".format(self.host, self.port, str(e.__class__))
            raise MiddlewareError(msg)
        return True

    def connect(self):
        try:
            self.connection.start()
            self.connection.connect()
        except (ConnectionClosedException, ConnectFailedException, NotConnectedException, ProtocolException) as e:
            msg = "ActiveMQ at {0}:{1} reconnection failed with error {2}.".format(self.host, self.port, str(e.__class__))
            raise MiddlewareError(msg)
        return True

    def status(self):
        error = self.not_connected()
        if error:
            try:
                self.connect()
            except:
                msg = "ActiveMQ connection not-authenticated | FAILED | %s:%d | %s" % (self.host, self.port, error)
            else:
                error = ""
        if not error:
            msg = "ActiveMQ connection not-authenticated | SUCCEED | %s:%d" % (self.host, self.port)
        return msg

    def not_connected(self):
        try:
            self.connection.begin(transaction='123')
            self.connection.abort(transaction='123')
        except (ConnectionClosedException, ConnectFailedException, NotConnectedException, ProtocolException) as e:
            error = re.sub('<class|>', '', str(e.__class__))
        else:
            error = ""
        return error
