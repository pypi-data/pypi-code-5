"""Client interface to Urban airship service."""
import logging

import urbanairship

from zope.interface import implementer, Interface

log = logging.getLogger(__name__)


def includeme(config):
    """Include :py:mod:`pyramid_blazon` into a Pyramid configurator. This will
    register a client utility and make it available on request.

    To activate, call the configurator method:

    .. code-block:: python

       config.include('pyramid_urbanairship')

    """
    registry = config.registry
    settings = config.registry.settings

    try:
        application_key = settings['urbanairship.application_key']
        application_secret = settings['urbanairship.application_secret']
    except KeyError as exc:
        log.error('Missing configuration entry for %s', exc.args[0])
        raise

    utility = UrbanAirship(application_key, application_secret)

    config.add_request_method(
        get_urbanairship_utility,
        'urbanairship',
        reify=True,
        )

    registry.registerUtility(utility)


def get_urbanairship_utility(request):
    """Fetch the Urban airship client utility from the Pyramid registry."""
    registry = request.registry
    return registry.getUtility(IUrbanAirship)


class IUrbanAirship(Interface):
    """An interface representing a client to the Blazon service."""


@implementer(IUrbanAirship)
class UrbanAirship(urbanairship.Airship):
    """The client interface to the Urban airship service."""

    def __init__(self, application_key, application_secret):
        super(UrbanAirship, self).__init__(application_key, application_secret)
