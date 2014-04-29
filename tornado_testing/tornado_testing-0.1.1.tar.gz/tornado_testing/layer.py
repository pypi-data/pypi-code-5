
from tornado.ioloop import IOLoop
from multiprocessing import Process
from socket import socket
from telnetlib import Telnet
from time import sleep


def get_port_number():
    """
    returns a free port number
    """
    sock = socket()
    sock.bind(('', 0))
    return sock.getsockname()[1]


class TornadoLayer:

    """ A test layer to be used with the zope.testrunner. """

    __bases__ = ()
    __name__ = 'tornado'

    class TornadoProcess(Process):

        def __init__(self, app, port, patches):
            super().__init__()
            self.app = app
            self.port = port
            self.patches = patches or []
            for patch in self.patches:
                patch.start()

        def terminate(self):
            for patch in self.patches:
                patch.stop()
            super().terminate()

        def run(self):
            self.app.listen(self.port)
            self.instance = IOLoop.instance()
            self.instance.start()

    def __init__(self, app, port=None, patches=None):
        """
        :param app: the tornado application that should be run.
        :param port: the port number on which the application should be run. If
                     None a free port number will be used.
        :param patches: a list of patches (from the mock package) that should be
                        started/registered when starting the tornado layer.
        """
        self.port = port or get_port_number()
        self.process = TornadoLayer.TornadoProcess(app, self.port, patches)

    def setUp(self):
        self.process.start()
        retries = 0
        # wait till tornado has been started
        while True:
            try:
                Telnet('localhost', self.port)
            except ConnectionRefusedError:
                retries += 1
                if retries > 40:
                    break
                sleep(0.020)
            else:
                break

    def tearDown(self):
        self.process.terminate()
