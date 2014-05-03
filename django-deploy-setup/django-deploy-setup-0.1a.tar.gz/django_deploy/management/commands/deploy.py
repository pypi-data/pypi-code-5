from django.conf import settings
from django.core.management.base import NoArgsCommand
from django.utils import importlib


class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        tasks_module = getattr(
            settings, 'DEPLOY_TASKS', 'django_deploy.deploy')

        deploy = importlib.import_module(tasks_module)

        for task in deploy.tasks:
            task.run()
