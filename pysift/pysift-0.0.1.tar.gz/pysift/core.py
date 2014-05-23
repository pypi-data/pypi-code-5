# -*- coding: utf-8 -*-

"""
pysift.core
~~~~~~~~~~~

This module provides the base entrypoint for pysift.
"""

from pysift.api import SiftScience


def from_key(api_key):
    return SiftScience(api_key)
