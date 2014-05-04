#!/usr/bin/env python

"""
FilteredWebSocket: Morgan (Reece) Phillips @linuxpoetry linux-poetry.com

Create WebSocket servers by composing filter chains.

"""

from twisted.internet.protocol import Factory
from twisted.internet import reactor
from TwistedWebsocket.server import Protocol
import argparse
import ssl
import sys

from storage_objects.default_storage_object import DefaultStorageObject
from filters.base import (
    WebSocketDataFilter,
    WebSocketMessageFilter,
    WebSocketDisconnectFilter,
)


class FilteredWebSocket(Protocol):

    def __init__(self, *args, **kwargs):

        # The storage object can be backed by a local data structure or a
        # remote storage device.  However, it must always behave like a
        # defaultdict(set)
        self.storage_object = kwargs.pop("storage_object")

        # The token object may be leveraged for authentication via OAuth,
        # session keys, or other such methods.  See the
        # token_broadcast_filters module for an example.
        self.token = kwargs.pop("token")

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

    def buildProtocol(self, _address):
        return FilteredWebSocket(
            self.users,
            storage_object=self.storage_object,
            token=self.token
        )


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
        "-key",
        help="A key file (ssl)."
    )
    parser.add_argument(
        "-cert",
        help="A certificate file (ssl)."
    )
    parser.add_argument(
        "-token",
        help="Set a default token."
    )
    return parser


def build_reactor(options, **kwargs):
    if options.key and options.cert:
        with open(options.key) as keyFile:
            with open(options.cert) as certFile:
                cert = ssl.PrivateCertificate.loadPEM(keyFile.read() + certFile.read())
                reactor.listenSSL(options.port, FilteredWebSocketFactory(**kwargs), cert.options())
    else:
        reactor.listenTCP(
            options.port,
            FilteredWebSocketFactory(**kwargs)
        )


if __name__ == '__main__':
    from filters import token_broadcast_filters # NOQA
    from storage_objects.redis_storage_object import RedisStorageObject, redis_subparser

    parser = default_parser()
    parser = redis_subparser(parser)
    options = parser.parse_args(sys.argv[1:])

    extra = {
        "storage_object": RedisStorageObject(
            host=options.redis_host,
            port=options.redis_port,
            key=options.redis_key
        )
    }

    build_reactor(options, **extra)
    reactor.run()
