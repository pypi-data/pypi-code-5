from django.views.generic.base import View
from django.shortcuts import render
from django.http import HttpResponseNotFound
from django.template.base import TemplateDoesNotExist
import os.path
import re


def clean_path(path):
    """ to prevent path traversal exploits, we whitelist
    allowed paths to only include alphanumeric chars,
    hyphens, and forward slashes. then we disallow
    forward slashes from the beginning or the end of the
    path """
    path = re.sub(r'[^\w\-\/]+', '', path)
    # no '/'s on either end
    path = path.strip('/')
    return path


class InfranilView(View):
    base_dir = "infranil"

    def get(self, request, path):
        path = clean_path(path)
        tpath = os.path.join(self.base_dir, path)

        try:
            return render(request, tpath + ".html", dict())
        except TemplateDoesNotExist:
            pass

        try:
            return render(request, tpath + "/index.html", dict())
        except TemplateDoesNotExist:
            return HttpResponseNotFound()
