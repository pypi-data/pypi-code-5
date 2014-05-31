#!/usr/bin/env python

from twisted import internet
import twisted.internet.ssl
import twisted.internet.reactor
import twisted.internet.protocol

class CursedLichClient(internet.protocol.Protocol):
    def connectionMade(self):
        self.transport.write('hello, world!')

    def dataReceived(self, data):
        print(data)
        self.transport.loseConnection()

def init_client(addr, port, ssl=False):
    factory = internet.protocol.ClientFactory()
    factory.protocol = CursedLichClient
    if ssl:
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
