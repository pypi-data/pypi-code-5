
import os
import socket

from .Communicator import Communicator
from .WiseAdmin import WiseAdmin
import Logging as logger


__ic = None


def initialize(host="127.0.0.1", port=8080, properties=None):
    global __ic
    assert __ic is None, "Only one communicator instance is supported"

    properties = properties or {}

    if properties.get("TornadoApp.debug", False):
        logger.warning("Wise: Debug Mode enabled, remove on production!!")

    host = host or socket.gethostbyname_ex(socket.gethostname())[0]
    __ice = Communicator(host=host, port=port, properties=properties)
    __ice.is_ready.wait()

    admin_adapter = __ice.createObjectAdapter("WiseAdmin", "-w wise")
    servant = WiseAdmin(__ice)
    admin_adapter.add(servant, "WiseAdmin")

    return __ice


def dirname(path):
    return os.path.abspath(os.path.dirname(path))


class Application(object):
    def __init__(self):
        self.broker = initialize()

    def main(self, argv=None):
        self.run(argv or [])


def add_placeholder(method):
    def deco(*args):
        return method(*args[:-1])
    return deco


class proxy_as_servant(object):
    def __init__(self, proxy):
        for name in proxy.wise_getMethodNames():
            setattr(self, name, add_placeholder(getattr(proxy, name)))
