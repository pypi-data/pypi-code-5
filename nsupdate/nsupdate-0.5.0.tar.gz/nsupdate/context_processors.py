# -*- coding: utf-8 -*-

import logging
logger = logging.getLogger(__name__)

import time

from .main.dnstools import put_ip_into_session

from django.conf import settings

MAX_IP_AGE = 180  # seconds


def add_settings(request):
    context = {}
    context['WWW_HOST'] = settings.WWW_HOST
    context['WWW_IPV4_HOST'] = settings.WWW_IPV4_HOST
    context['WWW_IPV6_HOST'] = settings.WWW_IPV6_HOST
    context['SERVICE_CONTACT'] = settings.SERVICE_CONTACT  # about view
    context['WE_HAVE_SSL'] = settings.WE_HAVE_SSL
    context['COOKIE_SECURE'] = settings.SESSION_COOKIE_SECURE or settings.CSRF_COOKIE_SECURE
    return context


def update_ips(request):
    """
    Update the IPs in the session using REMOTE_ADDR.
    Check the session if there are stale IPs and if so, remove them.
    """
    # XXX is a context processor is the right place for this?
    s = request.session
    t_now = int(time.time())
    # update and keep fresh using info from the request we have anyway:
    ipaddr = request.META['REMOTE_ADDR']
    put_ip_into_session(s, ipaddr, max_age=MAX_IP_AGE / 2)
    # remove stale data to not show outdated IPs (e.g. after losing IPv6 connectivity):
    for key in ['ipv4', 'ipv6', ]:
        timestamp_key = "%s_timestamp" % key
        try:
            timestamp = s[timestamp_key]
        except KeyError:
            # should be always there, initialize it:
            put_ip_into_session(s, '', kind=key)
        else:
            try:
                stale = timestamp + MAX_IP_AGE < t_now
            except (ValueError, TypeError):
                # invalid timestamp in session
                put_ip_into_session(s, '', kind=key)
            else:
                if stale:
                    logger.debug("ts: %s now: %s - killing stale %s (was: %s)" % (timestamp, t_now, key, s[key]))
                    # kill the IP, it is not up-to-date any more
                    # note: it is used to fill form fields, so set it to empty string
                    put_ip_into_session(s, '', kind=key)
    if s.session_key is None:
        # if we have a new session (== not loaded from database / storage), we
        # MUST save it here to create its session_key as the base.html template
        # uses .session_key to build the URL for detectip:
        s.save()
    return {}
