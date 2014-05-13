"""
middlware to restrict IP addresses
"""

from django import http
from django.template.loader import get_template
from django.template import TemplateDoesNotExist, Context

from models import BlockedIp
from django.conf import settings
from django.core.exceptions import SuspiciousOperation


class BotTrapMiddleware(object):

    def get_ip(self, request):
        ip = request.META.get('REMOTE_ADDR', '')
        return ip

    def process_request(self, request):
        ip = self.get_ip(request)

        try:
            request.get_host()
        except SuspiciousOperation:
            BlockedIp.objects.get_or_create(ip=ip)
            self.forbidden()

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
