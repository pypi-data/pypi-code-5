import os
import sys
f = __file__
p = os.path.abspath(f)
d = os.path.dirname(p)
base, module = os.path.split(d)
sys.path.insert(0, base)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "%s.settings" % module)
from django.core.wsgi import get_wsgi_application
application=get_wsgi_application()
