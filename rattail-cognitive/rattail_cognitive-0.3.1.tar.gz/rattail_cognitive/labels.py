#!/usr/bin/env python
# -*- coding: utf-8  -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2012 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

"""
Label Printing
"""

from cStringIO import StringIO

import edbob

from rattail import labels


class BlasterFilePrinter(labels.CommandFilePrinter):
    """
    Label printer class for Cognitive Blaster devices, which generates an
    output file containing native printer commands.
    """

    def batch_header_commands(self):
        return ['C' * 80] # wakeup


class BlasterFormatter(labels.CommandFormatter):
    """
    Default label formatter class for Cognitive Blaster devices.
    """

    def label_header_commands(self):
        return [
            '! 0 30 120 1',
            'WIDTH 233',
            ]

    def label_footer_commands(self):
        noindex = edbob.config.getboolean(
            'rattail.hw.cognitive', 'blaster.hack_noindex', default=False)
        if noindex:
            return [
                'NOINDEX',
                'END',
                '! 0 100 8 1',
                'END',
                ]
        return [
            'INDEX',
            'END',
            ]


class BlasterTwoUpFormatter(labels.TwoUpCommandFormatter, BlasterFormatter):
    """
    Default implementation of "two-up" formatter for Blaster label printing.
    """

    half_offset = 120

    def label_body_commands(self, product, x=0):
        description = '%s %s' % (product.description, product.size)
        return [
            'STRING 5X7(1,1,1,1) %u 5 %s' % (x + 5, description[:17]),
            'STRING 5X7(1,1,1,1) %u 15 %s' % (x + 5, description[17:]),
            'BARCODE UPCA+ %u 75 25 %011u' % (x + 9, product.upc),
            ]
