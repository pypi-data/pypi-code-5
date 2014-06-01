# -*- coding: utf-8 -*-
"""
placeholder
"""
import io
import cgi
import functools
import json
import base64
import logging
import stat
import mimetypes


__author__ = 'Kang Li<i@likang.me>'
__version__ = '0.0.3'

import os
import sys
import hashlib
from time import gmtime
from PIL import Image
from datetime import datetime, timedelta

PY2 = sys.version_info[0] == 2

from email.utils import parsedate_tz
if PY2:
    import urlparse
    from ConfigParser import ConfigParser
    import urllib2
    from SocketServer import ThreadingMixIn
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urllib import unquote, urlencode

    integer_types = (int, long)
    b = lambda v: v
else:
    from urllib import parse as urlparse
    from urllib import request as urllib2
    from urllib.parse import unquote, urlencode
    from configparser import ConfigParser
    from socketserver import ThreadingMixIn
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from http.client import HTTPMessage
    HTTPMessage.getheader = HTTPMessage.get


    integer_types = (int, )
    b = lambda v: v.encode('utf-8')


conf_path = os.path.expanduser('~/.upsrc')
options = ConfigParser()


def authenticated(method):
    """Upyun authenticate"""

    @functools.wraps(method)
    def wrapper(self):
        self.prepare()
        if self.bucket is None:
            self.write_error(400, 'Bad Request')
            return

        if self.bucket_path is None or not os.path.isdir(self.bucket_path):
            self.write_error(503, 'System Error')
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
                com_sign = hashlib.md5(b('&'.join(
                    [self.command,
                     self.uri,
                     date_str,
                     self.headers.getheader('Content-Length', '0'),
                     hashlib.md5(b(password)).hexdigest()]))).hexdigest()
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
            if options.has_section(self.bucket):
                self.bucket_path = options.get(self.bucket, 'path')
                self.file_path = self.path[len(self.bucket)+2:]
                self.file_path = unquote(self.file_path)

    def get_header(self, name, default=None):
        return self.headers.getheader(name, default)

    def get_headers(self, name):
        return self.headers.getheaders(name)

    def write_error(self, code, msg):
        self.send_response(code)
        self.end_headers()
        self.wfile.write(b(msg))

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

        file_content = self.rfile.read(int(self.get_header('Content-Length')))

        i = io.BytesIO()
        i.write(file_content)
        i.seek(0)
        is_picture = True
        try:
            im = Image.open(i)
        except IOError:
            is_picture = False

        # if it is picture
        if is_picture:
            cus_type = self.get_header('x-gmkerl-type', '')
            cus_value = self.get_header('x-gmkerl-value', '')
            cus_quanlity = int(self.get_header('x-gmkerl-quality', '95'))
            cus_unsharp = int(self.get_header('x-gmkerl-unsharp', 'true')
                              == 'true')
            ext = os.path.splitext(dest_path)[-1].lstrip('.')
            width, height = im.size
            if cus_type == 'fix_width':
                cus_value = float(cus_value)
                width_percent = cus_value/width
                cus_height = int(height*width_percent)
                im.thumbnail((cus_value, cus_height), cus_unsharp)
            elif cus_type == 'fix_height':
                cus_value = float(cus_value)
                height_percent = (cus_value/float(height))
                cus_width = int(width*height_percent)
                im.thumbnail((cus_width, cus_value), cus_unsharp)
            elif cus_type == 'fix_width_or_height':
                cus_width, cus_height = map(int, cus_value.split('x'))
                im.thumbnail((cus_width, cus_height), cus_unsharp)
            elif cus_type == 'fix_both':
                cus_width, cus_height = map(int, cus_value.split('x'))
                im.resize((cus_width, cus_height), cus_unsharp)
            elif cus_type == 'fix_max':
                cus_value = float(cus_value)
                percent = cus_value/max(width, height)
                im.thumbnail((width*percent, height*percent), cus_unsharp)
            elif cus_type == 'fix_min':
                cus_value = float(cus_value)
                percent = cus_value/min(width, height)
                im.thumbnail((width*percent, height*percent), cus_unsharp)
            elif cus_type == 'fix_scale':
                cus_value = int(cus_value)
                im.resize((width*cus_value/100.0, height*cus_value/100.0),
                          cus_unsharp)
            i.seek(0)
            im.save(i, ext if ext.lower() != 'jpg' else 'jpeg',
                    quantity=cus_quanlity)
            file_content = i.getvalue()
            i.close()

        with open(dest_path, 'wb') as f:
            f.write(file_content)

        self.send_response(200)
        self.end_headers()
        logging.info('save file to: %s', dest_path)

    def do_POST(self):
        if self.get_header('Content-Type', '').startswith(
                'multipart/form-data'):
            self.do_form()
        else:
            self.do_mkdir()

    @authenticated
    def do_mkdir(self):
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
        logging.info('rm file/directory : %s', dest_path)

    def do_GET(self):
        """Show directory info or download file or show usage  """
        path = self.path
        self.prepare()

        if self.query_str == 'usage':
            self.path = path
            self.do_usage()
            return

        dest_path = os.path.join(self.bucket_path, self.file_path)
        if not os.path.exists(dest_path):
            logging.error('file does not exist')
            self.write_error(404, 'Not Found')
            return

        if os.path.isdir(dest_path):
            self.path = path
            self.do_dir_info()
        else:
            self.do_download()

    def do_download(self):
        """Download file """
        dest_path = os.path.join(self.bucket_path, self.file_path)
        self.send_response(200)
        content_type = mimetypes.guess_type(dest_path)
        if content_type[0] is not None:
            self.send_header('Content-Type', content_type[0])
        self.end_headers()
        with open(dest_path, 'rb') as f:
            self.wfile.write(f.read())

    @authenticated
    def do_dir_info(self):
        """Show directory info"""
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
        self.wfile.write(b('\n'.join(result)))

    @authenticated
    def do_usage(self):
        """Show usage"""
        size = 0
        for dir_path, dir_names, files in os.walk(self.bucket_path):
            for f in files:
                size += os.stat(os.path.join(dir_path, f)).st_size

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b(str(size)))

    def do_form(self):
        """Form API"""
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST',
                     'CONTENT_TYPE': self.get_header('Content-Type'),
                     })
        if 'policy' not in form:
            self.write_form_resp(400, 'Not accept, Miss policy.', {},
                                 '', None)
            return
        if 'signature' not in form:
            self.write_form_resp(400, 'Not accept, Miss signature.', {},
                                 '', None)
            return

        if 'file' not in form:
            self.write_form_resp(400, 'Not accept, No file data.', {},
                                 '', None)
            return

        policy_str = form['policy'].value
        signature = form['signature'].value
        file_content = form['file'].file.read()
        file_name = form['file'].filename
        policy = json.loads(base64.b64decode(policy_str))

        if 'bucket' not in policy:
            self.write_form_resp(400, 'Not accept, Bucket is null.', policy,
                                 '', None)
            return
        self.bucket = policy['bucket']
        if not options.has_section(self.bucket):
            self.write_form_resp(404, 'Bucket does not exist.', policy,
                                 '', None)
            return

        self.bucket_path = options.get(self.bucket, 'path', None)

        form_secret = options.get(self.bucket, 'form_secret', '')
        if signature != hashlib.md5(b(policy_str+'&' + form_secret)):
            self.write_form_resp(403, 'Not accept, Signature error.', policy,
                                 '', form_secret)
            return
        if 'save_key' not in policy:
            self.write_form_resp(400, 'Not accept, Save-key is null.', policy,
                                 '', form_secret)
            return

        save_key = policy['save_key']
        now = datetime.now()
        year, mon, day, hour, minu, sec = \
            now.strftime('%Y %m %d %H %M %S').split()
        replaces = {
            'year': year,
            'mon': mon,
            'day': day,
            'hour': hour,
            'min': minu,
            'sec': sec,
            'filemd5': hashlib.md5(file_content).hexdigest(),
            'random': 16,
            'random32': 32,
            'filename': file_name,
            'suffix': os.path.basename(file_name),
            '.suffix': '.' + os.path.basename(file_name)
        }
        for k, v in replaces.items():
            save_key = save_key.replace('{%s}' % k, v)

        dest_path = os.path.join(self.bucket_path, save_key)
        if not os.path.exists(os.path.dirname(dest_path)):
            try:
                os.makedirs(os.path.dirname(dest_path))
            except OSError as ex:
                self.write_form_resp(503, 'System Error, please try again.',
                                     policy, save_key, form_secret)
                return
            with open(dest_path, 'rb') as f:
                f.write(file_content)
        self.write_form_resp(200, 'OK', policy, save_key, form_secret)

    def write_form_resp(self, code, message, policy, save_key, form_secret):
        response = {'code': code,
                    'message': message,
                    'time': int(datetime.now().strftime('%s')),
                    'url': save_key,
                    }
        if form_secret:
            response['sign'] = hashlib.md5(b('&'.join([
                code, message, save_key,
                response['time'], form_secret]))).hexdigest()
        else:
            response['non-sign'] = hashlib.md5(b('&'.join([
                code, message, save_key, response['time']]))).hexdigest()

        if 'return-url' in policy:
            return_url = policy['return-url'] + '?' + urlencode(response)
            self.send_response(302)
            self.send_header('Location', return_url)
            self.end_headers()
            return

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b(json.dumps(response, ensure_ascii=False)))

        if 'notify-url' in policy:
            notify_url = policy['notify-url'] + '?' + urlencode(response)
            urllib2.urlopen(notify_url, {})


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


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)1.1s %(asctime)s '
                               '%(module)s:%(lineno)d] %(message)s')
    load_options()

    host = options.get('server', 'host')
    port = options.get('server', 'port')
    http_server = ThreadedHTTPServer((host, int(port)), Handler)

    logging.info('Starting server on port %s, use <Ctrl-C> to stop' % port)
    http_server.serve_forever()

if __name__ == '__main__':
    main()
