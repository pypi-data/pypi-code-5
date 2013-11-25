# -*- coding: utf-8 -*-

from django.core.cache import get_cache
from django.utils.functional import cached_property
from jinja2 import BytecodeCache as _BytecodeCache


class BytecodeCache(_BytecodeCache):
    """
    A bytecode cache for Jinja2 that uses Django's caching framework.
    """

    def __init__(self, cache_name):
        self._cache_name = cache_name

    @cached_property
    def backend(self):
        return get_cache(self._cache_name)

    def load_bytecode(self, bucket):
        key = 'jinja2_%s' % str(bucket.key)
        bytecode = self.backend.get(key)
        if bytecode:
            bucket.bytecode_from_string(bytecode)

    def dump_bytecode(self, bucket):
        key = 'jinja2_%s' % str(bucket.key)
        self.backend.set(key, bucket.bytecode_to_string())
