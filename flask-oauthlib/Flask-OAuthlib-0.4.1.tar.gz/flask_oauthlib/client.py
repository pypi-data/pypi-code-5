# coding: utf-8
"""
    flask_oauthlib.client
    ~~~~~~~~~~~~~~~~~~~~~

    Implemnts OAuth1 and OAuth2 support for Flask.

    :copyright: (c) 2013 by Hsiaoming Yang.
"""

import logging
import oauthlib.oauth1
import oauthlib.oauth2
from functools import wraps
from oauthlib.common import to_unicode, PY3, add_params_to_uri
from flask import request, redirect, json, session, current_app
from werkzeug import url_quote, url_decode, url_encode
from werkzeug import parse_options_header, cached_property
try:
    from urlparse import urljoin
    import urllib2 as http
except ImportError:
    from urllib import request as http
    from urllib.parse import urljoin
log = logging.getLogger('flask_oauthlib')


__all__ = ('OAuth', 'OAuthRemoteApp', 'OAuthResponse', 'OAuthException')


class OAuth(object):
    """Registry for remote applications.

    :param app: the app instance of Flask

    Create an instance with Flask::

        oauth = OAuth(app)
    """

    def __init__(self, app=None):
        self.remote_apps = {}

        self.app = app
        if app:
            self.init_app(app)

    def init_app(self, app):
        """Init app with Flask instance.

        You can also pass the instance of Flask later::

            oauth = OAuth()
            oauth.init_app(app)
        """
        self.app = app
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['oauthlib.client'] = self

    def remote_app(self, name, register=True, **kwargs):
        """Registers a new remote application.

        :param name: the name of the remote application
        :param register: whether the remote app will be registered

        Find more parameters from :class:`OAuthRemoteApp`.
        """
        remote = OAuthRemoteApp(self, name, **kwargs)
        if register:
            assert name not in self.remote_apps
            self.remote_apps[name] = remote
        return remote

    def __getattr__(self, key):
        try:
            return object.__getattribute__(self, key)
        except AttributeError:
            app = self.remote_apps.get(key)
            if app:
                return app
            raise AttributeError('No such app: %s' % key)


_etree = None


def get_etree():
    global _etree
    if _etree is not None:
        return _etree
    try:
        from lxml import etree as _etree
    except ImportError:
        try:
            from xml.etree import cElementTree as _etree
        except ImportError:
            try:
                from xml.etree import ElementTree as _etree
            except ImportError:
                raise TypeError('lxml or etree not found')
    return _etree


def parse_response(resp, content, strict=False, content_type=None):
    """Parse the response returned by :meth:`OAuthRemoteApp.http_request`.

    :param resp: response of http_request
    :param content: content of the response
    :param strict: strict mode for form urlencoded content
    :param content_type: assign a content type manually
    """
    if not content_type:
        content_type = resp.headers.get('content-type', 'application/json')
    ct, options = parse_options_header(content_type)

    if ct in ('application/json', 'text/javascript'):
        return json.loads(content)

    if ct in ('application/xml', 'text/xml'):
        return get_etree().fromstring(content)

    if ct != 'application/x-www-form-urlencoded' and strict:
        return content
    charset = options.get('charset', 'utf-8')
    return url_decode(content, charset=charset).to_dict()


def prepare_request(uri, headers=None, data=None, method=None):
    """Make request parameters right."""
    if headers is None:
        headers = {}

    if data and not method:
        method = 'POST'
    elif not method:
        method = 'GET'

    if method == 'GET' and data:
        uri = add_params_to_uri(uri, data)
        data = None

    return uri, headers, data, method


def encode_request_data(data, format):
    if format is None:
        return data, None
    if format == 'json':
        return json.dumps(data or {}), 'application/json'
    if format == 'urlencoded':
        return url_encode(data or {}), 'application/x-www-form-urlencoded'
    raise TypeError('Unknown format %r' % format)


class OAuthResponse(object):
    def __init__(self, resp, content, content_type=None):
        self._resp = resp
        self.raw_data = content
        self.data = parse_response(
            resp, content, strict=True,
            content_type=content_type,
        )

    @property
    def status(self):
        """The status code of the response."""
        return self._resp.code


class OAuthException(RuntimeError):
    def __init__(self, message, type=None, data=None):
        self.message = message
        self.type = type
        self.data = data

    def __str__(self):
        if PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message


class OAuthRemoteApp(object):
    """Represents a remote application.

    :param oauth: the associated :class:`OAuth` object
    :param name: the name of the remote application
    :param base_url: the base url for every request
    :param request_token_url: the url for requesting new tokens
    :param access_token_url: the url for token exchange
    :param authorize_url: the url for authorization
    :param consumer_key: the application specific consumer key
    :param consumer_secret: the application specific consumer secret
    :param request_token_params: an optional dictionary of parameters
                                 to forward to the request token url
                                 or authorize url depending on oauth
                                 version
    :param access_token_params: an optional dictionary of parameters to
                                forward to the access token url
    :param access_token_method: the HTTP method that should be used for
                                the access_token_url. Default is ``GET``
    :param content_type: force to parse the content with this content_type,
                         usually used when the server didn't return the
                         right content type.

    .. versionadded:: 0.3.0

    :param app_key: lazy load configuration from Flask app config with
                    this app key
    """
    def __init__(
        self, oauth, name,
        base_url=None,
        request_token_url=None,
        access_token_url=None,
        authorize_url=None,
        consumer_key=None,
        consumer_secret=None,
        request_token_params=None,
        access_token_params=None,
        access_token_method=None,
        content_type=None,
        app_key=None,
        encoding='utf-8',
    ):
        self.oauth = oauth
        self.name = name

        if (not consumer_key or not consumer_secret) and not app_key:
            raise TypeError(
                'OAuthRemoteApp requires consumer key and secret'
            )

        self._base_url = base_url
        self._request_token_url = request_token_url
        self._access_token_url = access_token_url
        self._authorize_url = authorize_url
        self._consumer_key = consumer_key
        self._consumer_secret = consumer_secret
        self._request_token_params = request_token_params
        self._access_token_params = access_token_params
        self._access_token_method = access_token_method
        self._content_type = content_type
        self._tokengetter = None

        self.app_key = app_key
        self.encoding = encoding

    @cached_property
    def base_url(self):
        return self._get_property('base_url')

    @cached_property
    def request_token_url(self):
        return self._get_property('request_token_url', None)

    @cached_property
    def access_token_url(self):
        return self._get_property('access_token_url')

    @cached_property
    def authorize_url(self):
        return self._get_property('authorize_url')

    @cached_property
    def consumer_key(self):
        return self._get_property('consumer_key')

    @cached_property
    def consumer_secret(self):
        return self._get_property('consumer_secret')

    @cached_property
    def request_token_params(self):
        return self._get_property('request_token_params', {})

    @cached_property
    def access_token_params(self):
        return self._get_property('access_token_params', {})

    @cached_property
    def access_token_method(self):
        return self._get_property('access_token_method', 'GET')

    @cached_property
    def content_type(self):
        return self._get_property('content_type', None)

    def _get_property(self, key, default=False):
        attr = getattr(self, '_%s' % key)
        if attr is not None:
            return attr
        if not self.app_key:
            if default is not False:
                return default
            return attr
        app = self.oauth.app or current_app
        if self.app_key in app.config:
            # works with dict config
            config = app.config[self.app_key]
            if default is not False:
                return config.get(key, default)
            return config[key]
        # works with plain text config
        config_key = "%s_%s" % (self.app_key, key.upper())
        if default is not False:
            return app.config.get(config_key, default)
        return app.config[config_key]

    def make_client(self, token=None):
        # request_token_url is for oauth1
        if self.request_token_url:
            client = oauthlib.oauth1.Client(
                self.consumer_key, self.consumer_secret
            )

            params = self.request_token_params or {}
            if 'signature_method' in params:
                client.signature_method = _encode(params['signature_method'])
            if 'rsa_key' in params:
                client.rsa_key = _encode(params['rsa_key'])
            if 'signature_type' in params:
                client.signature_type = _encode(params['signature_type'])

            if token and isinstance(token, (tuple, list)):
                client.resource_owner_key, client.resource_owner_secret = token
        else:
            if token and isinstance(token, (tuple, list)):
                token = {'access_token': token[0]}
            client = oauthlib.oauth2.WebApplicationClient(
                self.consumer_key, token=token
            )
        return client

    @staticmethod
    def http_request(uri, headers=None, data=None, method=None):
        uri, headers, data, method = prepare_request(
            uri, headers, data, method
        )

        log.debug('Request %r with %r method' % (uri, method))
        req = http.Request(uri, headers=headers, data=data)
        req.get_method = lambda: method.upper()
        try:
            resp = http.urlopen(req)
            content = resp.read()
            resp.close()
            return resp, content
        except http.HTTPError as resp:
            content = resp.read()
            resp.close()
            return resp, content

    def get(self, *args, **kwargs):
        """Sends a ``GET`` request. Accepts the same paramters as
        :meth:`request`.
        """
        kwargs['method'] = 'GET'
        return self.request(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Sends a ``POST`` request. Accepts the same paramters as
        :meth:`request`.
        """
        kwargs['method'] = 'POST'
        return self.request(*args, **kwargs)

    def put(self, *args, **kwargs):
        """Sends a ``PUT`` request. Accepts the same paramters as
        :meth:`request`.
        """
        kwargs['method'] = 'PUT'
        return self.request(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Sends a ``DELETE`` request. Accepts the same paramters as
        :meth:`request`.
        """
        kwargs['method'] = 'DELETE'
        return self.request(*args, **kwargs)

    def request(self, url, data=None, headers=None, format='urlencoded',
                method='GET', content_type=None, token=None):
        """
        Sends a request to the remote server with OAuth tokens attached.

        :param data: the data to be sent to the server.
        :param headers: an optional dictionary of headers.
        :param format: the format for the `data`. Can be `urlencoded` for
                       URL encoded data or `json` for JSON.
        :param method: the HTTP request method to use.
        :param content_type: an optional content type. If a content type
                             is provided, the data is passed as it, and
                             the `format` is ignored.
        :param token: an optional token to pass, if it is None, token will
                      be generated be tokengetter.
        """

        headers = dict(headers or {})
        if not token:
            token = self.get_request_token()

        client = self.make_client(token)
        url = self.expand_url(url)
        if method == 'GET':
            assert format == 'urlencoded'
            if data:
                url = add_params_to_uri(url, data)
                data = None
        else:
            if content_type is None:
                data, content_type = encode_request_data(data, format)
            if content_type is not None:
                headers['Content-Type'] = content_type

        if self.request_token_url:
            # oauth1
            uri, headers, body = client.sign(
                url, http_method=method, body=data, headers=headers
            )
        else:
            # oauth2
            uri, headers, body = client.add_token(
                url, http_method=method, body=data, headers=headers
            )

        if hasattr(self, 'pre_request'):
            # this is desgined for some rubbish service like weibo
            # since they don't follow the standards, we need to
            # change the uri, headers, or body
            uri, headers, body = self.pre_request(uri, headers, body)

        resp, content = self.http_request(
            uri, headers, data=body, method=method
        )
        return OAuthResponse(resp, content, self.content_type)

    def authorize(self, callback=None):
        """
        Returns a redirect response to the remote authorization URL with
        the signed callback given.
        """
        if self.request_token_url:
            token = self.generate_request_token(callback)[0]
            url = '%s?oauth_token=%s' % (
                self.expand_url(self.authorize_url), url_quote(token)
            )
        else:
            assert callback is not None, 'Callback is required OAuth2'

            params = dict(self.request_token_params) or {}
            client = self.make_client()

            if 'scope' in params:
                scope = params.pop('scope')
            else:
                scope = None

            if isinstance(scope, str):
                # oauthlib need unicode
                scope = _encode(scope, self.encoding)

            session['%s_oauthredir' % self.name] = callback
            url = client.prepare_request_uri(
                self.expand_url(self.authorize_url),
                redirect_uri=callback,
                scope=scope,
                **params
            )
        return redirect(url)

    def tokengetter(self, f):
        """
        Register a function as token getter.
        """
        self._tokengetter = f
        return f

    def expand_url(self, url):
        return urljoin(self.base_url, url)

    def generate_request_token(self, callback=None):
        # for oauth1 only
        if callback is not None:
            callback = urljoin(request.url, callback)

        client = self.make_client()
        client.callback_uri = _encode(callback, self.encoding)

        realm = self.request_token_params.get('realm')
        realms = self.request_token_params.get('realms')
        if not realm and realms:
            realm = ' '.join(realms)
        uri, headers, _ = client.sign(
            self.expand_url(self.request_token_url), realm=realm
        )
        log.debug('Generate request token header %r', headers)
        resp, content = self.http_request(uri, headers)
        if resp.code not in (200, 201):
            raise OAuthException(
                'Failed to generate request token',
                type='token_generation_failed'
            )
        data = parse_response(resp, content)
        if data is None:
            raise OAuthException(
                'Invalid token response from %s' % self.name,
                type='token_generation_failed'
            )
        tup = (data['oauth_token'], data['oauth_token_secret'])
        session['%s_oauthtok' % self.name] = tup
        return tup

    def get_request_token(self):
        assert self._tokengetter is not None, 'missing tokengetter'
        rv = self._tokengetter()
        if rv is None:
            raise OAuthException('No token available', type='token_missing')
        return rv

    def handle_oauth1_response(self):
        """Handles an oauth1 authorization response."""
        client = self.make_client()
        client.verifier = request.args.get('oauth_verifier')
        tup = session.get('%s_oauthtok' % self.name)
        client.resource_owner_key = tup[0]
        client.resource_owner_secret = tup[1]

        uri, headers, data = client.sign(
            self.expand_url(self.access_token_url),
            _encode(self.access_token_method)
        )

        resp, content = self.http_request(uri, headers, data)
        data = parse_response(resp, content)
        if resp.code not in (200, 201):
            raise OAuthException(
                'Invalid response from %s' % self.name,
                type='invalid_response', data=data
            )
        return data

    def handle_oauth2_response(self):
        """Handles an oauth2 authorization response."""

        client = self.make_client()
        remote_args = {
            'code': request.args.get('code'),
            'client_secret': self.consumer_secret,
            'redirect_uri': session.get('%s_oauthredir' % self.name)
        }
        log.debug('Prepare oauth2 remote args %r', remote_args)
        remote_args.update(self.access_token_params)
        if self.access_token_method == 'POST':
            body = client.prepare_request_body(**remote_args)
            resp, content = self.http_request(
                self.expand_url(self.access_token_url),
                data=body,
                method=self.access_token_method,
            )
        elif self.access_token_method == 'GET':
            qs = client.prepare_request_body(**remote_args)
            url = self.expand_url(self.access_token_url)
            url += ('?' in url and '&' or '?') + qs
            resp, content = self.http_request(
                url,
                method=self.access_token_method,
            )
        else:
            raise OAuthException(
                'Unsupported access_token_method: %s' %
                self.access_token_method
            )

        data = parse_response(resp, content, content_type=self.content_type)
        if resp.code not in (200, 201):
            raise OAuthException(
                'Invalid response from %s' % self.name,
                type='invalid_response', data=data
            )
        return data

    def handle_unknown_response(self):
        """Handles a unknown authorization response."""
        return None

    def authorized_handler(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if 'oauth_verifier' in request.args:
                try:
                    data = self.handle_oauth1_response()
                except OAuthException as e:
                    data = e
            elif 'code' in request.args:
                try:
                    data = self.handle_oauth2_response()
                except OAuthException as e:
                    data = e
            else:
                data = self.handle_unknown_response()

            # free request token
            session.pop('%s_oauthtok' % self.name, None)
            session.pop('%s_oauthredir' % self.name, None)
            return f(*((data,) + args), **kwargs)
        return decorated


def _encode(text, encoding='utf-8'):
    if encoding:
        return to_unicode(text, encoding)
    return text
