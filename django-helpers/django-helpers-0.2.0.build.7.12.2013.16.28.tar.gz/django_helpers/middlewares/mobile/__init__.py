# coding=utf-8
"""

Copied from

http://code.google.com/p/minidetector/
All credits to original author.

"""
from django_helpers import get_settings_val
from django_helpers.helpers.views import redirect

from useragents import search_strings


class Middleware(object):
    def process_request(self, request):
        """Adds a "mobile" attribute to the request which is True or False
           depending on whether the request should be considered to come from a
           small-screen device such as a phone or a PDA"""

        MOBILE_URL = get_settings_val('REDIRECT_MOBILE', None)

        if request.META.has_key("HTTP_X_OPERAMINI_FEATURES"):
            #Then it's running opera mini. 'Nuff said.
            #Reference from:
            # http://dev.opera.com/articles/view/opera-mini-request-headers/
            request.mobile = True
            return None

        if request.META.has_key("HTTP_ACCEPT"):
            s = request.META["HTTP_ACCEPT"].lower()
            if 'application/vnd.wap.xhtml+xml' in s:
                if MOBILE_URL is None:
                    # Then it's a wap browser
                    request.mobile = True
                    return None
                else:
                    return redirect(MOBILE_URL)

        if request.META.has_key("HTTP_USER_AGENT"):
            # This takes the most processing. Surprisingly enough, when I
            # Experimented on my own machine, this was the most efficient
            # algorithm. Certainly more so than regexes.
            # Also, Caching didn't help much, with real-world caches.
            s = request.META["HTTP_USER_AGENT"].lower()
            for ua in search_strings:
                if ua in s:
                    if MOBILE_URL is None:
                        request.mobile = True
                        return None
                    else:
                        return redirect(MOBILE_URL)

        #Otherwise it's not a mobile
        request.mobile = False
        return None


def detect_mobile(view):
    """View Decorator that adds a "mobile" attribute to the request which is
       True or False depending on whether the request should be considered
       to come from a small-screen device such as a phone or a PDA"""

    def detected(request, *args, **kwargs):
        obj = Middleware()
        obj.process_request(request)
        return view(request, *args, **kwargs)

    detected.__doc__ = "%s\n[Wrapped by detect_mobile which detects if the request is from a phone]" % view.__doc__
    return detected


__all__ = ['Middleware', 'detect_mobile']