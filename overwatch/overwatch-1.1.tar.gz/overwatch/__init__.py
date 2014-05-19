from threading import Thread
from Queue import Queue
import logging
import socket
import bsoncoder as bson
import os
import datetime
import traceback
from time import time, sleep


def init(id, api_key=None):
    _instance = Overwatch(id, api_key)
    _instance.start()

class Overwatch(Thread):
    class Handler(logging.StreamHandler):
        def __init__(self, callback):
            self.callback = callback
            logging.StreamHandler.__init__(self)

        def emit(self, record):
            self.callback(record)

    def __init__(self, id, api_key):
        Thread.__init__(self)
        self.daemon = True
        self.id = id
        self.api_key = api_key
        self.socket_path = '/tmp/overwatch-%s.sock' % self.id

        self._init_socket()

        self.queue = Queue()
        self.root_logger = logging.getLogger()
        self.root_logger.addHandler(Overwatch.Handler(self._process))

    def _init_socket(self):
        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket.connect('/tmp/overwatch.sock')
            self.socket.send(bson.dumps({
                'action': 'hello',
                'project_id': self.id,
                'pid': os.getpid(),
            }))
        except Exception, e:
            pass

    def _process(self, record):
        self.queue.put(record)

    def run(self):
        while True:
            try:
                record = self.queue.get(True, 1)
            except:
                continue
            if record.exc_info:
                record.msg = record.msg + '\n' + ''.join(traceback.format_exception(
                    record.exc_info[0],
                    record.exc_info[1],
                    record.exc_info[2],
                    100
                ))
            while True:
                try:
                    self.socket.send(bson.dumps({
                        'action': 'log_event',
                        'record': {
                            'source': 'python',
                            'levelname': record.levelname,
                            'levelno': record.levelno,
                            'api_key': self.api_key,
                            'module': record.module,
                            'filename': record.filename,
                            'func_name': record.funcName,
                            'lineno': str(record.lineno),
                            'msg': record.msg % record.args,
                            'time': '%f' % time(),
                        },
                    }))
                    break
                except Exception, e:
                    sleep(1)
                    self.connect()
