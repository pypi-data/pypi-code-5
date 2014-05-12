"""
middlware to restrict IP addresses
"""

from django import http
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context

from models import BlockedIp


class BotTrapMiddleware(object):

    def get_ip(self, request):
        ip = request.META.get('REMOTE_ADDR', '')
#         if ((not ip or ip == '127.0.0.1' or (ip in self.frontends)) and
#             request.META.has_key('HTTP_X_FORWARDED_FOR')):
#             ip = request.META['HTTP_X_FORWARDED_FOR'].split(',')[-1].strip()
            
        return ip 

    def process_request(self, request):
        ip = self.get_ip(request)
        if BlockedIp.objects.filter(ip=ip).exists():
            return self.forbidden()
        return None

    def forbidden(self):
        try:            
            template = get_template('403.html')
            html = template.render(Context({}))
        except TemplateDoesNotExist:
            html = '<h1>Forbidden</h1>'
        return http.HttpResponseForbidden(html)