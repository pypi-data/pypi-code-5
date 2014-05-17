
# -*- encoding: utf-8 -*-
# Copyright (c) 2014 - Dedsert Ltd.

"""
.. module:: DoBy
    :plarform: Unix, Windows, OSX
    :synopsis: DoBy module can be used to raise exceptions if
        TODOs are not done by a certain time.

.. modelauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from datetime import datetime
from dateutil import parser


class DoBy(Exception):
    """The main DoBy Exception handler class"""

    def __init__(self, note, do_by_date):
        super(DoBy, self).__init__('TODO: ' + note)

        if type(do_by_date) is not datetime:
            do_by_date = parser.parse(do_by_date).replace(tzinfo=None)

        if do_by_date < datetime.now():
            raise self


def TODO(note, do_by):
    """ Call me to raise an exception if a TODOs
        is not done by a certain time
    """
    DoBy(note, do_by)
