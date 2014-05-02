# -*- extra stuff goes here -*-

import logging

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('collective.externalizelink')
logger = logging.getLogger('collective.externalizelink')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
