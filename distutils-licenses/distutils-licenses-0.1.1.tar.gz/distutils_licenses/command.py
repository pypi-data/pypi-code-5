from __future__ import print_function

from collections import defaultdict
from setuptools import Command


class LicenseCommand(Command):
    """Print the licenses for each package in the working set.

    """

    description = 'print the licenses for each package in the working set.'
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        import pkg_resources

        for pkg in pkg_resources.working_set:
            try:
                lines = pkg.get_metadata_lines('PKG-INFO')
            except:
                try:
                    lines = pkg.get_metadata_lines('METADATA')
                except:
                    lines = []

            metadata = defaultdict(lambda: [])

            for line in lines:
                if ': ' not in line:
                    continue

                k, v = line.split(': ', 1)
                metadata[k].append(v)

            name = "%s %s" % (pkg.project_name, pkg.version)
            licenses = ' / '.join(metadata.get('License', ['n/a']))
            print("%-40s %s" % (name, licenses))
