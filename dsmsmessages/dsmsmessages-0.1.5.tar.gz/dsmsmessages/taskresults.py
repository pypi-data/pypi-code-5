# -*- coding: utf-8 -*-

from .taskresult import TaskResult


class TaskResults(dict):
    """
    JobResult is a dict for storing TaskResults with convenience functions.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def add_task_result(self, task_result):
        if not task_result.task:
            raise ValueError("TaskResult must specify a task")
        if not task_result.tmoid:
            raise ValueError("TaskResult must specify a target monitoring "
                             "object id")

        self.setdefault(task_result.task, {})
        self[task_result.task][task_result.tmoid] = dict(task_result)

    def tasks(self):
        return self.iterkeys()

    def task_objs(self, task):
        try:
            self[task]
        except KeyError:
            raise ValueError("%s task not found in message" % task)

        return self[task].iterkeys()

    def get_task_result(self, task, tmoid):
        """
        Get a single TaskResult based on a task name and target monitoring
        ID.
        """
        try:
            self[task][tmoid]
        except KeyError:
            raise ValueError("Could not find task {0} with tmoid {1} in "
                             "results".format(task, tmoid))

        tr = TaskResult.init_from_dict(task, tmoid, self[task][tmoid])
        return tr
