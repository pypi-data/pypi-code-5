
class WSGI(BaseInterface):
    def handle(self, environ, start_response):
        c = self.get_call_instance(environ)
        res = c.handle()

        start_response(
            '{} {}'.format(res.code, res.status),
            [(k, v) for k, v in res.headers.iteritems()]
        )
        return [res.body]

    def get_request_instance(self, environ, *args, **kwargs):
        r = Request()
        for k, v in environ.iteritems():
            if k.startswith('HTTP_'):
                r.headers[k[5:]] = v

        r.method = environ['REQUEST_METHOD']
        r.path = environ['PATH_INFO']
        r.query = environ['QUERY_STRING']
        r.environ = environ

        if r.is_method('POST'):
            r.body = environ['wsgi.input'].read()

        return r

    def __call__(self, environ, start_response):
        return self.handle(environ, start_response)


