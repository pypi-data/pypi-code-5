# -*- coding: utf-8 -*-
"""
placeholder
"""
import functools
import urlparse
import base64
import logging
import stat


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.0.1'

import os
import sys
import threading
import hashlib
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

from time import time, gmtime
try:
    from email.utils import parsedate_tz
except ImportError: # pragma: no cover
    from email.Utils import parsedate_tz
from datetime import datetime, timedelta

PY2 = sys.version_info[0] == 2
if PY2:
    integer_types = (int, long)
    b = lambda v: v
else:
    integer_types = (int, )
    b = lambda v: v.encode('utf-8')


conf_path = os.path.expanduser('~/.upsrc')
options = ConfigParser()
logging.basicConfig(level=logging.INFO,
                    format='[%(levelname)1.1s %(asctime)s '
                           '%(module)s:%(lineno)d] %(message)s')


def authenticated(method):
    """Upyun authenticate"""

    @functools.wraps(method)
    def wrapper(self):
        self.prepare()
        if self.bucket is None:
            self.write_error(400, 'Bad Request')
            return

        auth = self.headers.getheader('Authorization', '')

        if not options.has_section(self.bucket) or not auth:
            self.write_error(401, 'Unauthorized')
            return
        username = options.get(self.bucket, 'username')
        password = options.get(self.bucket, 'password')

        auth_type, auth_content = auth.split()
        error_msg = ''
        # Basic auth
        if auth_type == 'Basic':
            if auth_content != base64.b64encode('%s:%s' % (username, password)):
                error_msg = 'Sign error'
        # UpYun auth
        elif auth_type == 'UpYun':
            date_str = self.headers.getheader('Date', '')
            if not date_str:
                error_msg = 'Need Date Header'
            else:
                user, sign = auth_content.split(':')
                com_sign = hashlib.md5('&'.join(
                    [self.command,
                     self.uri,
                     date_str,
                     self.headers.getheader('Content-Length', '0'),
                     hashlib.md5(password).hexdigest()])).hexdigest()
                logging.info('user %s sign %s', username, com_sign)
                if user != username or sign != com_sign:
                    error_msg = 'Sign error'
                else:
                    dt = parse_date(date_str)
                    if abs(int(dt.strftime('%s')) -
                            int(datetime.utcnow().strftime('%s'))) > 30*60:
                        error_msg = 'Date offset error'
        else:
            error_msg = 'Unauthorized'
        if error_msg:
            logging.info(error_msg)
            self.write_error(401, error_msg)
            return

        return method(self)
    return wrapper


class Handler(BaseHTTPRequestHandler):
    def __init__(self, request, client_address, server):
        self.uri = None
        self.path = None
        self.bucket = None
        self.bucket_path = None
        self.file_path = None
        self.query_str = None

        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def prepare(self):
        self.uri = self.path
        url_parsed = urlparse.urlparse(self.uri)
        self.path = url_parsed.path
        self.query_str = url_parsed.query
        tmp = self.path.split('/')
        if len(tmp) >= 2:
            self.bucket = tmp[1]
            self.bucket_path = options.get(self.bucket, 'path')
            self.file_path = self.path[len(self.bucket)+2:]

    def get_header(self, name, default=None):
        return self.headers.getheader(name, default=default)

    def get_headers(self, name):
        return self.headers.getheaders(name)

    def write_error(self, code, msg):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(msg)
        self.wfile.write('\n')

    @authenticated
    def do_HEAD(self):
        """file info  """
        dest_path = os.path.join(self.bucket_path, self.file_path)
        if not os.path.exists(dest_path):
            logging.error('file does not exist')
            self.write_error(404, 'Not Found')
            return
        file_info = os.stat(dest_path)
        file_type = 'folder' if stat.S_ISDIR(file_info.st_mode) else 'file'
        self.send_response(200)
        self.send_header('x-upyun-file-type', file_type)
        self.send_header('x-upyun-file-size', file_info.st_size)
        self.send_header('x-upyun-file-date', int(file_info.st_mtime))
        self.end_headers()
        self.wfile.write('\n')

    @authenticated
    def do_PUT(self):
        """ Upload file """
        dest_path = os.path.join(self.bucket_path, self.file_path)
        dir_name = os.path.dirname(dest_path)
        if not os.path.exists(os.path.dirname(dest_path)):
            if self.headers.getheader('Mkdir', 'false') != 'true':
                logging.error('directory does not exist')
                self.write_error(404, 'Not Found')
                return
            else:
                try:
                    os.makedirs(dir_name)
                except OSError as ex:
                    logging.error('mkdir failed, %s', ex.message)
                    self.write_error(503, 'System Error')
                    return

        with open(dest_path, 'wb') as f:
            f.write(self.rfile.read(int(self.get_header('Content-Length'))))

        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n')
        logging.info('save file to: %s', dest_path)

    def do_POST(self):
        """Make dirs """
        dest_path = os.path.join(self.bucket_path, self.file_path)
        if self.get_header('Folder', '') != 'true':
            self.write_error(503, 'System Error')
            return
        if not os.path.exists(dest_path):
            if self.get_header('Mkdir', 'false') == 'true':
                try:
                    os.makedirs(dest_path)
                except OSError as ex:
                    logging.error('mkdir failed, %s', ex.message)
                    self.write_error(503, 'System Error')
                    return
            else:
                try:
                    os.mkdir(dest_path)
                except OSError as ex:
                    logging.error('mkdir failed, %s', ex.message)
                    self.write_error(503, 'System Error')
                    return
        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n')
        logging.info('mkdir : %s', dest_path)

    @authenticated
    def do_DELETE(self):
        """Delete file or directory. """
        dest_path = os.path.join(self.bucket_path, self.file_path)
        if not os.path.exists(dest_path):
            logging.error('file does not exist')
            self.write_error(404, 'Not Found')
            return
        if os.path.isdir(dest_path):
            try:
                os.rmdir(dest_path)
            except OSError as ex:
                logging.error('rmdir failed, %s', ex.message)
                self.write_error(503, 'System Error')
        else:
            try:
                os.remove(dest_path)
            except OSError as ex:
                logging.error('rm failed, %s', ex.message)
                self.write_error(503, 'System Error')
        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n')
        logging.info('rm file/directory : %s', dest_path)

    @authenticated
    def do_GET(self):
        """ Directory info or download file or usage  """
        if self.query_str == 'usage':
            self.do_usage()
            return
        dest_path = os.path.join(self.bucket_path, self.file_path)
        if not os.path.exists(dest_path):
            logging.error('file does not exist')
            self.write_error(404, 'Not Found')
            return

        if os.path.isdir(dest_path):
            self.do_dir_info()
            return
        else:
            self.do_download()
            return

    def do_download(self):
        pass

    def do_dir_info(self):
        dest_path = os.path.join(self.bucket_path, self.file_path)
        result = []
        for f in os.listdir(dest_path):
            file_info = os.stat(os.path.join(dest_path, f))
            file_type = 'F' if stat.S_ISDIR(file_info.st_mode) else 'N'
            result.append('\t'.join([
                f,
                file_type,
                str(file_info.st_size),
                str(int(file_info.st_mtime))
            ]))

        self.send_response(200)
        self.end_headers()
        self.wfile.write('\n'.join(result))

    def do_usage(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write('0')


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


def parse_date(value):
    """Parse one of the following date formats into a datetime object:

    .. sourcecode:: text

        Sun, 06 Nov 1994 08:49:37 GMT  ; RFC 822, updated by RFC 1123
        Sunday, 06-Nov-94 08:49:37 GMT ; RFC 850, obsoleted by RFC 1036
        Sun Nov  6 08:49:37 1994       ; ANSI C's asctime() format

    If parsing fails the return value is `None`.

    :param value: a string with a supported date format.
    :return: a :class:`datetime.datetime` object.
    """
    if value:
        t = parsedate_tz(value.strip())
        if t is not None:
            try:
                year = t[0]
                # unfortunately that function does not tell us if two digit
                # years were part of the string, or if they were prefixed
                # with two zeroes.  So what we do is to assume that 69-99
                # refer to 1900, and everything below to 2000
                if 0 <= year <= 68:
                    year += 2000
                elif 69 <= year <= 99:
                    year += 1900
                return datetime(*((year,)+t[1:7]))-timedelta(seconds=t[-1] or 0)
            except (ValueError, OverflowError):
                return None


def _dump_date(d, delim=' '):
    """Used for `http_date` and `cookie_date`."""
    if d is None:
        d = gmtime()
    elif isinstance(d, datetime):
        d = d.utctimetuple()
    elif isinstance(d, (integer_types, float)):
        d = gmtime(d)
    return '%s, %02d%s%s%s%s %02d:%02d:%02d GMT' % (
        ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')[d.tm_wday],
        d.tm_mday, delim,
        ('Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
         'Oct', 'Nov', 'Dec')[d.tm_mon - 1],
        delim, str(d.tm_year), d.tm_hour, d.tm_min, d.tm_sec
    )


def load_options():
    if not os.path.exists(conf_path):
        print("Sorry but I can't find the config file. Please fill the "
              "following template and save it to %s" % conf_path)
        print("""
; Sample ups config file

; The below sample bucket section shows all possible config values,
; create one or more 'real' bucket sections to be able to control them under
; upc.

[server]
port=8080
host=127.0.0.1
; use 0.0.0.0 to allow outer access

;[bucket_name]
;username=foo
;password=bar
;path=/some/path
;

;[more_buckets] ; your bucket name
;..""")
        sys.exit(2)
    with open(conf_path, 'r') as f:
        options.readfp(f)

if __name__ == '__main__':
    load_options()

    host = options.get('server', 'host', '127.0.0.1')
    port = options.get('server', 'port', '7080')
    http_server = ThreadedHTTPServer((host, int(port)), Handler)

    logging.info('Starting server on port %s, use <Ctrl-C> to stop')
    http_server.serve_forever()
