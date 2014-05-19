# -*- coding: utf-8 -*-
"""
    Configuration

    :copyright: (c) 2014 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
from trytond.model import fields
from trytond.pool import PoolMeta


__all__ = ['Configuration']
__metaclass__ = PoolMeta


class Configuration:
    "Configuration"
    __name__ = "party.configuration"

    auspost_api_key = fields.Char('Australia Postcode Api Key')
