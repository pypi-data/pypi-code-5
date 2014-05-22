import gevent
from gevent import monkey
monkey.patch_all()

from flask import Flask, render_template, request

from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import BroadcastMixin

import logging

import zmq.green as zmq
from pkg_resources import iter_entry_points


app = Flask(__name__)


class Slotty:
    """ Flask app collecting all ioloop
    extensions points """

    def __init__(self, app):
        self.app = app
        self.app.config.from_object('slotty.config')
        self.app.config.from_envvar('SLOTTY_CONFIG_FILE', silent=True)
        self.configure_logging()
        self.load_sensors()
        self.load_plugins()

    def load_plugins(self):
        for entry_point in iter_entry_points(
                group='slotty.plugin', name=None):
            self.plugins[entry_point.name] =  {
                'plugin': entry_point.load(),
                'entry_point': entry_point}

    def load_sensors(self):
        """ Loads all entry points for the sensors.

        The entry point must return a function. The function is
        passed the zmq.green address to bind against for pushing
        the notifications. The notifications are forwarded to
        all connected clients through a socket.io connection.
        The sensor has to use gevent.sleep() to yield to other
        cooperative green threads. The
        """
        for entry_point in iter_entry_points(
                group='slotty.publisher', name=None):
            sensor = entry_point.load()
            self.app.logger.info("Data publisher '{}' loaded".format(entry_point.name))
            gevent.spawn(sensor, self.app.config["API_ADDRESS"])

    def configure_logging(self):
       log_format = self.app.config["LOG_FORMAT"]
       date_format = self.app.config["DATE_FORMAT"]
       formatter = logging.Formatter(log_format, date_format)
       console = logging.StreamHandler()
       console.setFormatter(formatter)
       logger = logging.getLogger()
       logger.addHandler(console)
       logger.setLevel(logging.DEBUG)
       for handler in self.app.logger.handlers:
           handler.setFormatter(formatter)


class SlottyAPI(BaseNamespace, BroadcastMixin):
    """ Endpoint for the socket.io connection.

    Broadcasts all incoming zmq.green data to the connected
    clients
    """
    def process_packet(self, packet):
        """ route the data to our zmq sockets

        Currentyl there is no ACL lookup for incoming
        messages
        """
        from pprint import pformat
        app.logger.info("Received Packet: %s", pformat(packet))
        packet_type = packet['type']

        if packet_type == 'connect':
            context = zmq.Context()
            sock = context.socket(zmq.SUB)
            sock.setsockopt(zmq.SUBSCRIBE, "")
            sock.connect(app.config["API_ADDRESS"])
            gevent.spawn(self.outbound, context, sock)

    def outbound(self, context, sock):
        while True:
            data = sock.recv_json()
            #app.logger.debug(data)
            self.broadcast_event(data["event"], data["args"])
            gevent.sleep(0.01)

    def inboud(self, context, sock):
        while True:
            data = sock.recv_json()
            app.logger.debug(data)
            self.broadcast_event(data["event"], data["args"])
            gevent.sleep(0.01)


slotty = Slotty(app)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/socket.io/<path:rest>')
def push_stream(rest):
    try:
        socketio_manage(request.environ,
                        {'/sensors': SlottyAPI},
                        request)
    except:
        app.logger.error("Exception while handling socketio connection",
                         exc_info=True)
