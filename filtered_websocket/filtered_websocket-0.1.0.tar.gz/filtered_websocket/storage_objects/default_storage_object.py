import collections


class BaseStorageObject(object):
    storage = None

    def __getitem__(self, item):
        raise NotImplementedError

    def add(self, key, value):
        raise NotImplementedError

    def remove(self, key, value):
        raise NotImplementedError


class BasePubSubStorageObject(BaseStorageObject):
    """
    Defines standard interfaces for storage objects, like redis,
    which support pubsub.
    """

    def publish(self, channel, data):
        raise NotImplementedError


class DefaultStorageObject(BaseStorageObject):

    def __init__(self, *args, **kwargs):
        self.storage = collections.defaultdict(set)

    def __getitem__(self, item):
        return self.storage.get(item)

    def add(self, key, value):
        self.storage[key].add(value)

    def remove(self, key, value):
        self.storage[key].remove(value)
