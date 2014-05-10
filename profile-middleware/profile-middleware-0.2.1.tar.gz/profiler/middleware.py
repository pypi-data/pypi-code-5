__author__ = 'vaibhav'

import sys
import os
import re
import hotshot, hotshot.stats
import tempfile
import StringIO
from django.template.loader import render_to_string

from django.conf import settings


class ProfileMiddleware(object):

    def process_request(self, request):
        if (settings.DEBUG or request.user.is_superuser) and 'prof' in request.GET:
            self.tmpfile = tempfile.mktemp()
            self.profiler = hotshot.Profile(self.tmpfile)

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if (settings.DEBUG or request.user.is_superuser) and 'prof' in request.GET:
            return self.profiler.runcall(callback, request, *callback_args, **callback_kwargs)

    def process_response(self, request, response):

        if settings.DEBUG and 'prof' in request.GET:
            self.profiler.close()

            out = StringIO.StringIO()
            old_stdout = sys.stdout
            sys.stdout = out

            stats = hotshot.stats.load(self.tmpfile)
            stats.sort_stats('time', 'calls')
            stats.print_stats()

            sys.stdout = old_stdout
            stats_str = out.getvalue()
            profile_output = stats_str.split('\n')
            info = '\n'.join(profile_output[:4])
            table_header = [_ for _ in profile_output[4].split(' ') if _]
            table_rows = [_.split() for _ in profile_output[5:-4] if _]
            table_rows = [_[:5] + [' '.join(_[5:])] for _ in table_rows]

            ret_dict = dict(table_header=table_header,
                            table_rows=table_rows,
                            info=info)

            response.content = render_to_string('profiler/profiler.html', ret_dict)
        return response