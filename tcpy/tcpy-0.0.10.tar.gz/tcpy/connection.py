import logging
import msgpack as umsgpack
import socket
import time

from util import msgpk_decode_datetime, msgpk_encode_datetime
try:
    from tcpyconfig import DEBUG
except:
    from default import DEBUG

MAX_ATTEMPTS = 20
logging.basicConfig()
logger = logging.getLogger("tcpy.connection")
if DEBUG:
    logger.setLevel(logging.DEBUG)


def prefix_to_len(prefix):
    "Converts a 4 byte big-endian value, to native"
    return ord(prefix[0]) << 24 | \
        ord(prefix[1]) << 16 | \
        ord(prefix[2]) << 8  | \
        ord(prefix[3])


def len_to_prefix(length):
    "Converts length to a 4 byte big-endian value"
    parts = "".join([
        chr(length >> 24 & 0xff),
        chr(length >> 16 & 0xff),
        chr(length >> 8 & 0xff),
        chr(length & 0xff)])
    return parts


def recv_bytes(sock, bytes):
    "Receive at least bytes"
    buf = ""
    while len(buf) < bytes:
        diff = bytes - len(buf)
        more = sock.recv(diff)
        if not more:
            raise Exception("Socket closed!")
        buf += more
    return buf


class ClientConnectionError(Exception):
    pass


class ClientConnection(object):

    """ Client Connection wrapper class for nice send/read interface """

    def __init__(self, host, port, timeout=None):
        self.host = host
        self.port = port
        self.sock = None
        self.attempts = 0
        self.timeout = timeout

    def _connect(self):
        if self.sock:
            return

        self.sock = self._create_socket()

    def _create_socket(self):
        try:
            logger.debug("Creating socket for client. %s")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            logger.debug("Socket created successfully.")
            sock.settimeout(self.timeout)
            logger.debug("Trying to connect socket to %s:%s." % (self.host, self.port))
            sock.connect((self.host, self.port))
            logger.debug("Successfully connected.")
            # we need to set the timeout once again after connecting
            sock.settimeout(self.timeout)

            return sock
        except socket.error:
            self._disconnect()
            raise ClientConnectionError('Unable to create or connect socket')

    def _disconnect(self):
        logger.debug("Closing socket.")

        if self.sock is None:
            return

        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except socket.error:
            logger.debug("Error closing socket.")
            pass

        self.sock = None

    def send(self, data):
        msg = umsgpack.packb(data, default=msgpk_encode_datetime)

        while self.attempts <= MAX_ATTEMPTS:
            try:
                self._connect()
                logger.debug("Client sending bytes to server.")
                self.sock.sendall(len_to_prefix(len(msg)))
                self.sock.sendall(msg)
                logger.debug("Client sent %s bytes to server." % len(msg))
                self.attempts = 0
                return
            except socket.error:
                logger.debug("Failed to send data to server -- Retrying.")
                self.attempts += 1
                self._disconnect()
                if self.attempts >= MAX_ATTEMPTS:
                    raise Exception('Max number of retries reached!')
            time.sleep(.01)

    def read(self):
        try:
            logger.debug("Client waiting for bytes from server.")
            msgprefix = self.sock.recv(4)
            msglen = prefix_to_len(msgprefix)
            response = recv_bytes(self.sock, msglen)
            logger.debug("Client received %s bytes from server." % msglen)
        except:
            self._disconnect()
            raise ClientConnectionError('Error reading from server.')

        return umsgpack.unpackb(response, object_hook=msgpk_decode_datetime)


class ServerConnection(object):

    """ Server Connection wrapper class for nice send/read interface.
    Different from the ClientConnection in that it will not retry to send.
    """

    def __init__(self, cl_host, cl_port, cl_sock):
        self.host = cl_host
        self.port = cl_port
        self.sock = cl_sock

    def send(self, data):
        msg = umsgpack.packb(data, default=msgpk_encode_datetime)

        try:
            logger.debug("Server sending bytes to client.")
            self.sock.sendall(len_to_prefix(len(msg)))
            self.sock.sendall(msg)
            logger.debug("Server sent %s bytes to client." % len(msg))
        except socket.error:
            logger.exception('ServerConnection failed to send %s.' % data)
            self.finish()

    def read(self):
        try:
            logger.debug("Server waiting for bytes from client.")
            msgprefix = self.sock.recv(4)
            msglen = prefix_to_len(msgprefix)
            response = recv_bytes(self.sock, msglen)
            logger.debug("Server received %s bytes from client." % msglen)
        except Exception as e:
            msg = e.message if e.message else "Error reading from client"
            raise Exception(msg)

        return umsgpack.unpackb(response, object_hook=msgpk_decode_datetime)

    def finish(self):
        if self.sock is None:
            return

        logger.debug("Closing socket.")
        try:
            self.sock.shutdown(socket.SHUT_RDWR)
            self.sock.close()
        except socket.error:
            logger.debug("Error closing socket.")
            pass
