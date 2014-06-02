from django.conf import settings

WKHTMLTOPDF_CMD = getattr(settings, 'WKHTMLTOPDF_CMD', 'wkhtmltopdf')
