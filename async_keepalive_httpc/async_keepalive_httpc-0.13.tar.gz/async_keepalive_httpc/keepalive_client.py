#!/usr/bin/env python
from __future__ import absolute_import, division, print_function, with_statement

from tornado.escape import utf8, _unicode, native_str
from tornado.httpclient import HTTPResponse, HTTPError, _RequestProxy, HTTPRequest
from tornado import httputil
from tornado.iostream import IOStream, SSLIOStream
from tornado.netutil import Resolver, OverrideResolver

from tornado import stack_context
from tornado.util import GzipDecompressor
from tornado.concurrent import TracebackFuture
from tornado.simple_httpclient import _DEFAULT_CA_CERTS
import time

import base64
import collections
import copy
import functools

import re
import socket
import ssl
import sys

import logging

try:
    from io import BytesIO  # python 3
except ImportError:
    from cStringIO import StringIO as BytesIO  # python 2

try:
    import urlparse  # py2
except ImportError:
    import urllib.parse as urlparse  # py3


class SimpleKeepAliveHTTPClient(object):
    """Non-blocking HTTP client with no external dependencies.

    This class implements an HTTP 1.1 client on top of Tornado's IOStreams.
    It does not currently implement all applicable parts of the HTTP
    specification, but it does enough to work with major web service APIs.

    Some features found in the curl-based AsyncHTTPClient are not yet
    supported.  In particular, proxies are not supported, connections
    are not reused, and callers cannot select the network interface to be
    used.
    """
    def __init__(self, io_loop,
                   hostname_mapping=None, max_buffer_size=104857600,
                   resolver=None, defaults=None, idle_timeout=30.0):
        """Creates a AsyncHTTPClient.

        Only a single AsyncHTTPClient instance exists per IOLoop
        in order to provide limitations on the number of pending connections.
        force_instance=True may be used to suppress this behavior.

        max_clients is the number of concurrent requests that can be
        in progress.  Note that this arguments are only used when the
        client is first created, and will be ignored when an existing
        client is reused.

        hostname_mapping is a dictionary mapping hostnames to IP addresses.
        It can be used to make local DNS changes when modifying system-wide
        settings like /etc/hosts is not possible or desirable (e.g. in
        unittests).

        max_buffer_size is the number of bytes that can be read by IOStream. It
        defaults to 100mb.
        """
        self.io_loop = io_loop
        self.queue = collections.deque()
        self.active = {}
        self.max_buffer_size = max_buffer_size
        if resolver:
            self.resolver = resolver
            self.own_resolver = False
        else:
            self.resolver = Resolver(io_loop=self.io_loop)
            self.own_resolver = True
        if hostname_mapping is not None:
            self.resolver = OverrideResolver(resolver=self.resolver,
                                             mapping=hostname_mapping)

        self.defaults = dict(HTTPRequest._DEFAULTS)
        if defaults is not None:
            self.defaults.update(defaults)

        self.connection = KeepAliveHTTPConnection(self.io_loop, self, self.max_buffer_size, self.resolver)

        self.idle_timeout = idle_timeout
        self._idle_timeout_callback = None
        self.logger = logging.getLogger(self.__class__.__name__)


    def fetch(self, request, callback=None, **kwargs):
        """Executes a request, asynchronously returning an `HTTPResponse`.

        The request may be either a string URL or an `HTTPRequest` object.
        If it is a string, we construct an `HTTPRequest` using any additional
        kwargs: ``HTTPRequest(request, **kwargs)``

        This method returns a `.Future` whose result is an
        `HTTPResponse`.  The ``Future`` wil raise an `HTTPError` if
        the request returned a non-200 response code.

        If a ``callback`` is given, it will be invoked with the `HTTPResponse`.
        In the callback interface, `HTTPError` is not automatically raised.
        Instead, you must check the response's ``error`` attribute or
        call its `~HTTPResponse.rethrow` method.
        """
        if not isinstance(request, HTTPRequest):
            request = HTTPRequest(url=request, **kwargs)
        # We may modify this (to add Host, Accept-Encoding, etc),
        # so make sure we don't modify the caller's object.  This is also
        # where normal dicts get converted to HTTPHeaders objects.
        request.headers = httputil.HTTPHeaders(request.headers)
        request = _RequestProxy(request, self.defaults)
        future = TracebackFuture()
        if callback is not None:
            callback = stack_context.wrap(callback)

            def handle_future(future):
                exc = future.exception()
                if isinstance(exc, HTTPError) and exc.response is not None:
                    response = exc.response
                elif exc is not None:
                    response = HTTPResponse(
                        request, 599, error=exc,
                        request_time=time.time() - request.start_time)
                else:
                    response = future.result()
                self.io_loop.add_callback(callback, response)
            future.add_done_callback(handle_future)

        def handle_response(response):
            if response.error:
                future.set_exception(response.error)
            else:
                future.set_result(response)
        self.fetch_impl(request, handle_response)
        return future

    def close(self):
        super(SimpleKeepAliveHTTPClient, self).close()
        if self.own_resolver:
            self.resolver.close()

    def fetch_impl(self, request, callback):
        key = object()
        self.queue.append((key, request, callback))
        self._process_queue()

    def _process_queue(self):
        with stack_context.NullContext():
            if len (self.queue) and len(self.active) < 1:
                key, request, callback = self.queue.popleft()
                self.active[key] = (request, callback)
                release_callback = functools.partial(self._release_fetch, key)
                self._handle_request(request, release_callback, callback)


            if len(self.queue) == 0 and len(self.active) == 0:
                now = self.io_loop.time()
                self._idle_timeout_callback = self.io_loop.add_timeout(
                    now + self.idle_timeout,
                    stack_context.wrap(self._on_idle_timeout)
                )

            else:

                if self._idle_timeout_callback:
                    self.io_loop.remove_timeout(self._idle_timeout_callback)
                    self._idle_timeout_callback = None

    def _handle_request(self, request, release_callback, final_callback):
        if self.connection.final_callback and not self.connection.is_support_keepalive:
            self.logger.info('old connection does not support KA. creating new connection')
            self.connection = KeepAliveHTTPConnection(self.io_loop, self, self.max_buffer_size, self.resolver)

        self.connection.add_request(request, release_callback, final_callback)

    def _release_fetch(self, key):
        del self.active[key]
        self._process_queue()

    def _on_idle_timeout(self):
        msg = 'idle timeout'
        if hasattr(self, 'res_id'):
            msg += ' for {}'.format(self.res_id)
        self.logger.info(msg)
        self.connection.disconnect()

    def __len__(self):
        return len(self.queue) + len(self.active)


class KeepAliveHTTPConnection(object):
    _SUPPORTED_METHODS = set(["GET", "HEAD", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])

    def __init__(self, io_loop, client, max_buffer_size, resolver):
        self.start_time = io_loop.time()
        self.io_loop = io_loop
        self.client = client
        self.request = None
        self.release_callback = None
        self.final_callback = None
        self.max_buffer_size = max_buffer_size
        self.resolver = resolver
        self.code = None
        self.headers = None
        self.chunks = None
        self._decompressor = None
        # Timeout handle returned by IOLoop.add_timeout
        self._timeout = None
        self.is_support_keepalive = True
        self.stream = None
        self.connect_times = 0
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_request(self, request, release_callback, final_callback):
        self.request = request
        self.release_callback = release_callback
        self.final_callback = final_callback
        self._remove_timeout()
        self.resolve()

    def disconnect(self):
        self.logger.warn('about to disconnect')
        self.stream.close()

    def is_connected(self):
        if not self.stream:
            return False

        if self.stream.closed():
            return False

        return True

    def resolve(self):
        with stack_context.ExceptionStackContext(self._handle_exception):
            self.parsed = urlparse.urlsplit(_unicode(self.request.url))
            if self.parsed.scheme not in ("http", "https"):
                raise ValueError("Unsupported url scheme: %s" %
                                 self.request.url)
            # urlsplit results have hostname and port results, but they
            # didn't support ipv6 literals until python 2.7.
            netloc = self.parsed.netloc
            if "@" in netloc:
                userpass, _, netloc = netloc.rpartition("@")
            match = re.match(r'^(.+):(\d+)$', netloc)
            if match:
                host = match.group(1)
                port = int(match.group(2))
            else:
                host = netloc
                port = 443 if self.parsed.scheme == "https" else 80
            if re.match(r'^\[.*\]$', host):
                # raw ipv6 addresses in urls are enclosed in brackets
                host = host[1:-1]
            self.parsed_hostname = host  # save final host for _on_connect

            if self.request.allow_ipv6:
                af = socket.AF_UNSPEC
            else:
                # We only try the first IP we get from getaddrinfo,
                # so restrict to ipv4 by default.
                af = socket.AF_INET

            self.update_timeout()

        if self.is_connected():
            self.logger.info('is connecting ....')
            self._on_connect()
        else:
            self.resolver.resolve(host, port, af, callback=self._on_resolve)

    def update_timeout(self):
        # update the start_time here
        self.start_time = self.io_loop.time()
        timeout = min(self.request.connect_timeout, self.request.request_timeout)
        if timeout:
            self._timeout = self.io_loop.add_timeout(
                self.start_time + timeout,
                stack_context.wrap(self._on_timeout))

    def _on_resolve(self, addrinfo):
        if self.final_callback is None:
            # final_callback is cleared if we've hit our timeout
            return

        self.stream = self._create_stream(addrinfo)
        self.stream.set_close_callback(self._on_close)

        # ipv6 addresses are broken (in self.parsed.hostname) until
        # 2.7, here is correctly parsed value calculated in __init__
        sockaddr = addrinfo[0][1]
        self.stream.connect(sockaddr, self._on_connect,
                            server_hostname=self.parsed_hostname)
        self.connect_times += 1

    def _create_stream(self, addrinfo):
        af = addrinfo[0][0]
        if self.parsed.scheme == "https":
            ssl_options = {}
            if self.request.validate_cert:
                ssl_options["cert_reqs"] = ssl.CERT_REQUIRED
            if self.request.ca_certs is not None:
                ssl_options["ca_certs"] = self.request.ca_certs
            else:
                ssl_options["ca_certs"] = _DEFAULT_CA_CERTS
            if self.request.client_key is not None:
                ssl_options["keyfile"] = self.request.client_key
            if self.request.client_cert is not None:
                ssl_options["certfile"] = self.request.client_cert

            # SSL interoperability is tricky.  We want to disable
            # SSLv2 for security reasons; it wasn't disabled by default
            # until openssl 1.0.  The best way to do this is to use
            # the SSL_OP_NO_SSLv2, but that wasn't exposed to python
            # until 3.2.  Python 2.7 adds the ciphers argument, which
            # can also be used to disable SSLv2.  As a last resort
            # on python 2.6, we set ssl_version to TLSv1.  This is
            # more narrow than we'd like since it also breaks
            # compatibility with servers configured for SSLv3 only,
            # but nearly all servers support both SSLv3 and TLSv1:
            # http://blog.ivanristic.com/2011/09/ssl-survey-protocol-support.html
            if sys.version_info >= (2, 7):
                ssl_options["ciphers"] = "DEFAULT:!SSLv2"
            else:
                # This is really only necessary for pre-1.0 versions
                # of openssl, but python 2.6 doesn't expose version
                # information.
                ssl_options["ssl_version"] = ssl.PROTOCOL_TLSv1

            return SSLIOStream(socket.socket(af),
                               io_loop=self.io_loop,
                               ssl_options=ssl_options,
                               max_buffer_size=self.max_buffer_size)
        else:
            return IOStream(socket.socket(af),
                            io_loop=self.io_loop,
                            max_buffer_size=self.max_buffer_size)

    def _on_timeout(self):
        self._timeout = None
        if self.final_callback is not None:
            raise HTTPError(599, "Timeout")

    def _remove_timeout(self):
        if self._timeout is not None:
            self.io_loop.remove_timeout(self._timeout)
            self._timeout = None

    def _on_connect(self):
        self._remove_timeout()
        if self.final_callback is None:
            return
        if self.request.request_timeout:
            self._timeout = self.io_loop.add_timeout(
                self.start_time + self.request.request_timeout,
                stack_context.wrap(self._on_timeout))
        if (self.request.method not in self._SUPPORTED_METHODS and
                not self.request.allow_nonstandard_methods):
            raise KeyError("unknown method %s" % self.request.method)
        for key in ('network_interface',
                    'proxy_host', 'proxy_port',
                    'proxy_username', 'proxy_password'):
            if getattr(self.request, key, None):
                raise NotImplementedError('%s not supported' % key)
        # KA: here is the only changes
        #if "Connection" not in self.request.headers:
        self.request.headers["Connection"] = "keep-alive"
        if "Host" not in self.request.headers:
            if '@' in self.parsed.netloc:
                self.request.headers["Host"] = self.parsed.netloc.rpartition('@')[-1]
            else:
                self.request.headers["Host"] = self.parsed.netloc
        username, password = None, None
        if self.parsed.username is not None:
            username, password = self.parsed.username, self.parsed.password
        elif self.request.auth_username is not None:
            username = self.request.auth_username
            password = self.request.auth_password or ''
        if username is not None:
            if self.request.auth_mode not in (None, "basic"):
                raise ValueError("unsupported auth_mode %s",
                                 self.request.auth_mode)
            auth = utf8(username) + b":" + utf8(password)
            self.request.headers["Authorization"] = (b"Basic " +
                                                     base64.b64encode(auth))
        if self.request.user_agent:
            self.request.headers["User-Agent"] = self.request.user_agent
        if not self.request.allow_nonstandard_methods:
            if self.request.method in ("POST", "PATCH", "PUT"):
                if self.request.body is None:
                    raise AssertionError(
                        'Body must not be empty for "%s" request'
                        % self.request.method)
            else:
                if self.request.body is not None:
                    raise AssertionError(
                        'Body must be empty for "%s" request'
                        % self.request.method)
        if self.request.body is not None:
            self.request.headers["Content-Length"] = str(len(
                self.request.body))
        if (self.request.method == "POST" and
                "Content-Type" not in self.request.headers):
            self.request.headers["Content-Type"] = "application/x-www-form-urlencoded"
        if self.request.use_gzip:
            self.request.headers["Accept-Encoding"] = "gzip"
        req_path = ((self.parsed.path or '/') +
                   (('?' + self.parsed.query) if self.parsed.query else ''))
        request_lines = [utf8("%s %s HTTP/1.1" % (self.request.method,
                                                  req_path))]
        for k, v in self.request.headers.get_all():
            line = utf8(k) + b": " + utf8(v)
            if b'\n' in line:
                raise ValueError('Newline in header: ' + repr(line))
            request_lines.append(line)
        request_str = b"\r\n".join(request_lines) + b"\r\n\r\n"
        if self.request.body is not None:
            request_str += self.request.body
        self.stream.set_nodelay(True)
        self.stream.write(request_str)
        self.stream.read_until_regex(b"\r?\n\r?\n", self._on_headers)

    def _release(self):
        if self.release_callback is not None:
            release_callback = self.release_callback
            self.release_callback = None
            release_callback()

    def _run_callback(self, response):
        if self.final_callback is not None:
            final_callback = self.final_callback
            self.final_callback = None
            self.io_loop.add_callback(final_callback, response)

        self._release()

    def _handle_exception(self, typ, value, tb):
        if self.final_callback:
            self._remove_timeout()
            self._run_callback(HTTPResponse(self.request, 599, error=value,
                                            request_time=self.io_loop.time() - self.start_time,
                                            ))

            if hasattr(self, "stream"):
                if self.stream:
                    self.stream.close()
            return True
        else:
            # If our callback has already been called, we are probably
            # catching an exception that is not caused by us but rather
            # some child of our callback. Rather than drop it on the floor,
            # pass it along.
            return False

    def _on_close(self):
        if self.final_callback is not None:
            message = "Connection closed"
            if self.stream.error:
                message = str(self.stream.error)
            raise HTTPError(599, message)

    def _handle_1xx(self, code):
        self.stream.read_until_regex(b"\r?\n\r?\n", self._on_headers)

    def _on_headers(self, data):
        data = native_str(data.decode("latin1"))
        first_line, _, header_data = data.partition("\n")
        match = re.match("HTTP/1.[01] ([0-9]+) ([^\r]*)", first_line)
        assert match
        code = int(match.group(1))
        self.headers = httputil.HTTPHeaders.parse(header_data)
        if 100 <= code < 200:
            self._handle_1xx(code)
            return
        else:
            self.code = code
            self.reason = match.group(2)

        connection_param = self.headers.get('Connection', None)

        if connection_param and connection_param.lower() == 'keep-alive':
            self.logger.info('yes keep-alive')
        else:
            self.logger.info('no keep-alive')
            self.is_support_keepalive = False

        if "Content-Length" in self.headers:
            if "," in self.headers["Content-Length"]:
                # Proxies sometimes cause Content-Length headers to get
                # duplicated.  If all the values are identical then we can
                # use them but if they differ it's an error.
                pieces = re.split(r',\s*', self.headers["Content-Length"])
                if any(i != pieces[0] for i in pieces):
                    raise ValueError("Multiple unequal Content-Lengths: %r" %
                                     self.headers["Content-Length"])
                self.headers["Content-Length"] = pieces[0]
            content_length = int(self.headers["Content-Length"])
        else:
            content_length = None

        if self.request.header_callback is not None:
            # re-attach the newline we split on earlier
            self.request.header_callback(first_line + _)
            for k, v in self.headers.get_all():
                self.request.header_callback("%s: %s\r\n" % (k, v))
            self.request.header_callback('\r\n')

        if self.request.method == "HEAD" or self.code == 304:
            # HEAD requests and 304 responses never have content, even
            # though they may have content-length headers
            self._on_body(b"")
            return
        if 100 <= self.code < 200 or self.code == 204:
            # These response codes never have bodies
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec4.html#sec4.3
            if ("Transfer-Encoding" in self.headers or
                    content_length not in (None, 0)):
                raise ValueError("Response with code %d should not have body" %
                                 self.code)
            self._on_body(b"")
            return

        if (self.request.use_gzip and
                self.headers.get("Content-Encoding") == "gzip"):
            self._decompressor = GzipDecompressor()
        if self.headers.get("Transfer-Encoding") == "chunked":
            self.chunks = []
            self.stream.read_until(b"\r\n", self._on_chunk_length)
        elif content_length is not None:
            self.stream.read_bytes(content_length, self._on_body)
        else:
            self.stream.read_until_close(self._on_body)

    def _on_body(self, data):
        self._remove_timeout()
        original_request = getattr(self.request, "original_request",
                                   self.request)
        if (self.request.follow_redirects and
            self.request.max_redirects > 0 and
                self.code in (301, 302, 303, 307)):
            assert isinstance(self.request, _RequestProxy)
            new_request = copy.copy(self.request.request)
            new_request.url = urlparse.urljoin(self.request.url,
                                               self.headers["Location"])
            new_request.max_redirects = self.request.max_redirects - 1
            del new_request.headers["Host"]
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.3.4
            # Client SHOULD make a GET request after a 303.
            # According to the spec, 302 should be followed by the same
            # method as the original request, but in practice browsers
            # treat 302 the same as 303, and many servers use 302 for
            # compatibility with pre-HTTP/1.1 user agents which don't
            # understand the 303 status.
            if self.code in (302, 303):
                new_request.method = "GET"
                new_request.body = None
                for h in ["Content-Length", "Content-Type",
                          "Content-Encoding", "Transfer-Encoding"]:
                    try:
                        del self.request.headers[h]
                    except KeyError:
                        pass
            new_request.original_request = original_request
            final_callback = self.final_callback
            self.final_callback = None
            self._release()
            self.client.fetch(new_request, final_callback)
            self._on_end_request()
            return
        if self._decompressor:
            data = (self._decompressor.decompress(data) +
                    self._decompressor.flush())
        if self.request.streaming_callback:
            if self.chunks is None:
                # if chunks is not None, we already called streaming_callback
                # in _on_chunk_data
                self.request.streaming_callback(data)
            buffer = BytesIO()
        else:
            buffer = BytesIO(data)  # TODO: don't require one big string?
        response = HTTPResponse(original_request,
                                self.code, reason=self.reason,
                                headers=self.headers,
                                request_time=self.io_loop.time() - self.start_time,
                                buffer=buffer,
                                effective_url=self.request.url)
        self._run_callback(response)
        self._on_end_request()

    def _on_end_request(self):
        if not self.is_support_keepalive:
            self.stream.close()

    def _on_chunk_length(self, data):
        # TODO: "chunk extensions" http://tools.ietf.org/html/rfc2616#section-3.6.1
        length = int(data.strip(), 16)
        if length == 0:
            if self._decompressor is not None:
                tail = self._decompressor.flush()
                if tail:
                    # I believe the tail will always be empty (i.e.
                    # decompress will return all it can).  The purpose
                    # of the flush call is to detect errors such
                    # as truncated input.  But in case it ever returns
                    # anything, treat it as an extra chunk
                    if self.request.streaming_callback is not None:
                        self.request.streaming_callback(tail)
                    else:
                        self.chunks.append(tail)
                # all the data has been decompressed, so we don't need to
                # decompress again in _on_body
                self._decompressor = None
            self._on_body(b''.join(self.chunks))
        else:
            self.stream.read_bytes(length + 2,  # chunk ends with \r\n
                                   self._on_chunk_data)

    def _on_chunk_data(self, data):
        assert data[-2:] == b"\r\n"
        chunk = data[:-2]
        if self._decompressor:
            chunk = self._decompressor.decompress(chunk)
        if self.request.streaming_callback is not None:
            self.request.streaming_callback(chunk)
        else:
            self.chunks.append(chunk)
        self.stream.read_until(b"\r\n", self._on_chunk_length)

