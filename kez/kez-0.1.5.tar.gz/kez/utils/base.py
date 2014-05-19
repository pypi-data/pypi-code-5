
from datetime import datetime
try:
    from urlparse import urlparse
except ImportError:
    from urllib.parse import urlparse

try:
    from configparser import ConfigParser as BaseParser, NoOptionError
except ImportError:
    from ConfigParser import ConfigParser as BaseParser, NoOptionError
    from ast import literal_eval

from slugify import slugify
from watdarepo import watdarepo
from giturlparse import parse as giturlparse

from kez.exceptions import URLFormatError


__all__ = [
    'import_object',
    'String',
    'slugify',
    'slugify_vcs_url',
    'parse_vcs_url',
    'evaluate_config_options',
    'ConfigParser',
    'NoOptionError',
]

def import_object(name):
    """Imports an object by name.

    import_object('x.y.z') is equivalent to 'from x.y import z'.

    """
    name = str(name)
    if '.' not in name:
        return __import__(name)
    parts = name.split('.')
    m = '.'.join(parts[:-1])
    attr = parts[-1]
    obj = __import__(m, None, None, [attr], 0)
    try:
        return getattr(obj, attr)
    except AttributeError as e:
        raise ImportError("'%s' does not exist in module '%s'" % (attr, m))

class String(object):
    TIME_FORMAT = '%H:%M:%S.%f'
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%dT%H:%M:%S.%f'

    @staticmethod
    def parse_time(s):
        return datetime.strptime(s, TIME_FORMAT)

    @staticmethod
    def parse_date(s):
        return datetime.strptime(s, DATE_FORMAT)

    @staticmethod
    def parse_datetime(s):
        return datetime.strptime(s, DATETIME_FORMAT)

    @staticmethod
    def format_time(dt):
        return datetime.strftime(dt, TIME_FORMAT)

    @staticmethod
    def format_date(dt):
        return datetime.strftime(dt, DATE_FORMAT)

    @staticmethod
    def format_datetime(dt):
        return datetime.strftime(dt, DATETIME_FORMAT)

def slugify_vcs_url(url):
    path = urlparse(url).path
    scheme, at, path = path.partition('@')
    if not at:
        path = scheme
    return slugify(path)

def parse_vcs_url(url):
    wat = watdarepo(url)
    parts = {
        "vcs": wat["vcs"],
        "host": wat["hosting_service"],
        "url": url,
    }
    if wat["vcs"] == "git":
        parsed = giturlparse(url)
        if not parsed.valid:
            raise URLFormatError(url)
        parts["host"] = parsed.host
        parts["owner"] = parsed.owner
        parts["repo"] = parsed.repo
        parts["url"] = parsed.url2ssh
    parts["slug"] = slugify_vcs_url(parts["url"])
    while parts["host"] and "." in parts["host"]:
        parts["host"] = parts["host"].partition(".")[0]
    return parts

class Python2Parser(BaseParser):

    def _interpolate(self, section, option, rawval, vars):
        try:
            return literal_eval(rawval)
        except (ValueError, SyntaxError):
            return rawval

def ConfigParser():
    try:
        import configparser
    except ImportError:
        parser = Python2Parser()
    else:
        from .typedinterpolation import TypedBasicInterpolation
        parser = BaseParser(interpolation=TypedBasicInterpolation())
    # prevent configparser setting keys to lowercase
    parser.optionxform = str
    return parser

def evaluate_config_options(cfg, section):
    options = {}
    settings = {}
    dunder = '__'
    for k, v in cfg.items(section):
        if k:
            if k[:2] == dunder and k[-2:] == dunder:
                options[k[2:-2]] = v
            else:
                settings[k] = v
    return options, settings

