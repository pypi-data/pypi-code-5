import redis
import redis_collections

from default_storage_object import BaseStorageObject


def redis_subparser(parser):
    parser.add_argument(
        "-redis_host",
        default="localhost"
    )
    parser.add_argument(
        "-redis_port",
        type=int,
        default=6379
    )
    parser.add_argument(
        "-redis_key",
        help="A key prefix.",
        default="my_app"
    )
    return parser


class RedisStorageObject(BaseStorageObject):

    def __init__(self, *args, **kwargs):
        host = kwargs.get("host")
        port = kwargs.get("port")
        key = kwargs.get("key")
        self.storage = redis_collections.Dict(key=key, redis=redis.Redis(host=host, port=port))

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
