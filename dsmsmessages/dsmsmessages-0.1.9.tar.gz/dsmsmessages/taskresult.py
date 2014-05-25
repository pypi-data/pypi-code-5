# -*- coding: utf-8 -*-

import logging
import colander

from datetime import datetime
from .fields import MsgFields as F
from .exceptions import ValidationError
import schemas


SEED_VERSION = "9.9.9"


def iso_now():
    return datetime.utcnow().isoformat()


class TaskResult(dict):
    """
    TaskResult represents a Task result for a single Target Monitoring Object
    (TMO). It's designed to be used inside task functions like this:

    tr = TaskResult("mytask", "2.2.5", 1111)
    tr.add("analysis", [1, 2, 3])
    tr.finish()

    This also adds a variety of metadata, like task run times and errors.
    """

    reserved_keys = [F.META]

    def __init__(self, task_name, task_version, tmoid, data=None,
                 schema=None):
        # str name of the task's output.
        # Not used internally, but referenced when adding to TaskResults.
        self.task_name = task_name
        # Supplied by task.
        self.task_version = task_version
        # int with the id of the target monitor object
        # Not used internally, but referenced when adding to TaskResults.
        self.tmoid = tmoid
        # Should be class of type colander.Schema.
        # Chiefly for testing - by default, will look for corresponding
        # schema to task_name
        self.schema = self._set_schema(schema)

        if not self.task_name:
            raise ValueError("Must define a task type")
        if (not self.task_version or
                not isinstance(self.task_version, basestring)):
            raise ValueError("Must define a task version as a string "
                             "(e.g. '1.2.2.'")
        elif not self.tmoid or not isinstance(self.tmoid, int):
            raise ValueError("Target monitoring id (tmoid) must be an int")

        # start the timer
        self.time_start = iso_now()
        self.time_end = None

        dict.__init__(self)

        if data and not isinstance(data, dict):
            raise ValueError("data must be a dictionary to import")
        elif data:
            self.update(data)

    @classmethod
    def init_from_dict(cls, task, tmoid, data, schema=None):
        """
        Load a TaskResult from a dict, likely a deserialized TaskResult from
        somewhere else. Note that task_version is contained in the meta data
        already, so we don't pass it in.
        """
        # str name of the task's output
        task_version = None
        # int with the id of the target monitor object

        try:
            task_version = data[F.META][F.META_VERSION]
        except KeyError:
            raise ValueError("TaskResult dict does not define a version "
                             "number")
        return cls(task, task_version, tmoid, data, schema=schema)

    def _set_schema(self, supplied_schema):
        schema_cls = None

        if not self.task_name:
            raise ValueError("Must specify a task_name")

        print ("Supplied schema: %s" % supplied_schema)
        if not supplied_schema:
            print "No schema supplied, going auto"
            schema_name = "{0}Schema".format(self.task_name.title())
            try:
                schema_cls = getattr(schemas, schema_name)
            except AttributeError:
                raise ValueError("Couldn't find validation schema called {0}"
                                   .format(schema_name))
        else:
            schema_cls = supplied_schema
        print (schema_cls)
        if schemas._BaseTaskSchema not in schema_cls.__bases__:
            raise ValueError("schema must be of type colander.Schema")

        return schema_cls

    def add(self, result_name, result_val):
        """
        Add a named result to the TaskResult.
        """
        if result_name in self.reserved_keys:
            raise ValueError("{0} is a reserved key name - please choose"
                             " another.".format(result_name))

        if not result_name:
            raise ValueError("key must be a defined value")

        self.setdefault(result_name, result_val)

    def get_data_strict(self, key):
        """
        Find and return a data key, raise ValueError if not found
        """
        try:
            return self[key]
        except KeyError:
            logging.debug(self)
            raise ValueError("{0}.{1} has no value for {2}".format(
                self.task_name, self.tmoid, key))

    def get_data(self, key):
        """
        Find and return a data key, return None if not found
        """
        return self.get(key, None)

    def get_meta(self, key):
        """
        Return a meta field from this Task
        """
        return self[F.META].get(key)

    @property
    def success(self):
        """
        Return true if the task returned with no errors
        """
        return self.err is None

    @property
    def err(self):
        """
        Return errors returned by a task
        """
        try:
            return self[F.META][F.META_ERR]
        except KeyError:
            return

    @property
    def version(self):
        """
        Return errors returned by a task
        """
        try:
            return self[F.META][F.META_VERSION]
        except KeyError:
            return

    def finish(self, err=None, msg=None):
        """
        Add the result for the event, any error messages, and stop the timer
        """
        self.time_end = iso_now()

        self.setdefault(F.META, {})
        self[F.META][F.META_ERR] = err
        self[F.META][F.META_MSG] = msg
        self[F.META][F.META_START_TIME] = self.time_start
        self[F.META][F.META_END_TIME] = self.time_end
        self[F.META][F.META_VERSION] = self.task_version

        self.schema_validate()

    def schema_validate(self):
        try:
            self.schema().deserialize(self)
        except colander.Invalid as e:
            raise ValidationError(
                "Couldn't validate schema: {0}".format(e))


class TaskSeed(TaskResult):
    def __init__(self, task, tmoid, key, val):
        super(TaskSeed, self).__init__(task, SEED_VERSION, tmoid)
        self.add(key, val)
        self.finish()
