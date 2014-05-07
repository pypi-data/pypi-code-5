from django.core.management import call_command


class Task(object):
    def __init__(self, command=None, custom_callable=None, *args, **kwargs):
        if not command and not custom_callable:
            raise ValueError('Either command or custom_callable must be set.')

        if command:
            custom_callable = call_command

        self.callable = custom_callable
        self.command = command
        self.args = args
        self.kwargs = kwargs

    def run(self):
        if self.command:
            self.callable(self.command, *self.args, **self.kwargs)
        else:
            self.callable(*self.args, **self.kwargs)


def deploy_tasks(*tasks):
    task_objects = []
    for task in tasks:
        if not isinstance(task, Task):
            task = Task(*task)
        task_objects.append(task)

    return task_objects
