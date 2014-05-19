#!/usr/bin/env python

"""
FilteredWebSocket: Morgan (Reece) Phillips @linuxpoetry linux-poetry.com

Create WebSocket servers by composing filter chains.

"""

from __future__ import absolute_import

from twisted.internet.protocol import Factory
from twisted.internet import reactor, ssl
from twisted.internet.task import LoopingCall
from .server_protocol.server import Protocol
import argparse
import json
import sys

from .storage_objects.default_storage_object import DefaultStorageObject
from .filters.base import (
    WebSocketDataFilter,
    WebSocketMessageFilter,
    WebSocketDisconnectFilter,
    WebSocketConsumerFilter,
)


class FilteredWebSocket(Protocol):

    def __init__(self, *args, **kwargs):

        # The storage object should inherit from
        # storage_objects.default_storage_object.BaseStorageObject
        self.storage_object = kwargs.pop("storage_object")

        # The token object may be leveraged for authentication via OAuth,
        # session keys, or other such methods.  See the
        # broadcast_messages_by_token module for an example.
        self.token = kwargs.pop("token")

        # A queue to be used in any producer/consumer activities
        # TODO: Implement this as an actual Queue object
        self.queue = []

        super(FilteredWebSocket, self).__init__(*args, **kwargs)

    def dataReceived(self, data):
        WebSocketDataFilter.run(self, data)
        super(FilteredWebSocket, self).dataReceived(data)

    def onDisconnect(self):
        WebSocketDisconnectFilter.run(self)

    def onMessage(self, msg):
        WebSocketMessageFilter.run(self, msg)


class FilteredWebSocketFactory(Factory):

    def __init__(self, **kwargs):
        self.storage_object = kwargs.get("storage_object", DefaultStorageObject())
        self.token = kwargs.get("token")
        self.users = {}
        self.queue = []

    def buildProtocol(self, _address):
        return FilteredWebSocket(
            self.users,
            storage_object=self.storage_object,
            token=self.token
        )

    def consumer(self):
        """
        Called in a reactor loop to enable the producer/consumer pattern.
        """
        if len(self.queue) > 0:
            data = self.queue.pop()
            WebSocketConsumerFilter.run(self, data)


def default_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-p",
        "--port",
        help="The listening port.",
        type=int,
        default=9000
    )
    parser.add_argument(
        "-c",
        "--config",
        help="A JSON config file."
    )
    parser.add_argument(
        "-f",
        "--filters",
        help="Filters to import at runtime.",
        nargs="*"
    )
    parser.add_argument(
        "-key",
        help="A key file (ssl)."
    )
    parser.add_argument(
        "-cert",
        help="A certificate file (ssl)."
    )
    parser.add_argument(
        "-token",
        help="Set a default token value."
    )
    return parser


def build_reactor(options, **kwargs):
    web_socket_instance = FilteredWebSocketFactory(**kwargs)
    pubsub_listener = kwargs.pop("pubsub_listener", None)

    if options.key and options.cert:
        with open(options.key) as keyFile:
            with open(options.cert) as certFile:
                cert = ssl.PrivateCertificate.loadPEM(keyFile.read() + certFile.read())
                reactor.listenSSL(options.port, web_socket_instance, cert.options())
    else:
        reactor.listenTCP(
            options.port,
            web_socket_instance
        )
    if pubsub_listener is not None:
        reactor.callInThread(
            pubsub_listener.listener,
            web_socket_instance
        )
        reactor.addSystemEventTrigger(
            "before",
            "shutdown",
            pubsub_listener.kill
        )

    # Start the consumer loop
    consumer_loop = LoopingCall(
        web_socket_instance.consumer
    )
    consumer_loop.start(0.01, now=False)
    return web_socket_instance


def config_deserializer(filename):
    """
    Transforms a JSON config file into a list or arguments which may be passed
    to arg_parser.parse_args.

    For instance:

        {
            port: 22
        }

    Would would be transformed to:

        ['--port', '22']
    """
    with open(filename, "r") as config_file:
        config_lines = "".join([l for l in config_file if l[0] != "#"])
        config_data = json.loads(config_lines)
        processed_config_data = []
        for key, value in config_data.items():
            if key == "flags":
                for flag in value:
                    processed_config_data.append("--%s" % flag)
            else:
                processed_config_data.append("--%s" % key)
                if isinstance(value, (list, set)):
                    processed_config_data += value
                else:
                    processed_config_data.append(value)
    return processed_config_data


if __name__ == '__main__':
    import importlib
    from .storage_objects.redis_storage_object import RedisStorageObject, redis_parser
    from .pubsub_listeners.redis_pubsub_listener import RedisPubSubListener

    parser = default_parser()
    parser = redis_parser(parser)
    options = parser.parse_args(sys.argv[1:])

    # A passed in config file will overwrite all other args
    if options.config is not None:
        options = parser.parse_args(config_deserializer(options.config))

    # If no filters are specified this will be imported.
    # the broadcast_by_message filter just creates a simple broadcast server
    FILTERS = [
        "filtered_websocket.filters.broadcast_messages_by_token",
        "filtered_websocket.filters.stdout_messages",
    ]

    # Extra args to set up custom storage (redis in this case)
    extra = {}
    if options.redis is True:
        FILTERS += ["filtered_websocket.filters.broadcast_pubsub"]
        redis_storage_object = RedisStorageObject(
            host=options.redis_host,
            port=options.redis_port,
            key=options.redis_key
        )
        redis_pubsub = RedisPubSubListener(
            redis_storage_object.redis,
            options.redis_channels
        )
        # Build our server reactor.
        web_socket_instance = build_reactor(
            options,
            storage_object=redis_storage_object,
            pubsub_listener=redis_pubsub
        )
    else:
        build_reactor(options)

    if options.filters is not None:
        FILTERS = options.filters

    # Importing the filters will inject them into event handlers at runtime
    for _filter in FILTERS:
        importlib.import_module(_filter)

    reactor.run()
