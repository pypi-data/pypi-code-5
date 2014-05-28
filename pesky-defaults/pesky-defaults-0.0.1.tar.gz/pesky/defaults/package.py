# Copyright 2010-2014 Michael Frank <msfrank@syntaxjockey.com>
#
# This file is part of Pesky.  Pesky is BSD-licensed software;
# for copyright information see the LICENSE file.

import pkg_resources, json

def package_defaults(project):
    req = pkg_resources.Requirement.parse(project)
    provider = pkg_resources.get_provider(req)
    if provider.has_metadata('pesky_defaults.json'):
        return json.loads(provider.get_metadata('pesky_defaults.json'))
    return dict()
