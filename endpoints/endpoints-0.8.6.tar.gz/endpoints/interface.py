import os
from BaseHTTPServer import BaseHTTPRequestHandler
import socket

from .http import Request, Response
from .call import Call

import pout


class BaseInterface(object):
    def __init__(self, controller_prefix='', *args, **kwargs):
        self.controller_prefix = controller_prefix

    def handle(self, *args, **kwargs):
        raise NotImplemented()

    def get_request_instance(self, *args, **kwargs):
        raise NotImplemented()

    def get_call_instance(self, *args, **kwargs):
        if not self.controller_prefix:
            self.controller_prefix = os.environ.get('ENDPOINTS_PREFIX', '')

        c = Call(self.controller_prefix)
        c.request = self.get_request_instance(*args, **kwargs)
        return c


class WSGI(BaseInterface):
    def handle(self, environ, start_response):
        c = self.get_call_instance(environ)
        res = c.handle()

        start_response(
            '{} {}'.format(res.code, res.status),
            [(k, v) for k, v in res.headers.iteritems()]
        )
        return [res.body]

    def get_request_instance(self, environ, *args, **kwargs):
        r = Request()
        for k, v in environ.iteritems():
            if k.startswith('HTTP_'):
                r.headers[k[5:]] = v

        r.method = environ['REQUEST_METHOD']
        r.path = environ['PATH_INFO']
        r.query = environ['QUERY_STRING']
        r.environ = environ

        if r.is_method('POST'):
            r.body = environ['wsgi.input'].read()

        return r

    def __call__(self, environ, start_response):
        return self.handle(environ, start_response)


class PythonHTTP(BaseHTTPRequestHandler, BaseInterface):

    def handle(self, *args, **kwargs):
        try:
            self.raw_requestline = self.rfile.readline(65537)
            if not self.raw_requestline:
                self.close_connection = 1
                return

            if not self.parse_request():
                # An error code has been sent, just exit
                return

            req = Request()
            req.path = path
            req.query = query
            req.method = self.command
            req.headers = self.headers.dict

            c = self.get_call_instance()
            res = c.handle()

            self.send_response(res.code)
            for h, hv in res.headers.iteritems():
                self.send_header(h, hv)

            #self.send_header('Connection', 'close')
            self.end_headers()

            body = res.body
            if body:
                self.wfile.write(res.body)
                self.wfile.flush()

        except socket.timeout, e:
            self.log_error("Request timed out: %r", e)
            self.close_connection = 1
            return

    def get_request_instance(self, *args, **kwargs):
        if '?' in self.path:
            path, query = self.path.split('?', 1)
        else:
            path = self.path
            query = ""

        r = Request()
        r.path = path
        r.query = query
        r.method = self.command
        r.headers = self.headers.dict

        if r.is_method('POST'):
            pout.v(self)

        return r

    def handle_one_request(self):
        return self.handle()
