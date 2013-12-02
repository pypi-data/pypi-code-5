import math
from hashlib import md5
from itertools import cycle

from numpy import random


class Iterator(object):

    def __init__(self):
        self.prefix = None

    def __iter__(self):
        return self

    def add_prefix(self, key):
        if self.prefix:
            return '{}-{}'.format(self.prefix, key)
        else:
            return key


class ExistingKey(Iterator):

    def __init__(self, working_set, working_set_access, prefix):
        self.working_set = working_set
        self.working_set_access = working_set_access
        self.prefix = prefix

    def next(self, curr_items, curr_deletes):
        num_existing_items = curr_items - curr_deletes
        num_hot_items = int(num_existing_items * self.working_set / 100.0)
        num_cold_items = num_existing_items - num_hot_items

        left_limit = 1 + curr_deletes
        if random.random_integers(0, 100) <= self.working_set_access:
            left_limit += num_cold_items
            right_limit = curr_items
        else:
            right_limit = left_limit + num_cold_items
        key = 'key-{}'.format(random.random_integers(left_limit, right_limit))
        return self.add_prefix(key)


class SequentialHotKey(Iterator):

    def __init__(self, sid, ws, prefix):
        self.sid = sid
        self.ws = ws
        self.prefix = prefix

    def __iter__(self):
        num_hot_keys = int(self.ws.items * self.ws.working_set / 100.0)
        num_cold_items = self.ws.items - num_hot_keys
        keys_per_worker = num_hot_keys / self.ws.workers
        left_limit = 1 + num_cold_items + self.sid * keys_per_worker
        right_limit = left_limit + keys_per_worker

        for seq_id in range(left_limit, right_limit):
            key = 'key-{}'.format(seq_id)
            key = self.add_prefix(key)
            yield key


class NewKey(Iterator):

    def __init__(self, prefix, expiration):
        self.prefix = prefix
        self.expiration = expiration
        self.ttls = cycle(range(150, 450, 30))

    def next(self, curr_items):
        key = 'key-{}'.format(curr_items)
        key = self.add_prefix(key)
        ttl = None
        if self.expiration and random.random_integers(1, 100) <= self.expiration:
            ttl = self.ttls.next()
        return key, ttl


class KeyForRemoval(Iterator):

    def __init__(self, prefix):
        self.prefix = prefix

    def next(self, curr_deletes):
        key = 'key-{}'.format(curr_deletes)
        return self.add_prefix(key)


class NewDocument(Iterator):

    SIZE_VARIATION = 0.25  # 25%
    KEY_LENGTH = 10

    def __init__(self, avg_size):
        self.avg_size = avg_size

    @classmethod
    def _get_variation_coeff(cls):
        return random.uniform(1 - cls.SIZE_VARIATION, 1 + cls.SIZE_VARIATION)

    @staticmethod
    def _build_alphabet(key):
        return md5(key).hexdigest() + md5(key[::-1]).hexdigest()

    @staticmethod
    def _build_name(alphabet):
        return '{} {}'.format(alphabet[:6], alphabet[6:12])

    @staticmethod
    def _build_email(alphabet):
        return '{}@{}.com'.format(alphabet[12:18], alphabet[18:24])

    @staticmethod
    def _build_city(alphabet):
        return alphabet[24:30]

    @staticmethod
    def _build_realm(alphabet):
        return alphabet[30:36]

    @staticmethod
    def _build_coins(alphabet):
        return max(0.1, int(alphabet[36:40], 16) / 100.0)

    @staticmethod
    def _build_category(alphabet):
        return int(alphabet[41], 16) % 3

    @staticmethod
    def _build_achievements(alphabet):
        achievement = 256
        achievements = []
        for i, char in enumerate(alphabet[42:58]):
            achievement = (achievement + int(char, 16) * i) % 512
            if achievement < 256:
                achievements.append(achievement)
        return achievements

    @staticmethod
    def _build_body(alphabet, length):
        length_int = int(length)
        num_slices = int(math.ceil(length / len(alphabet)))
        body = num_slices * alphabet
        return body[:length_int]

    def next(self, key):
        next_length = self._get_variation_coeff() * self.avg_size
        alphabet = self._build_alphabet(key)
        doc = {
            'name': self._build_name(alphabet),
            'email': self._build_email(alphabet),
            'city': self._build_city(alphabet),
            'realm': self._build_realm(alphabet),
            'coins': self._build_coins(alphabet),
            'category': self._build_category(alphabet),
            'achievements': self._build_achievements(alphabet),
            'body': self._build_body(alphabet, next_length)
        }
        return doc
