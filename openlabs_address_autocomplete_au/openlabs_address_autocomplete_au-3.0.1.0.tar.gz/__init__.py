# -*- coding: utf-8 -*-
"""
    __init__.py

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.pool import Pool

from party import Address
from configuration import Configuration


def register():
    Pool.register(
        Address,
        Configuration,
        module='address_autocomplete_au', type_='model'
    )
