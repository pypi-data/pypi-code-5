class Fault(object):
    # cribbed from jsonrpclib https://github.com/joshmarshall/jsonrpclib/blob/master/jsonrpclib/jsonrpc.py
    # JSON-RPC error class
    def __init__(self, code=-32000, message='Server error'):
        self.faultCode = code
        self.faultString = message

    def error(self):
        return {'code':self.faultCode, 'message':self.faultString}

class WrappedRPCError(Exception):
    def __init__(self, code, remote_message, remote_data=None):
        self.args = (code, remote_message, remote_data)
        self.code = code
        self.msg = remote_message or self._default_message
        self.data = remote_data

    def __repr__(self):
        return u"%s(%r, %r, %r)"%(self.__class__.__name__, self.args[0], self.args[1], self.args[2])
