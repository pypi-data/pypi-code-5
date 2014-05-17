
# -*- encoding: utf-8 -*-
# Copyright (c) 2014.

"""
.. module:: DoBy
    :plarform: Unix, Windows, OSX
    :synopsis: DoBy module can be used to raise exceptions if
        TODOs are not done by a certain time.

.. modelauthor:: Adam Drakeford <adamdrakeford@gmail.com>
"""

from dateutil import parser
from datetime import datetime


class DoBy(Exception):
    """The main DoBy Exception handler class"""

    def __init__(self, note, doby_date):
        super(DoBy, self).__init__('TODO: ' + note)

        if type(doby_date) is not datetime:
            doby_date = parser.parse(doby_date).replace(tzinfo=None)

        if doby_date < datetime.now():
            raise self


def TODO(note, doby):
    """ Call me to raise an exception if a TODOs
        is not done by a certain time.
        :param note: a str for the TODO note.
        :param doby: a str or datetime object for the date
            in which the TODO is to be done by.
    """
    DoBy(note, doby)
