from importlib import import_module
import sys

from django.conf import settings
from django.http import Http404
from django.utils import six

from floraconcierge import shortcuts
from floraconcierge.client import ApiClient
from floraconcierge.errors import ResultObjectNotFoundError


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class designated by the
    last name in the path. Raise ImportError if the import failed.

    Helper function from django 1.7
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "%s doesn't look like a module path" % dotted_path
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    # noinspection PyUnboundLocalVariable
    module = import_module(module_path)

    try:
        # noinspection PyUnboundLocalVariable
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "%s" does not define a "%s" attribute/class' % (
            dotted_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def initialize_apiclient(request):
    err_pattern = 'floraconcierge.middleware.ApiClientMiddleware requires to be set settings.%s'

    api_id = getattr(settings, 'FLORACONCIERGE_API_ID', None)
    if not api_id:
        raise ValueError(err_pattern % 'FLORACONCIERGE_API_ID')

    secret = getattr(settings, 'FLORACONCIERGE_API_SECRET', None)
    if not secret:
        raise ValueError(err_pattern % 'FLORACONCIERGE_API_SECRET')

    client = ApiClient(api_id, secret)

    sess_env = request.session.get("__floraconcierge_api_env", None)
    restored = False
    if sess_env:
        client.env = sess_env
        restored = True

    init_env = getattr(settings, 'FLORACONCIERGE_API_INIT_ENV', None)
    if init_env:
        init_env = import_string(init_env)
        env = init_env(client, request, restored)
        if env:
            client.env = env

    return client


class ApiClientMiddleware(object):
    def process_request(self, request):
        init = getattr(settings, 'FLORACONCIERGE_API_INIT_CLIENT', None)
        if init:
            init = import_string(init)
            client = init(request)
        else:
            client = initialize_apiclient(request)

        request.api = client
        request.apienv = client.env

        shortcuts.activate(client)

    def process_response(self, request, response):
        request.session['__floraconcierge_api_env'] = getattr(request, 'apienv', None)

        return response


class ApiObjectNotFound404(object):
    def process_exception(self, request, exception):
        if isinstance(exception, ResultObjectNotFoundError):
            raise Http404
