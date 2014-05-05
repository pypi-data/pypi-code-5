# -*- coding: utf-8 -*-
from twisted.words.protocols.jabber import xmlstream, client
from twisted.words.xish import domish
from time import time


__author__ = 'badim'


def jabberClientFactory(jid, secret, ping_timeout, ping_fail_time, host):

    class PingXmlStream(xmlstream.XmlStream):
        def __init__(self, authenticator):
            xmlstream.XmlStream.__init__(self, authenticator)
            self.ping_received_time = time()

        def connectionMade(self):
            xmlstream.XmlStream.connectionMade(self)
            self._callLater(ping_timeout, self.checkPong)

        def checkPong(self):
            self.sendPing()
            if time() - self.ping_received_time >= ping_fail_time:
                self.transport.loseConnection()
            else:
                self._callLater(ping_timeout, self.checkPong)

        def sendMessage(self, to, message):
            msg = domish.Element(("jabber:client", "message"))
            msg["to"] = to
            msg.addElement("body", content=message)
            self.send(msg)

        def sendPing(self):
            self.sendMessage("echo.{0}".format(host), "ping")

        def receivePing(self):
            self.ping_received_time = time()


    class ReconnectClientFactory(xmlstream.XmlStreamFactory):
        protocol = PingXmlStream

        def __init__(self, authenticator):
            xmlstream.XmlStreamFactory.__init__(self, authenticator)
            self.maxDelay = 10

    a = client.BasicAuthenticator(jid, secret)
    return ReconnectClientFactory(a)
