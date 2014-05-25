# Copyright 2014 Dan Kilman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fcntl
import sys
import time
import uuid
import select
import os
import json
import socket
import errno
from SocketServer import (ThreadingUnixStreamServer,
                          StreamRequestHandler)
from io import BytesIO
from StringIO import StringIO
import traceback

import pysource
from pysource import config
from pysource import remote_call_handlers
from pysource import request_context


RESPONSE_STATUS_OK = "ok"
RESPONSE_STATUS_ERROR = "error"

CONTROL_SOCKET_ERROR_CODE = 1
CONTROL_SOCKET_LENGTH_CODE = 2

unix_socket_path = lambda: os.path.join(config.pysource_dir, 'socket')


DEBUG = False
DEBUG_CLIENT = True
DEBUG_SERVER = False


def _handle(req_type, payload, **kwargs):
    handler = remote_call_handlers.get(req_type)
    if handler is None:
        raise RuntimeError('Unknown request type: {0}'.format(req_type))
    return handler(**payload)


class RequestHandler(StreamRequestHandler):

    def __init__(self, request, client_address, server):
        self.pipe_control_handler = None
        StreamRequestHandler.__init__(self, request, client_address, server)

    def handle(self):
        try:
            res_status = RESPONSE_STATUS_OK
            body = _read_body(self.rfile)
            if body['piped'] is True:
                request_context.piped = True
                self.pipe_control_handler = \
                    PipeControlSocketHandler(body['uid'])
                self._handle_piped(body, self.pipe_control_handler)
                res_payload = {}
            else:
                res_payload = _handle(**body)
        except Exception:
            res_status = RESPONSE_STATUS_ERROR
            error = StringIO()
            error.write('daemon: ')
            traceback.print_exc(file=error)
            res_payload = {'error': error.getvalue()}

        if self.pipe_control_handler:
            response_file = self.pipe_control_handler.wfile
            if res_status == RESPONSE_STATUS_ERROR:
                try:
                    self.wfile.flush()
                except socket.error:
                    pass
                response_file.write('{}\r\n'.format(CONTROL_SOCKET_ERROR_CODE))
                response_file.flush()
        else:
            response_file = self.wfile
        _write_body(response_file, {
            'payload': res_payload,
            'status': res_status
        })

    def finish(self):
        StreamRequestHandler.finish(self)
        if self.pipe_control_handler:
            self.pipe_control_handler.close()

    def _handle_piped(self, body, pipe_control_handler):
        self.connection.setblocking(0)
        try:
            pipe_control_handler.accept()
            piped_input = PipeControlledInputSocket(
                self.rfile,
                self.connection,
                pipe_control_handler.rfile,
                pipe_control_handler.conn)
            piped_output = PipeControlledOutputSocket(
                self.wfile,
                self.connection,
                pipe_control_handler.wfile,
                pipe_control_handler.conn)
            request_context.stdin = piped_input
            request_context.stdout = piped_output
            result = _handle(**body)
            if result is not None:
                piped_output.write(result)
            piped_input.close()
            piped_output.close()
        finally:
            self.connection.setblocking(1)
            pipe_control_handler.conn.setblocking(1)


class PipeControlSocketHandler(object):

    def __init__(self, uid):
        self.uid = uid
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.unix_socket_path = os.path.join(config.pysource_dir, self.uid)
        self.conn = None
        self.wfile = None
        self.rfile = None
        self.server = True

    def accept(self):
        self.sock.bind(self.unix_socket_path)
        self.sock.listen(1)
        conn, addr = self.sock.accept()
        self._setup(conn)

    def connect(self):
        self.server = False
        retries = 20
        current_tries = 0
        while True:
            try:
                current_tries += 1
                self.sock.connect(self.unix_socket_path)
                break
            except socket.error, e:
                if e.errno == errno.ENOENT and current_tries < retries:
                    time.sleep(0.1)
                else:
                    raise

        self._setup(self.sock)

    def _setup(self, conn):
        self.conn = conn
        self.conn.setblocking(0)
        self.rfile = self.conn.makefile('rb', -1)
        self.wfile = self.conn.makefile('wb', 0)

    def close(self):
        if not self.wfile.closed:
            try:
                self.conn.setblocking(1)
                self.wfile.flush()
            except socket.error:
                pass
        self.wfile.close()
        self.rfile.close()
        if self.server:
            try:
                self.conn.shutdown(socket.SHUT_WR)
            except socket.error:
                pass
            try:
                self.sock.close()
            except socket.error:
                pass
        self.conn.close()
        if self.server and os.path.exists(self.unix_socket_path):
            os.remove(self.unix_socket_path)


class PipeControlledBaseSocket(object):

    def __init__(self, data_file, data_socket, control_file, control_socket):
        self.closed = False
        self.data_file = data_file
        self.data_socket = data_socket
        self.control_file = control_file
        self.control_socket = control_socket
        self.sockets = [self.data_socket, self.control_socket]


class PipeControlledInputSocket(PipeControlledBaseSocket):

    def __init__(self, data_file, data_socket, control_file, control_socket):
        super(PipeControlledInputSocket, self).__init__(data_file,
                                                        data_socket,
                                                        control_file,
                                                        control_socket)
        self.bytes_read = 0
        self.total_bytes = None
        self.done = False
        self.read_sockets = self.sockets
        self.control_consumed = False

    def p(self, message):
        if DEBUG and ((DEBUG_CLIENT and not request_context.piped) or
                      (DEBUG_SERVER and request_context.piped)):
            prefix = '(SERVER_IN)' if request_context.piped else '(CLIENT_IN)'
            print '{} {} (total_bytes={}, bytes_read={}, done={})'.format(
                prefix, message, self.total_bytes, self.bytes_read, self.done)

    def read(self, length=0, blocking=True):
        self.p('read length={}, blocking={}'.format(
            length, blocking))
        if self.done:
            return ''
        result = BytesIO()
        while True:
            self.p('loop')
            if self.bytes_read == self.total_bytes:
                break
            timeout = 30 if blocking else 0
            readable, _, _ = select.select(self.read_sockets, [], [], timeout)
            if self.control_socket in readable:
                self.read_sockets = [self.data_socket]
                total_bytes = self.consume_control()
                if total_bytes == -1:  # error
                    self.total_bytes = self.bytes_read
                    break
                else:
                    self.total_bytes = total_bytes
                self.p('total_bytes={}'.format(self.total_bytes))
            if self.data_socket in readable:
                to_read = 1024 if length <= 0 else length - result.tell()
                if self.total_bytes and self.total_bytes < to_read:
                    to_read = self.total_bytes
                try:
                    data = self.data_socket.recv(to_read)
                    self.p('data={}, len={}'.format(data, len(data)))
                    self.bytes_read += len(data)
                    result.write(data)
                except socket.error, e:
                    if e.errno == errno.EAGAIN:
                        self.p('errno.EAGAIN blocking={}'.format(
                            blocking))
                        if blocking:
                            pass
                        else:
                            break
                    else:
                        raise
                if 0 < length == result.tell():
                    break
            if len(readable) == 0 and not blocking:
                break
        if self.bytes_read == self.total_bytes:
            self.done = True
        self.p('out done={}, bytes_read={}, total_bytes={}'.format(
            self.done, self.bytes_read, self.total_bytes))
        value = result.getvalue()
        if len(value) == 0:
            if self.done:
                return ''
            else:
                return None
        else:
            return result.getvalue()

    def consume_control(self):
        if self.control_consumed:
            return -2
        self.control_consumed = True
        self.control_socket.setblocking(1)
        try:
            control_code = int(self.control_file.readline())
            self.p('control_code={}'.format(control_code))
            if control_code == CONTROL_SOCKET_ERROR_CODE:
                return -1
            else:
                return int(self.control_file.readline())
        finally:
            self.control_socket.setblocking(0)

    def close(self):
        self.p('read_close done={}, bytes_read={}, total_bytes={}'.format(
            self.done, self.bytes_read, self.total_bytes))


class PipeControlledOutputSocket(PipeControlledBaseSocket):

    def __init__(self, data_file, data_socket, control_file, control_socket):
        super(PipeControlledOutputSocket, self).__init__(data_file,
                                                         data_socket,
                                                         control_file,
                                                         control_socket)
        self.bytes_written = 0

    def p(self, message):
        if DEBUG and ((DEBUG_CLIENT and not request_context.piped) or
                      (DEBUG_SERVER and request_context.piped)):
            prefix = '(SERVER_OUT)' if request_context.piped else \
                '(CLIENT_OUT)'
            print '{} {}'.format(prefix, message)

    def write(self, data):
        self.p('write data={}'.format(data))
        view = memoryview(data)
        total_bytes_to_write = len(view)
        total_sent = 0
        while True:
            if total_sent == total_bytes_to_write:
                break
            _, writable, _ = select.select([], [self.data_socket], [], 30)
            if self.data_socket in writable:
                sent = self.data_socket.send(view[total_sent:])
                total_sent += sent
        self.bytes_written += total_bytes_to_write
        self.p('write out bytes_written={}'.format(self.bytes_written))

    def close(self):
        self.p('write close bytes_written={}'.format(self.bytes_written))
        self.control_socket.setblocking(1)
        try:
            length_control_message = '{}\r\n{}\r\n'.format(
                CONTROL_SOCKET_LENGTH_CODE, self.bytes_written)
            self.control_file.write(length_control_message)
            self.control_file.flush()
        finally:
            self.control_socket.setblocking(0)


def do_regular_client_request(req_type, payload):
    return _do_client_request(req_type, payload)


def do_piped_client_request(req_type, payload):

    def p(message):
        if DEBUG:
            print '(CLIENT) {}'.format(message)

    def pipe_handler(sock, req, res, uid):
        sock.setblocking(0)
        try:
            pipe_control_handler = PipeControlSocketHandler(uid)
            pipe_control_handler.connect()
            piped_output = PipeControlledOutputSocket(
                req,
                sock,
                pipe_control_handler.wfile,
                pipe_control_handler.conn)
            piped_input = PipeControlledInputSocket(
                res,
                sock,
                pipe_control_handler.rfile,
                pipe_control_handler.conn)

            stdin_fd = sys.stdin.fileno()
            stdin_buf = 16 * 1024
            fl = fcntl.fcntl(stdin_fd, fcntl.F_GETFL)
            fcntl.fcntl(stdin_fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

            data_sock = sock
            data_sock_buf = 1024
            control_soc = pipe_control_handler.conn
            control_soc_written = False

            read_sockets = [stdin_fd, data_sock, control_soc]

            while True:
                readable = select.select(read_sockets, [], [], 30)[0]
                if stdin_fd in readable:
                    stdin_read = os.read(stdin_fd, stdin_buf)
                    if stdin_read == '':
                        piped_output.close()
                        read_sockets = [data_sock, control_soc]
                    elif stdin_read is not None:
                        piped_output.write(stdin_read)
                if control_soc in readable:
                    control_soc_written = True
                if data_sock in readable:
                    if control_soc_written:
                        buf = piped_input.read()
                    else:
                        buf = piped_input.read(data_sock_buf,
                                               blocking=False)
                    if buf is '':
                        break
                    elif buf is not None:
                        sys.stdout.write(buf)
                        try:
                            sys.stdout.flush()
                        except IOError, e:
                            if e.errno == errno.EPIPE:
                                raise pysource.error('Flushing stdout failed.'
                                                     ' It seems the process'
                                                     ' being piped to, '
                                                     'terminated.')
                            else:
                                raise
                if control_soc_written:
                    break

            piped_input.consume_control()
            piped_input.close()
            pipe_control_handler.conn.setblocking(1)
            return pipe_control_handler
        finally:
            sock.setblocking(1)
    return _do_client_request(req_type, payload, pipe_handler)


def _do_client_request(req_type, payload, pipe_handler=None):
    sock = _client_connect()
    req = sock.makefile('wb', 0)
    res = sock.makefile('rb', -1)
    piped = pipe_handler is not None
    uid = str(uuid.uuid4())
    try:
        _write_body(req, {
            'req_type': req_type,
            'payload': payload,
            'piped': piped,
            'uid': uid
        })
        if piped:
            pipe_control_handler = pipe_handler(sock, req, res, uid)
            res_body = _read_body(pipe_control_handler.rfile)
            pipe_control_handler.close()
        else:
            res_body = _read_body(res)
        res_body_payload = res_body['payload']
        if res_body['status'] == RESPONSE_STATUS_ERROR:
            error = res_body_payload['error']
            raise pysource.error('{0}'.format(error))
        return res_body_payload
    finally:
        req.close()
        res.close()
        sock.close()


def _client_connect():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        sock.connect(unix_socket_path())
    except socket.error, e:
        if e.errno in [errno.ENOENT, errno.ECONNREFUSED]:
            raise pysource.error('Is the pysource daemon running? '
                                 'Run "pysource daemon start" to start '
                                 'it.')
        else:
            raise
    return sock


def _read_body(sock):
    json_body_len = int(sock.readline())
    return json.loads(sock.read(json_body_len))


def _write_body(sock, body):
    json_body = json.dumps(body)
    json_body_len = len(json_body)
    sock.write(json_body_len)
    sock.write('\r\n')
    sock.write(json_body)


def start_server():
    server = ThreadingUnixStreamServer(unix_socket_path(),
                                       RequestHandler)
    server.serve_forever()


def cleanup():
    """Used for forced cleanup"""
    if os.path.exists(unix_socket_path()):
        try:
            os.remove(unix_socket_path())
        except (OSError, IOError), e:
            # could happen in tests
            if e.errno == errno.ENOENT:
                pass
            else:
                raise
