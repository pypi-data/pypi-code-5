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

        # Always remove check digit from UPC.
        upc = unicode(product.upc)[:-1]
        if len(upc) != 13:
            raise ValueError(u"UPC format is unexpected: {0}".format(repr(product.upc)))

        # Create barcode command based on type of UPC.
        if upc.startswith(u'00'): # UPC-A
            barcode_type = u'UPCA+'
            barcode = upc[2:]
        elif upc.startswith(u'0'): # EAN-13
            barcode_type = u'EAN13+'
            barcode = upc[1:]
        else:
            raise ValueError(u"UPC format is invalid: {0}".format(repr(product.upc)))

        description = u'{0} {1}'.format(product.description, product.size)
        return [
            u'STRING 5X7(1,1,1,1) {0} 5 {1}'.format(x + 5, description[:17]),
            u'STRING 5X7(1,1,1,1) {0} 15 {1}'.format(x + 5, description[17:]),
            u'BARCODE {0} {1} 75 25 {2}'.format(barcode_type, x + 9, barcode),
            ]
