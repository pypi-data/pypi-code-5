from max import main
from maxclient.rest import MaxClient as RestClient
from webtest.app import TestApp
from StringIO import StringIO


class RequesterApp(TestApp):
    """
        Simplified version of webtest.app.TestApp with a modified
        do_request method,  without cookie handling and testing variables

    """

    def do_request(self, req, status, expect_errors):
        errors = StringIO()
        req.environ['wsgi.errors'] = errors
        script_name = req.environ.get('SCRIPT_NAME', '')
        if script_name and req.path_info.startswith(script_name):
            req.path_info = req.path_info[len(script_name):]

        res = req.get_response(self.app, catch_exc_info=True)

        res.decode_content()

        try:
            res.body
        except TypeError:
            pass
        res.errors = errors.getvalue()

        return res


class MaxClient(RestClient):
    """
        WSGI spinoff based on the rest client, that instantiates a max app
        without opening any port or socket
    """
    path = ''
    route = ''
    app = None

    def setToken(self, oauth2_token):
        """
            Instantiates a fallback RestClient to use with fileserver dependant endpoints
            This has to be executed after the original setToken, to be sure that
            the oauth_server has been set or fetched from the maxserver info endpoint.
        """
        super(MaxClient, self).setToken(oauth2_token)
        self.rest = RestClient(self.url, oauth_server=self.oauth_server)
        self.rest.actor = self.actor
        self.rest.token = self.token
        self.settings = self.rest.info.settings.get()
        self.settings['max.include_traceback_in_500_errors'] = True

        # Reset url after modification, to make requests trough the wsgi app
        self.url = ''

    @property
    def requester(self):
        if self.app is None:
            self.app = RequesterApp(main({}, **self.settings))
        return self.app

    def do_request(self, route, method_name, uri, params):
        """
            If request contains files to upload, delegate call
            to the fallback rest client
        """
        if params.get('files', {}):
            return self.rest.do_request(route, method_name, self.rest.url + uri, params)

        method = getattr(self.requester, method_name)
        method_kwargs = {
            'headers': params.get('headers', {})
        }
        if method != 'delete':
            method_kwargs['params'] = params.get('data', '')
        return method(uri, **method_kwargs)

    def response_content(self, response):
        return response.text
