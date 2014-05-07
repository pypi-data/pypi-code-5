import django
from django.conf import settings

from django_deploy.models import deploy_tasks, Task


default_tasks = []

if django.VERSION[1] < 7:
    default_tasks.append(Task('syncdb', interactive=False))

if 'south' in settings.INSTALLED_APPS or django.VERSION[1] >= 7:
    default_tasks.append(Task('migrate'))

if 'staticfiles' in settings.INSTALLED_APPS and settings.STATIC_ROOT:
    default_tasks.append(Task('collectstatic', interactive=False))

if settings.USE_I18N:
    default_tasks.append(Task('compilemessages'))

tasks = deploy_tasks(*default_tasks)
