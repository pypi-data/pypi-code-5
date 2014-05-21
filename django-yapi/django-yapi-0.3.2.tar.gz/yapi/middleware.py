# Snippet taken from:
# https://gist.github.com/426829/9ff9b8337d61d40978ab22080cf424e8242ab97b

from django import http
from django.conf import settings


class XsSharing(object):
    """
    This middleware allows cross-domain XHR using the html5 postMessage API.
    
    Access-Control-Allow-Origin: http://foo.example
    Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE
    """
    def process_request(self, request):
        if 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
            response = http.HttpResponse()
            response['Access-Control-Allow-Origin']  = settings.YAPI['XS_SHARING_ALLOWED_ORIGINS'] 
            response['Access-Control-Allow-Methods'] = ",".join(settings.YAPI['XS_SHARING_ALLOWED_METHODS'])
            response['Access-Control-Allow-Headers'] = 'X-Requested-With, Authorization, X-Prototype-Version, Content-type'
            return response
        else:
            return None
    
    def process_response(self, request, response):
        # Avoid unnecessary work
        if response.has_header('Access-Control-Allow-Origin'):
            return response
        else:
            response['Access-Control-Allow-Origin']  = settings.YAPI['XS_SHARING_ALLOWED_ORIGINS'] 
            response['Access-Control-Allow-Methods'] = ",".join(settings.YAPI['XS_SHARING_ALLOWED_METHODS'])
            response['Access-Control-Allow-Headers'] = 'X-Requested-With, Authorization, X-Prototype-Version, Content-type'
            return response