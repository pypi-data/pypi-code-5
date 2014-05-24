from BaseHTTPServer import HTTPServer
import os
import argparse

from .interface import PythonHTTP


def console():
    parser = argparse.ArgumentParser(description='Endpoints -- Simple server')
    parser.add_argument(
        '--dir', '-d',
        dest='dir',
        default=os.curdir,
        help='directory to server from, defaults to current working directory'
    )
    parser.add_argument(
        '--port', '-p',
        dest='port',
        default=8000,
        type=int,
        help='the port for the webserver'
    )
    parser.add_argument(
        '--prefix',
        dest='prefix',
        default='',
        help='the controller prefix'
    )

    args = parser.parse_args()

    if args.prefix:
        os.environ['ENDPOINTS_PREFIX'] = args.prefix

    server_address = ('', args.port)
    httpd = HTTPServer(server_address, PythonHTTP)
    httpd.serve_forever()
    #httpd.handle_request()

