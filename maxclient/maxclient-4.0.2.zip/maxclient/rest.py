from copy import deepcopy
from functools import partial
from hashlib import sha1
from maxclient.client import BaseClient
from maxclient.defaults import ENDPOINT_METHOD_DEFAULTS
from maxclient.resources import RESOURCES as ROUTES
from maxclient.utils import RUDict
from maxclient.utils import expand
from maxclient.utils import patch_send
from urllib import urlencode

import json
import re
import requests


class ResourceVariableWrappers(object):
    """
        Container to all the defined variable wrappers
    """

    def _username_(self, resource, value):
        """
            Adapter to {username} variable
            Transforms :me into the current authenticated username
        """
        if value == ':me':
            return resource.client.actor['username']
        else:
            return value

    def _hash_(self, resource, value):
        """
            Adapter to {hash} variable
            Transforms any value into a hash, if it's not already a hash.
        """
        if re.match(r'^[0-9a-f]{40}$', value):
            return value
        else:
            return sha1(value).hexdigest()


class RequestError(Exception):
    """
    """
    def __init__(self, code, *args, **kwargs):
        super(RequestError, self).__init__(*args, **kwargs)
        self.code = code


class Resource(object):
    """
    """

    def __init__(self, parent, attr):
        self.client = parent.client
        self.parent = parent
        self._name = attr
        self.routes = parent.routes[attr]

    @property
    def path(self):
        return '/'.join([self.parent.path, self._name])

    def defaults(self, method):
        default_name = '{}_{}'.format(self.route, method)
        return ENDPOINT_METHOD_DEFAULTS.get(default_name, {})

    @property
    def uri(self):
        return self.client.url + self.path

    @property
    def route(self):
        return '/'.join([self.parent.route, self._name])

    def __call__(self):
        return self.get()

    def __getattr__(self, attr):
        """
            Returns a ResourceCollection  if the accessed attribute mathes
            a valid point in the current routes map
        """
        if attr in self.routes.keys():
            return ResourceCollection(self, attr)
        elif attr in ['get', 'post', 'put', 'delete', 'head']:
            # Returns a prefilled _make_request_ with the resource and method
            # The resulting function will be the one that the client will fill
            # with request parameters
            return partial(self.client._make_request_, self, attr)
        return AttributeError("Resource not found {}".format(attr))


class ResourceCollection(Resource):
    """
    """

    def __repr__(self):
        return '<Lazy Resource Collection @ "{}">'.format(self.path)

    def __getitem__(self, key):
        """
            Returns a ResourceItem representing a Item on the collection
        """

        return ResourceItem(self, key)


class ResourceItem(Resource):
    """
    """

    wrappers = ResourceVariableWrappers()

    def __init__(self, parent, attr):
        self.parent = parent
        self.client = parent.client
        self.rest_param = self.get_rest_param()
        self._name = self.parse_rest_param(attr)
        self.routes = parent.routes[self.rest_param]

    @property
    def route(self):
        return '/'.join([self.parent.route, self.rest_param])

    def parse_rest_param(self, value):
        """
            Transparently adapt values based on variable definitions
            return raw value if no adapation defined for variable
        """
        wrapper_method_name = re.sub(r'{(.*?)}', r'_\1_', self.rest_param)
        wrapper_method = getattr(self.wrappers, wrapper_method_name, None)
        if wrapper_method is None:
            return value
        else:
            return wrapper_method(self, value)

    def get_rest_param(self):
        """
            Searches for variable wrappers {varname} in the current level routes.
            There should be only one available {varname} for each level, so first one is
            returned, otherwise an exception is raised.
        """
        resource_wrappers = [a for a in self.parent.routes.keys() if re.match(r'{.*?}', a)]
        if resource_wrappers:
            if len(resource_wrappers) != 1:
                raise KeyError("Resource collection {} has more than one wrapper defined".format(self.parent.path))
            return resource_wrappers[0]
        raise KeyError("<Resource Item {}".format(self.parent.path))

    def __repr__(self):
        return '<Lazy Resource Item @ {}>'.format(self.path)

    def __getitem__(self, key):
        """
            Returns a ResourceItem representing a Item on the Item
        """

        return ResourceItem(self, key)


class MaxClient(BaseClient):

    path = ''
    route = ''

    def __init__(self, *args, **kwargs):
        super(MaxClient, self).__init__(*args, **kwargs)
        self.last_response = None
        self.last_response_code = None

        self.debug = kwargs.get('debug', False)
        if self.debug:
            patch_send()

    def do_request(self, route, method_name, uri, params):
        method = getattr(requests, method_name)
        return method(uri, **params)

    def response_content(self, response):
        return response.content

    def _make_request_(self, resource, method_name, default_filename='file', data=None, qs=None, **kwargs):
        """
            Prepare call parameters  based on method_name, and
            make the appropiate call using requests.
            Responses with an error will raise an exception
        """
        #extract file uploads from kwargs
        file_uploads = []
        for k, v in kwargs.items():
            is_upload_file = re.match(r'^upload_file_?(\w*)$', k)
            if is_upload_file:
                captured_form_file_id = is_upload_file.groups()[0]
                form_file_id = captured_form_file_id if captured_form_file_id else 'file'
                file_uploads.append({
                    'form_file_id': form_file_id,
                    'file': v
                })
                del kwargs[k]

        # User has provided us the constructed query
        if data is not None:
            if isinstance(data, dict):
                query = RUDict(data)
            else:
                query = data

        # Otherwise construct it from kwargs, based on defaults (if any)
        else:
            query = RUDict(deepcopy(resource.defaults(method_name)))
            query.update(expand(kwargs))

        # Construct uri with optional query string
        uri = resource.uri
        if qs is not None:
            uri = '{}?{}'.format(uri, urlencode(qs))

        # Set default requests parameters
        headers = {}
        headers.update(self.client.OAuth2AuthHeaders())
        method_kwargs = {
            'headers': headers,
            'verify': False
        }

        # Add query to body only in this methods

        if method_name in ['post', 'put', 'delete']:
            if file_uploads:
                method_kwargs['files'] = {}
                for file_upload in file_uploads:
                    # Get name of open file, excluding path part,
                    # fallback to default if object has no name attribute (i.e StringIO)
                    # Finally feed file contents into request arguments
                    object_filename = getattr(file_upload['file'], 'name', default_filename)
                    filename = re.match(r'^.*?/?([^\/]*$)', object_filename).groups()[0]
                    method_kwargs['files'][file_upload['form_file_id']] = (filename, file_upload['file'].read())
                if query:
                    method_kwargs['data'] = {'json_data': json.dumps(query)}

            else:
                headers['content-type'] = 'application/json'
                method_kwargs['data'] = json.dumps(query)
        # call corresponding request method
        response = self.do_request(resource.route, method_name, uri, method_kwargs)

        # Save response status to be able to query on succesfull responses
        self.last_response = self.response_content(response)
        self.last_response_code = response.status_code

        # Legitimate max 404 NotFound responses get a None in response
        # 404 responses caused by unimplemented methods, raise an exception
        if response.status_code in [404]:
            try:
                response_text = self.response_content(response)
                json.loads(response_text)
                if self.debug:
                    print response_text
                return None
            except ValueError:
                # In case that we are accessing to an non existing resource, not
                # to a not implemented method thus the return is 404 legitimate,
                # and we need to inform of it
                if method_name == 'head':
                    method = getattr(requests, 'get')
                    response = method(uri, **method_kwargs)
                    json_error = json.loads(self.response_content(response))
                    error_message = "{error}: {error_description}".format(**json_error)
                    raise RequestError(404, error_message)
                else:
                    raise RequestError(404, "Not Implemented: {} doesn't accept method {}".format(resource.uri, method_name))

        # Some proxy lives between max and the client, and something went wrong
        # on the backend site, probably max is stopped
        elif response.status_code in [502]:
            raise RequestError(502, "Server {} responded with 502. Is max running?".format(self.url))

        # Successfull requests gets the json response in return
        # except HEAD ones, that gets the count
        elif response.status_code in [200, 201, 204]:
            if method_name == 'head':
                return int(response.headers.get('X-totalItems', 0))
            else:
                try:
                    return json.loads(self.response_content(response))
                except:
                    # post avatar currently returns 'Uploaded' plain text...
                    return self.response_content(response)

        # Everything else is treated as a max error response,
        # and so we expect to contain json, otherwise is an unknown error
        else:
            try:
                json_error = json.loads(self.response_content(response))
                error_message = "{error}: {error_description}".format(**json_error)
            except:
                error_message = "Server responded with error {}".format(response.status_code)
            raise RequestError(response.status_code, error_message)

    @property
    def client(self):
        return self

    def getRoute(self, path):
        for route_name, route in ROUTES.items():
            if path == route['route']:
                return route
        return {}

    @property
    def routes(self):
        """
            Parses the endpoint list on ROUTES, and transforms it to be accessed dict-like
            level by level.
        """
        routes = {}
        for route_name, route in ROUTES.items():
            parts = route['route'].split('/')[1:]
            last_path = routes
            for part in parts:
                last_path = last_path.setdefault(part, {})

        return routes

    def __getattr__(self, attr):
        """
            Returns a ResourceCollection  if the accessed attribute mathes
            a valid point in the current routes map
        """
        if attr in self.routes.keys():
            return ResourceCollection(self, attr)
        return AttributeError('Resource not found "{}"'.format(attr))
