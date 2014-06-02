#!/usr/bin/env python

from twisted import internet
import twisted.internet.ssl
import twisted.internet.reactor
import twisted.internet.protocol

from google.protobuf.message import DecodeError

import net_pb2

__version__ = 1

class CursedLichClient(internet.protocol.Protocol):
    username=None
    password=None
    
    def __init__(self):
        self.request_id = 1

    def connectionMade(self):
        req = net_pb2.Request()
        req.typ = net_pb2.MT_LOGIN
        req.request_id = self.request_id
        self.request_id += 1
        req.version = __version__
        req.login_request.username = CursedLichClient.username
        req.login_request.password = CursedLichClient.password
        self.transport.write(req.SerializeToString())

    def dataReceived(self, data):
        res = net_pb2.Response()
        try:
            res.ParseFromString(data)
        except DecodeError:
            print('client could not decode data from response: %s' %
                data.encode('hex'))
            return
        print(res.response_id)
        print(res.typ)
        print(res.version)
        print(res.compatible)
        print(res.status)
        print(res.error)
        print(res.login_response.session_id)
        self.transport.loseConnection()

def init_client(addr, port, username, password, insecure=False):
    factory = internet.protocol.ClientFactory()
    CursedLichClient.username = username
    CursedLichClient.password = password
    factory.protocol = CursedLichClient
    if not insecure:
        internet.reactor.connectSSL(
            addr, port, factory, internet.ssl.ClientContextFactory())
    else:
        internet.reactor.connectTCP(
            addr, port, factory)
    internet.reactor.run()

def main():
    from bin import cursed_lich
    cursed_lich()

if __name__ == '__main__':
    main()
