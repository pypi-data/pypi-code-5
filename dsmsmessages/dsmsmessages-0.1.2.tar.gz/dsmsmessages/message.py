# -*- coding: utf-8 -*-

class Message(dict):
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)

    def set_task_obj(self, task, obj_id, key, val):
        if not task:
            raise ValueError("task must be a defined value")
        elif not obj_id:
            raise ValueError("obj_id must be a defined value")
        elif not key:
            raise ValueError("key must be a defined value")

        try:
            self.setdefault(task, {}).setdefault(obj_id, {})[key] = val
        except:
            raise

    def get_task_obj(self, task, tmo_id):
        try:
            self[task]
        except KeyError:
            raise ValueError("%s task not found in message" % task)

        try:
            return self[task][tmo_id]
        except KeyError:
            raise ValueError("%s obj ID not found in this message" % tmo_id)
