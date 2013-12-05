"""Print the metadata for one or more Python package distributions.

Usage:  %prog [options] path+

Each 'path' entry can be one of the following:

o a source distribution:  in this case, 'path' should point to an existing
  archive file (.tar.gz, .tar.bz2, or .zip) as generated by 'setup.py sdist'.

o a binary distribution:  in this case, 'path' should point to an existing
  archive file (.egg)

o a "develop" checkout:  in ths case,  'path' should point to a directory
  intialized via 'setup.py develop' (under setuptools).

o an installed package:  in this case, 'path' should be the importable name
  of the package.
"""
from ConfigParser import ConfigParser
from csv import writer
import optparse
import os
import sys

from pkginfo import get_metadata


def _parse_options():
    parser = optparse.OptionParser(usage=__doc__)

    parser.add_option("-m", "--metadata-version", default=None,
                      help="Override metadata version")

    parser.add_option("-f", "--field", dest="fields", action="append",
                      help="Specify an output field (repeatable)",
                      )

    parser.add_option("-d", "--download-url-prefix",
                      dest="download_url_prefix", 
                      help="Download URL prefix",
                      )

    parser.add_option("--simple", dest="output", action="store_const",
                      const='simple', default='simple',
                      help="Output as simple key-value pairs",
                      )

    parser.add_option("-s", "--skip", dest="skip", action="store_true",
                      default=True,
                      help="Skip missing values in simple output",
                     )

    parser.add_option("-S", "--no-skip", dest="skip", action="store_false",
                      help="Don't skip missing values in simple output",
                     )

    parser.add_option("--single", dest="output", action="store_const",
                      const='single',
                      help="Output delimited values",
                      )

    parser.add_option("--item-delim", dest="item_delim", action="store",
                      default=';',
                      help="Delimiter for fields in single-line output",
                      )

    parser.add_option("--sequence-delim", dest="sequence_delim",
                      action="store", default=',',
                      help="Delimiter for multi-valued fields",
                      )

    parser.add_option("--csv", dest="output", action="store_const",
                      const='csv',
                      help="Output as CSV",
                      )

    parser.add_option("--ini", dest="output", action="store_const",
                      const='ini',
                      help="Output as INI",
                      )

    options, args = parser.parse_args()

    if len(args)==0:
        parser.error("Pass one or more files or directories as arguments.")
    else:
        return options, args

class Base(object):
    _fields = None
    def __init__(self, options):
        if options.fields:
            self._fields = options.fields

    def finish(self):
        pass

class Simple(Base):
    def __init__(self, options):
        super(Simple, self).__init__(options)
        self._skip = options.skip

    def __call__(self, meta):
        for field in self._fields or list(meta):
            value = getattr(meta, field)
            if (not self._skip) or (value is not None and value!=()):
                print("%s: %s" % (field, value))

class SingleLine(Base):
    _fields = None
    def __init__(self, options):
        super(SingleLine, self).__init__(options)
        self._item_delim = options.item_delim
        self._sequence_delim = options.sequence_delim

    def __call__(self, meta):
        if self._fields is None:
            self._fields = list(meta)
        values = []
        for field in self._fields:
            value = getattr(meta, field)
            if isinstance(value, (tuple, list)):
                value = self._sequence_delim.join(value)
            else:
                value = str(value)
            values.append(value)
        print(self._item_delim.join(values))

class CSV(Base):
    _wrote_headers = False
    def __init__(self, options):
        super(CSV, self).__init__(options)
        self._writer = writer(sys.stdout)
        self._sequence_delim = options.sequence_delim

    def __call__(self, meta):
        if self._fields is None:
            self._fields = list(meta) # first dist wins
        fields = self._fields
        if not self._wrote_headers: # latch
            self._writer.writerow(fields)
            self._wrote_headers = True
        values = []
        for field in fields:
            value = getattr(meta, field)
            if isinstance(value, (tuple, list)):
                value = self._sequence_delim.join(value)
            else:
                value = str(value)
            values.append(value)
        self._writer.writerow(values)

class INI(Base):
    _fields = None
    def __init__(self, options):
        super(INI, self).__init__(options)
        self._parser = ConfigParser()

    def __call__(self, meta):
        name = meta.name
        version = meta.version
        section = '%s-%s' % (name, version)
        if self._parser.has_section(section):
            raise ValueError('Duplicate distribution: %s' % section)
        self._parser.add_section(section)
        for field in self._fields or list(meta):
            value = getattr(meta, field)
            if isinstance(value, (tuple, list)):
                value = '\n\t'.join(value)
            self._parser.set(section, field, value)

    def finish(self):
        self._parser.write(sys.stdout)

_FORMATTERS = {
    'simple': Simple,
    'single': SingleLine,
    'csv': CSV,
    'ini': INI,
}

def main():
    """Entry point for pkginfo tool
    """
    options, paths = _parse_options()
    format = getattr(options, 'output', 'simple')
    formatter = _FORMATTERS[format](options)

    for path in paths:
        meta = get_metadata(path, options.metadata_version)
        if meta is None:
            continue

        if options.download_url_prefix:
            if meta.download_url is None:
                filename = os.path.basename(path)
                meta.download_url = '%s/%s' % (options.download_url_prefix,
                                               filename)

        formatter(meta)

    formatter.finish()
