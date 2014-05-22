import logging

from connection import ServerConnection


logging.basicConfig()
logger = logging.getLogger(__name__)


class TCPHandler(object):
    """
    Abstract base class to be extended by Handler classes.
    Exposes the execute() method which will be called by
    the TCPServer on handler associated with a given command.
    """

    def __init__(self, **kwargs):
        self.conn = None

    def send(self, data):
        self.conn.send(data)

    def recv(self):
        return self.conn.read()

    def execute(self):
        """ Must be overridden by subclasses. """
        raise NotImplementedError()

    def success(self, **kwargs):
        """ Provide a wrapper for well-formed success responses """
        res = {
            'success': True,
        }
        res.update(kwargs)
        return res

    def error(self, message, **kwargs):
        """ Provide a wrapper for well-formed error dicts """
        res = {
            'error': True,
            'message': message
        }
        res.update(kwargs)
        return res


class HandlerFactory(object):
    """
    Factory for creating handlers that will
    execute specific commands.
    """
    def __init__(self, commands):
        self.commands = commands

    def make_handler(self, cmd=None, **kwargs):
        """
        Return a class that can execute a given command.
        """
        if not cmd or cmd not in self.commands:
            raise Exception("Invalid command %s!" % cmd)

        return self.commands.get(cmd)(**kwargs)


class RequestHandler(object):
    """
    Abstraction for handling a request to a TCPServer instance.
    """

    def __init__(self, factory, host, port, sock):
        self.factory = factory
        self.conn = ServerConnection(host, port, sock)

    def handle(self):
        try:
            data = self.conn.read()
            handler = self.factory.make_handler(**data)
            handler.conn = self.conn
            res = handler.execute()
        except Exception as e:
            logger.error(e.message)
            res = {"error": True, "message": e.message}
        self.conn.send(res)
