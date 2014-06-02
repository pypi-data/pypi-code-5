#!/usr/bin/python

import socket
import message_pb2

class TrisDbConnection:
    def __init__(self, host, port):
        self.hostname = host
	self.port = port
	try:
	    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	    client.connect((self.hostname, self.port))
	    client.close()
	except:
	    print "Error connecting to %s on port %s" % (self.hostname, self.port)

    def get(self, s, p=None, o=None):
        req = message_pb2.QueryRequest()
	if p is None:
	    req.query = 'GET "%s"' % s
	else:
	    req.query = 'GET "%s" "%s" "%s"' % (s, p, o)
	tmp = self.__sendData(req)
        result = []
        for i in tmp.data:
            result.append({'subject':i.subject, 'predicate':i.predicate, 'object':i.object})
        return result

    def gets(self, s, p, o):
        req = message_pb2.QueryRequest()
        req.query = 'GETS "%s" "%s" "%s"' % (s, p, o)
        tmp = self.__sendData(req)
        result = []
        for i in tmp.data:
            result.append(i.subject)
        return result

    def getp(self, s, p, o):
        req = message_pb2.QueryRequest()
        req.query = 'GETP "%s" "%s" "%s"' % (s, p, o)
        tmp = self.__sendData(req)
        result = []
        for i in tmp.data:
            result.append(i.predicate)
        return result

    def geto(self, s, p, o):
        req = message_pb2.QueryRequest()
        req.query = 'GETO "%s" "%s" "%s"' % (s, p, o)
        tmp = self.__sendData(req)
        result = []
        for i in tmp.data:
            result.append(i.object)
        return result

    def create(self, s, p, o):
        req = message_pb2.QueryRequest()
        req.query = 'CREATE "%s" "%s" "%s"' % (s, p, o)
	tmp = self.__sendData(req)
        result = []
        for i in tmp.data:
            result.append({'subject':i.subject, 'predicate':i.predicate, 'object':i.object})
        return result

    def delete(self, s, p, o):
        req = message_pb2.QueryRequest()
        req.query = 'DELETE "%s" "%s" "%s"' % (s, p, o)
        self.__sendData(req)
        return 'OK'

    def clear(self):
        req = message_pb2.QueryRequest()
        req.query = 'CLEAR'
	self.__sendData(req)
	return 'OK'

    def __sendData(self, request):
	try:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client.connect((self.hostname, self.port))
	    request.timestamp = '123456789'
            client.send(request.SerializeToString())
            data = ""
            while True:
                buf = client.recv(1024)
                if not len(buf):
                    break;
                data += buf
            client.close()
            res = message_pb2.QueryResponse()
            res.ParseFromString(data)
	    return res
        except:
            print "Connection error"
