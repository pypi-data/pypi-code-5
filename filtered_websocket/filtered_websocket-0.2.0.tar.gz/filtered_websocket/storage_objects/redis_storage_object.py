from __future__ import absolute_import

import redis
import redis_collections

from .default_storage_object import BasePubSubStorageObject


def redis_parser(parser):
    parser.add_argument(
        "--redis",
        help="Use redis as a storage object.",
        action="store_true"
    )
    parser.add_argument(
        "--redis_host",
        default="localhost"
    )
    parser.add_argument(
        "--redis_port",
        type=int,
        default=6379
    )
    parser.add_argument(
        "--redis_channels",
        help="pubsub channels to subscribe to.",
        nargs="*"
    )
    parser.add_argument(
        "--redis_key",
        help="A key prefix.",
        default="my_app"
    )
    return parser


class RedisStorageObject(BasePubSubStorageObject):

    def __init__(self, *args, **kwargs):
        host = kwargs.get("host")
        port = kwargs.get("port")
        key = kwargs.get("key")
        self.redis = redis.Redis(host=host, port=port)
        self.storage = redis_collections.Dict(key=key, redis=self.redis)

    def __getitem__(self, item):
        return self.storage.get(item)

    def add(self, key, value):
        current = self.storage.get(key)
        if current is None:
            current = set()
        current.add(value)
        self.storage[key] = current

    def remove(self, key, item):
        current = self.storage.get(key)
        if current is not None:
            current.remove(item)
            self.storage[key] = current

    def publish(self, channel, data):
        self.redis.publish(channel, data)
