from functools import wraps
from .base_exceptions import Fault

class RPCExceptionHandler(object):
    def __init__(self, exceptions):
        if isinstance(exceptions, type):
            exceptions = [ exceptions, ]
        self.exceptions = exceptions
        self.wrapped_exceptions  = tuple(e for e in exceptions)
        self.unwrapped_exceptions = dict(((e.code, e.api_name), e) for e in self.wrapped_exceptions)

    def get_exception_instance(self, code, api_name, message=None, data=None):
        ''' Coerce a wrapped exception its original exception instance '''
        return self.get_exception(code, api_name)(remote_message=message, remote_data=data)

    def get_exception(self, code, api_name):
        ''' Coerce a wrapped exception into its original exception type '''
        return self.unwrapped_exceptions[( code, api_name)]

    def wrap_rpc_exception(self, f):
        ''' Catch an exception in WRAPPED_EXS and coerce it to a jsonrpclib Fault '''
        @wraps(f)
        def wrapped(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except self.wrapped_exceptions as e:
                return Fault(e.code, e.msg)
        return wrapped
