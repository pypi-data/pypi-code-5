import logging
import socket

from handler import RequestHandler, HandlerFactory
from handler_pool import request_queue
try:
    from tcpyconfig import NUM_THREADS
except:
    from default import NUM_THREADS
try:
    from tcpyconfig import POLL_INTERVAL
except:
    from default import POLL_INTERVAL
try:
    from tcpyconfig import DEBUG
except:
    from default import DEBUG
from default import SERVER_DEFAULT, PORT_DEFAULT


logging.basicConfig()
logger = logging.getLogger("tcpy.TCPServer")
if DEBUG:
    logger.setLevel(logging.DEBUG)


class TCPServer(object):
    """
    Base Server class.  Listens for requests
    and queues them to be handled by a worker thread.
    """
    def __init__(self, host=None, port=None, **kwargs):
        self.host = host if host else SERVER_DEFAULT
        self.port = port if port else PORT_DEFAULT
        self.commands = kwargs.get("commands", {})
        threads = kwargs.get("threads", NUM_THREADS)
        poll_intv = kwargs.get("poll_intv", POLL_INTERVAL)
        self.request_queue = request_queue(threads, poll_intv)
        self.socket = None
        self.make_conn()

    def make_conn(self):
        """
        Open a socket and bind it to our address and port.
        """
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.host, self.port))
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.listen(5)

    def listen(self):
        print "TCPServer is listening at %s:%d!" % (self.host, self.port)
        hf = HandlerFactory(self.commands)
        while True:
            logging.debug("TCPServer accepting requests.")
            client_sock, client_addr = self.socket.accept()
            client_host, client_port = client_addr
            logging.debug("TCPServer handling request from %s:%s." % (client_host, client_port))
            handler = RequestHandler(hf,
                                     client_host,
                                     client_port,
                                     client_sock)
            self.request_queue.add(handler)
        self.socket.close()
