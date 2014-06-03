#!/usr/bin/env python

from twisted import internet
import twisted.internet.ssl
import twisted.internet.reactor
import twisted.internet.protocol

from google.protobuf.message import DecodeError

import net_pb2

__version__ = 1

class LichClientFactory(internet.protocol.ClientFactory):
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.session_id = None

    def buildProtocol(self, addr):
        self.addr = addr
        return LichClientProtocol(self)

class LichClientProtocol(internet.protocol.Protocol):
    
    def __init__(self, factory):
        self.request_id = 1
        self.factory = factory

    def connectionMade(self):
        self.login()

    def login(self):
        req = net_pb2.Request()
        req.typ = net_pb2.MT_LOGIN
        req.request_id = self.request_id
        self.request_id += 1
        req.version = __version__
        req.login_request.username = self.factory.username
        req.login_request.password = self.factory.password
        self.transport.write(req.SerializeToString())
        self.transport.loseConnection()

    def create_hero(self, name):
        req = net_pb2.Request()
        req.session_id = self.factory.session_id
        req.typ = net_pb2.MT_CREATE_HERO
        req.request_id = self.request_id
        self.request_id += 1
        req.version = __version__
        req.create_hero_request.name = name
        self.transport.write(req.SerializeToString())
        self.transport.loseConnection()

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
        if res.typ == net_pb2.MT_LOGIN:
            self.factory.session_id = res.login_response.session_id
            print(self.factory.session_id)

def init_client(addr, port, username, password, insecure=False):
    factory = LichClientFactory(username, password)
    factory.protocol = LichClientProtocol
    factory.username = username
    factory.password = password
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
