# deepdesk/data.py
# Copyright (C) 2014  Domino Marama
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import binascii
import isodate
import json
import os
import password
import re
import shutil
import socket
import tempfile
import time
import uuid
import requests

from contextlib import contextmanager
from datetime import datetime
from glob import glob
from Stemmer import Stemmer
from time import sleep

SYSTEM = 0
PUBLIC = 1
TRUSTED = 50
PRIVATE = 100

LOCK_RETRY = 500
LOCK_TIMEOUT = 0.05


def keysplit(key):
    """
    keysplit(key) -> (folder, id)
    """
    parts = key.split("/")
    return ("/".join(parts[:-1]), parts[-1])


def locationsplit(location):
    """
    locationsplit(location) -> (section, folder, id)
    """
    parts = key.split("/")
    return (parts[0], "/".join(parts[1:-1]), parts[-1])


def titlespace(s):
    """
    titlespace(str) -> str

    Adds spaces into TitleCase strings

    >>> titlespace("ThisWouldBeBetterWithSpaces")
    'This Would Be Better With Spaces'
    """
    return "".join([s[0]] + [
        " " + char if char.isupper() else char for char in s[1:]])


def validate(value, rule):
    """
    validate(value, rule) -> bool

    Returns true if the value object passes the rule or false if it fails.
    Each item in a tuple or list must pass the rule or validation will fail.

    Available rules are in the validators dict.

    >>> validate(23, "min 0|max 20")
    False
    >>> validate([0, 5, 12, 19], "min 0|max 20")
    True
    >>> validate("10.10.10.10", "ipv4")
    True
    >>> validate({"a":1,"b":2,"c":3}, "a|b")
    True
    """
    if isinstance(value, dict):
        # only validator for dict is to see if keys exist
        for r in rule.split("|"):
            if r not in value:
                return False
        return True
    elif isinstance(value, (list, tuple)):
        # all items must be valid
        for item in value:
            if not validate(item, rule):
                return False
        return True
    try:
        for r in rule.split("|"):
            # todo: improve re to allow escape quoted strings in rules
            #          none of current validators require this
            parts = re.findall(r'(?:(?<=["\']).*?(?=["\'])|\w+)', r)
            method = parts[0]
            args = [value]
            for n, i in enumerate(parts):
                if n:
                    cls = validators[value.__class__][method][n]
                    args.append(cls(i))
            if not validators[value.__class__][method][0](*args):
                return False
        return True
    except:
        return False


def isdate(value, format):
    # todo convert to isodate
    try:
        datetime.datetime.strptime(value, format)
        return True
    except ValueError:
        return False


def isemail(value):
    """
    isemail(value) -> bool

    Returns true if the value is an email address.

    >>> isemail("domino.marama@example.com")
    True
    >>> isemail("domino.marama@example")
    False
    """
    pattern = r'^[a-z0-9]+([._-][a-z0-9]+)*@([a-z0-9]+([._-][a-z0-9]+))+$'
    return re.match(pattern, value) is not None


def isipv4(value):
    """
    isipv4(value) -> bool

    Returns true if the value is an Internet Protocol Version 4 address.

    >>> isipv4("10.50.90.123")
    True
    >>> isipv4("10_50_90_123")
    False
    """
    try:
        socket.inet_pton(socket.AF_INET, value)
        return True
    except socket.error:
        return False


def isipv6(value):
    """
    isipv6(value) -> bool

    Returns true if the value is an Internet Protocol Version 6 address.

    >>> isipv6("c001:face:1015::")
    True
    >>> isipv6("ff0X::101")
    False
    """
    # todo? support multicast addresses eg ff0X::101
    try:
        socket.inet_pton(socket.AF_INET6, value)
        return True
    except socket.error:
        return False


def isurl(value):
    """
    isurl(value) -> bool

    Returns true if the value is a Uniform Resource Locator.

    >>> isurl("http://example.com")
    True
    >>> isurl("www.example.com")
    False
    """
    url_regex = re.compile(
        r'^(?:http|ftp)s?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url_regex.match(value) is not None

# each entry in validators is a class with a dict of rules
# each rule is a name with a tuple of the function and the class
# types for any arguments to the function

validators = {
    float: {
        'min': (float.__ge__, float),
        'max': (float.__le__, float),
        '>': (float.__gt__, float),
        '<': (float.__lt__, float)
        },
    int: {
        'min': (int.__ge__, int),
        'max': (int.__le__, int),
        '>': (int.__gt__, int),
        '<': (int.__lt__, int)
        },
    str: {
        'min': (lambda s, v: len(s) >= v, int),
        'max': (lambda s, v: len(s) <= v, int),
        'url': (isurl,),
        'ipv4': (isipv4,),
        'ipv6': (isipv6,),
        'email': (isemail,),
        'date': (isdate,)
        }
    }


class Field:
    def __init__(self, value):
        object.__setattr__(self, 'value', value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return "Field({})".format(repr(self.value))

    def __getattr__(self, name):
        if hasattr(self.__dict__['value'], name):
            return getattr(self.value, name)
        raise AttributeError

    def __setattr__(self, name, value):
        if name == 'value':
            if hasattr(self.value, name):
                return self.value.__setattr__(name, value)
        return object.__setattr__(self, name, value)

    def __getitem__(self, name):
        if isinstance(name, int):
            return self.value.values()[name]
        else:
            return self.value[name]

    def __setitem__(self, name, value):
        self.value[name] = value

    def jsonencode(self):
        if 'jsonencode' in dir(self.value):
            return self.value.jsonencode()
        else:
            return self.value


class Path:
    def __init__(self, root, location):
        self.location = location
        self.root = root
        if isinstance(self.root, str):
            self.path = os.path.join(self.root, *location.split('/'))
        else:
            self.path = self.root.join(*location.split('/'))

    def __str__(self):
        return str(self.path)

    def __repr__(self):
        return "Path({}, {})".format(repr(self.root), repr(self.location))

    @property
    def exists(self):
        return os.path.exists(self.path)

    @property
    def last_modified(self):
        if self.exists:
            return isodate.datetime_isoformat(
                datetime.fromtimestamp(os.path.getmtime(self.path)))
        else:
            return False

    def make(self):
        """
        This creates the path's directories if they do not already exists.
        """
        p = os.path.dirname(self.path)
        if not os.path.exists(p):
            os.makedirs(p)

    def lock(self):
        if hasattr(self, '_lock'):
            return
        lock = self.path + ".lock"
        self.make()
        repeats = LOCK_RETRY
        while repeats and os.path.exists(lock):
            sleep(LOCK_TIMEOUT)
            repeats -= 1
        if not repeats:
            raise TimeoutError
        open(lock, 'a')
        self._lock = lock

    def release(self):
        if hasattr(self, '_lock'):
            os.remove(self._lock)
            del(self._lock)

    @contextmanager
    def open(self, *args, **kwargs):
        self.lock()
        try:
            yield open(self.path, *args, **kwargs)
        finally:
            self.release()


class ListFile(Path):
    def load(self):
        """
        Returns a list of the values stored in location.
        """
        if self.exists:
            with self.open('r') as file:
                return [line.strip() for line in file]

    def walk(self):
        """Iterable values in location"""
        if self.exists:
            with self.open('r') as file:
                for line in file:
                    yield line.strip()

    def append(self, value):
        """
        Stores a unique value in location.
        """
        if value not in [None, "", [], {}, ()]:
            for line in self.walk():
                if line == str(value):
                    return
            with self.open("a") as file:
                file.write(str(value) + "\n")

    def extend(self, iterable):
        """
        Stores each unique value from the iterable in location.
        """
        for each in iterable:
            if hasattr(each, __iter__):
                self.extend(each)
            else:
                self.append(each)

    def remove(self, value):
        """
        Removes a unique value from location.
        """
        if value not in [None, "", [], {}, ()] and self.exists:
            with tempfile.NamedTemporaryFile(
                    prefix="deepdesk", delete=False) as new:
                newname = new.name
                for line in self.walk():
                    if line != value:
                        new.write(line.encode("utf-8"))
            if os.path.getsize(newname):
                shutil.copyfile(newname, self.path)
            else:
                os.remove(self.path)
            os.remove(newname)


class IndexFile(Path):
    """
    An IndexFile is a store of unique entry, value pairs.
    """
    def __init__(self, root, location):
        Path.__init__(self, root, "index/" + location)

    def lookup(self, entry, reverse=False):
        """
        lookup(entry, reverse) -> str

        >>> lookup(entry)
        value
        >>> lookup(value, True)
        entry
        """
        e = str(entry)
        folder = keysplit(self.location[6:])[0]
        if reverse:
            if e.startswith(folder):
                e = e[len(folder):]
        else:
            e = e.replace(" ", "_")
        for entry, value in self.walk():
            if reverse:
                if value == e:
                    return entry
            else:
                if entry == e:
                    if value[0] == "/":
                        value = folder + value
                    return value
        return None

    def walk(self):
        """Iterable key, entry pairs for index"""
        if self.exists:
            folder = keysplit(self.location[6:])[0]
            with self.open('r') as file:
                for line in file:
                    entry, value = line.split(" ", 1)
                    yield (entry, value.strip())

    def write(self, entry, value):
        """
        Store a unique entry, value pair.

        >>> indexwrite(
                        "domino.marama@example.com",
                        "person/domino.marama")
        """
        e = str(entry).replace(" ", "_")
        v = str(value)
        b = keysplit(self.location[6:])[0]
        if v.startswith(b):
            v = v[len(b):]
        if self.exists:
            self.delete(e)
        if value not in [None, "", [], {}, ()]:
            with self.open("a") as file:
                file.write("{} {}\n".format(e, v))

    def delete(self, entry):
        """
        Deletes any references to entry from filename.
        """
        if self.exists:
            with tempfile.NamedTemporaryFile(
                    prefix="deepdesk", delete=False) as new:
                newname = new.name
                for e, value in self.walk():
                    if e != entry:
                        new.write((e + " " + value + "\n").encode("utf-8"))
            if os.path.getsize(newname):
                shutil.copyfile(newname, self.path)
            else:
                os.remove(self.path)
            os.remove(newname)


class Record(Path):
    password = password.Password(keep_on_blank=True)

    @property
    def iscurrent(self):
        """Record on disk has not been updated since record loaded"""
        return self.last_saved == self.last_modified

    def __init__(self, root, key="record", indict=None, profile="deepdesk"):
        assert isinstance(root, Root)
        self.profile = profile
        self.owner = profile
        self.created = isodate.datetime_isoformat(
            datetime.fromtimestamp(time.time()))
        self.root = root
        self.hash = None
        self.salt = None
        self.base = None
        self.privs = None
        self.fields = {}
        self.last_saved = None
        if str(key).startswith("|"):
            hook = includehook
            key = str(key)[1:]
        else:
            hook = loadhook
        self.key = Key(str(key))
        if self.key.value.endswith("/"):
            if self.key.value.startswith("data/"):
                template = Record(
                    self.root,
                    self.key.value.replace("data/", "|template/"))[:-1]
            else:
                template = Record(
                    self.root,
                    "|template/" + self.key.value[:-1])
            if template.exists:
                self.base = template.key.location[:-5]
                self.importrecord(template.fields)
            self.key.value += str(uuid.uuid4()).replace("-", "/")
            self.path = self.root.join(self.key.location)
        else:
            self.path = self.root.join(self.key.location)
            try:
                self.path = max(glob(self.path[:-5] + "*.json"))
                self.key = Key(self.path[len(self.root.basepath) + 1:])
                self.version = int(self.key.value[-9:-5])
            except:
                pass
            if os.path.islink(self.path):
                self.path = os.path.realpath(self.path)
                self.key = Key(self.path[len(root) + 1:].replace(os.sep, '/'))
            if self.exists:
                with self.open() as file:
                    self.last_saved = isodate.datetime_isoformat(
                        datetime.fromtimestamp(os.path.getmtime(self.path))
                    )
                    self.importrecord(json.load(file, object_hook=hook))
        if indict:
            # indict with default of {} caused weird problems..
            # was getting values from root._search.fields somehow!
            self.importrecord(indict)
        self.updateprivs(profile)

    def deindex(self, item=None):
        """Remove all system indices for this record."""
        if item is None:
            item = self.fields
        if isinstance(item, Index):
            if item.index:
                indexfile = IndexFile(self.root, item.index)
                indexfile.delete(item.value)
        elif isinstance(item, Key):
            listfile = ListFile(
                self.root,
                Key(item.value).location[:-5] + ".ref")
            listfile.remove(str(self.key))
        elif isinstance(item, Alias):
            path = Path(self.root, Key(item.alias).location)
            if path.exists:
                path.lock()
                os.remove(path.path)
                path.release()
        elif isinstance(item, (list, tuple)):
            for i in item:
                self.deindex(i)
        elif isinstance(item, dict):
            self.deindex(list(item.values()))
        os.remove(self.path[:-5] + ".cit")
        # todo deindex Search & Group objects

    def importrecord(self, indict):
        """Imports indict into this record."""
        if '__record__' in indict:
            if 'owner' in indict:
                self.owner = indict['owner']
            if 'hash' in indict:
                try:
                    self.hash = binascii.a2b_hex(indict['hash'])
                except:
                    self.hash = True
                self.salt = indict['salt']
            if 'base' in indict:
                self.base = indict['base']
            if 'created' in indict:
                self.created = indict['created']
            indict = indict['value']
        for name, value in indict.items():
            if name in self.fields and not isinstance(value, Field):
                f = self.fields[name]
                if hasattr(f, 'value'):
                    while hasattr(f.value, 'value'):
                        f = f.value
                    f.value = value
                    continue
            if isinstance(value, Field):
                self.fields[name] = value
            else:
                self.fields[name] = Field(value)

    def purge(self):
        """Deindex and remove this record from disk."""
        self.deindex()
        if self.exists:
            os.remove(self.path)

    def reindex(self, item=None):
        """Update all system indices for this record"""
        indexed = False
        if item is None:
            item = self.fields
        if isinstance(item, Index):
            indexed = True
            if item.index:
                indexfile = IndexFile(self.root, item.index)
                indexfile.write(item.value, self.key)
        elif isinstance(item, Collect):
            if item.active and item.collect and item.value is not None:
                listfile = ListFile(
                    self.root, "/".join("collection", item.collection))
                listfile.append(item.value)
        elif isinstance(item, Key):
            if item.value != self.key.value:
                if not item.value.endswith("/"):
                    listfile = ListFile(self.root, self.key.location[:-5] + ".cit")
                    listfile.append(item)
                    listfile = ListFile(
                        self.root,
                        Key(item.value).location[:-5] + ".ref")
                    listfile.append(self.key)
        elif isinstance(item, Group):
            if item.index and item.value is not None:
                if item.value not in ["", [], ()]:
                    if not isinstance(item.value, dict):
                        if not isinstance(item.value, (list, tuple)):
                            v = [item.value]
                        else:
                            v = item.value
                    for value in v:
                        listfile = ListFile(self.root, "group/" + item.group)
                        list.append(self.key)
        elif isinstance(item, Search):
            if item.value:
                stemmer = Path(tempfile.gettempdir(), 'deepdesk.stemmer')
                stemmer.lock()
                for word in [
                        w.lower() for w in set(
                            self.root._stemmer.stemWords(item.value.split()))
                        if w.lower() not in self.root._search['stopwords']]:
                    parts = re.findall(
                        '.' * self.root._search['pathsplit'], word)
                    listfile = ListFile(
                        self.root,
                        '/'.join(['search', '/'.join(parts), word]))
                    listfile.append(self.key)
                stemmer.release()
        elif isinstance(item, (list, tuple)):
            for i in item:
                indexed = indexed or self.reindex(i)
        elif isinstance(item, dict):
            indexed = indexed or self.reindex(list(item.values()))
        elif isinstance(item, Field):
            indexed = indexed or self.reindex(item.value)
        if item == self.fields:
            if not indexed:
                listfile = ListFile(self.root, "index/unindexed")
                listfile.append(self.key)
        else:
            return indexed

    def save(self):
        """Save this record to disk."""
        if hasattr(self, 'version'):
            try:
                path = max(glob(self.root.join(str(self.key) + "*.json")))
                self.version = int(path[-9:-5]) + 1
            except:
                pass
            n = "000" + str(self.version)
            self.key.value = str(self.key) + "." + n[-4:] + ".json"
            self.path = self.root.join(self.key.value)
        with self.open("w") as file:
            if self.root.pretty:
                json.dump(self, file, indent=4, sort_keys=True, cls=encoder)
            else:
                json.dump(self, file, separators=(',', ':'), cls=encoder)
        if not self.key.startswith("template"):
            self.reindex()

    def storealias(self, alias):
        """
        Stores an alias for this record.
        An alias is an alternate key which refers to the same record.
        """
        path = Path(self.root, alias)
        path.lock()
        if os.path.islink(path.path):
            os.remove(path.path)
        os.symlink(self.path, path.path)
        path.release()

    def updateprivs(self, user=None):
        """
        Update active priviledges (x.privs).

        x.privs is an int from 0 to 100 where 1 is public and 100 is
        the owner of the record. 0 is reserved for system (ie no access).
        """
        PUBLIC
        if user is None:
            user = self.profile
        if self.owner == user:
            self.privs = PRIVATE
        else:
            self.privs = PUBLIC

    def __setitem__(self, name, value):
        """x.__setitem__(i, y) <==> x[i]=y"""
        if name in self.fields and \
                hasattr(self.fields[name], 'value') and \
                self.fields[name].__class__ != Field:
            self.fields[name].value = value
        else:
            self.fields[name] = value

    def __getitem__(self, name):
        """x.__getitem__(y) <==> x[y]"""
        if isinstance(name, int):
            value = self.fields.values()[name]
        else:
            value = self.fields[name]
        if isinstance(value, Access):
            if self.privs >= value.access:
                return value
            else:
                return None
        if hasattr(value, 'value'):
            return value.value
        else:
            return value

    def __delitem__(self, name):
        """x.__delitem__(y) <==> del x[y]"""
        del(self.fields[name])

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        s = "indict={}".format(repr(self.fields))
        if self.key.value:
            s = "key={}, ".format(repr(self.key.location)) + s
        return "Record({}, profile={})".format(s, repr(self.profile))

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return str(self.fields)

    def __len__(self):
        """x.__len__() <==> len(x)"""
        return len(self.fields)

    def jsonencode(self):
        """Returns a json representation of the object."""
        d = {
            '__record__': self.key.clean,
            'value': self.fields}
        d['owner'] = self.owner
        d['created'] = self.created
        if self.hash:
            d['hash'] = binascii.b2a_hex(self.hash).decode()
            if self.salt:
                d['salt'] = self.salt
            else:
                d['salt'] = True
        if self.base:
            d['base'] = self.base
        return d


class Root:
    """
    The root directory object for the database.
    """
    def __init__(self, path="./root", pretty=True):
        self.basepath = os.path.abspath(path)
        self.pretty = pretty

        # Setup stemmer for search term reduction

        self._search = Record(self, "deepdesk/search")
        if not self._search.exists:
            self._search.fields.update(
                {
                    'stemmer': 'english',
                    'cache': 0,
                    'pathsplit': 3,
                    'stopwords': sorted(['them', 'then', 'thei', 'she', 'what', 'would', 'own', 'no', 'either', 'off', 'wa', 'we', 'but', 'often', 'all', 'not', 'nor', 'where', 'should', 'abl', 'almost', 'get', 'on', 'of', 'onli', 'or', 'could', 'also', 'into', 'our', 'must', 'your', 'for', 'other', 'els', 'dear', 'most', 'and', 'some', 'do', 'ani', 'whom', 'among', 'thi', 'the', 'might', 'him', 'like', 'me', 'had', 'becaus', 'their', 'did', 'my', 'been', 'can', 'while', 'doe', 'why', 'ever', 'rather', 'too', 'neither', 'who', 'with', 'when', 'these', 'so', 'i', 'sinc', 'have', 'how', 'after', 'sai', 'u', 'you', 'ti', 'were', 'to', 'across', 'that', 'which', 'than', 'an', 'am', 'got', 'yet', 'ar', 'at', 'cannot', 'hi', 'he', 'howev', 'ha', 'from', 'let', 'mai', 'said', 'a', 'be', 'want', 'least', 'by', 'twa', 'it', 'her', 'there', 'just', 'if', 'everi', 'in', 'will']),
                }
            )

        self._stemmer = Stemmer(
            self._search['stemmer'], self._search['cache'])

    def __len__(self):
        return len(self.basepath)

    def __str__(self):
        return str(self.basepath)

    def __repr__(self):
        return "Root({})".format(repr(self.basepath))

    def join(self, *args):
        """
        join(path) -> path

        Use instead of os.path.join to ensure that path is below the root.
        """
        path = os.path.abspath(os.path.join(self.basepath, *args))
        assert path.startswith(self.basepath)
        return path

    def browse(self, location=""):
        """
        browse(location) -> list

        Returns a list of items stored in the location.

        >>> browse('data')
        ['menu', 'imports', 'schema.org', 'deepdesk']
        >>> browse("data/menu/schema.org")
        ['Data Type', 'Thing', 'Data Type.json', 'Thing.json']
        """
        if location.endswith("*"):
            path = self.join(*location.split('/')[:-1])
            start = location.split('/')[-1][:-1]
        else:
            path = self.join(*location.split('/'))
            start = ""
        if os.path.isdir(path):
            return [p for p in os.listdir(path)
                    if p.split('/')[-1].startswith(start)]
        else:
            if os.path.exists(path):
                return [os.path.split(path)[-1]]
            else:
                return []

    def init(self):
        """
        Initialise root database
        """
        # setup system records
        if not self._search.exists:
            self._search.save()
        # import schema.org
        schema = Record(self, "imports/schema.org")
        if not schema.exists:
            schema.fields = requests.get(
                "http://schema.rdfs.org/all.json").json()
            schema.save()
        r = Record(self, "schema.org")
        update = True
        if r.exists:
            if schema['valid'] != r['valid']:
                r['valid'] = schema['valid']
                r.save()
            else:
                update = False
        else:
            r['valid'] = schema['valid']
            r.save()
        if update:
            for section in schema.fields.keys():
                for datatype in schema[section]:
                    if section == 'valid':
                        continue
                    key = "schema.org/" + schema[section][datatype]['id']
                    record = Record(
                        self, key, indict=schema[section][datatype])
                    record['id'] = \
                        Key("schema.org/" + str(record['id'])).clean
                    for name in [
                            'supertypes',
                            'ancestors',
                            'subtypes',
                            'properties',
                            'specific_properties',
                            'domains',
                            'ranges']:
                        if name in record.fields:
                            record[name] = [
                                Key("schema.org/" + a)
                                for a in record[name]]
                    if not isinstance(record['label'], Search):
                        record['label'] = Search(record['label'])
                    record.save()
                    if 'ancestors' in record.fields and section.endswith('types'):
                        alias = "/".join(['menu', 'schema.org'] + [
                            titlespace(keysplit(s.clean)[1]) for s in record['ancestors']] + [str(record['label'])]) + ".json"
                        record.storealias(alias)

    def search(self, value):
        """
        search(value) -> set

        This returns a set of matching keys for the search value.
        The search value can be a str or a list of str.

        >>> search("web")
        {'schema.org/WebPage', 'schema.org/WebPageElement', 'schema.org/WebApplication', 'schema.org/MedicalWebPage'}

        >>> search("page")
        {'schema.org/UserPageVisits', 'schema.org/WebPage', 'schema.org/ContactPage', 'schema.org/numberOfPages', 'schema.org/ItemPage', 'schema.org/representativeOfPage', 'schema.org/CollectionPage', 'schema.org/WebPageElement', 'schema.org/SearchResultsPage', 'schema.org/CheckoutPage', 'schema.org/MedicalWebPage', 'schema.org/mainContentOfPage', 'schema.org/printPage', 'schema.org/AboutPage', 'schema.org/primaryImageOfPage', 'schema.org/ProfilePage'}

        >>> search(["page", "web"])
        {'schema.org/WebPage', 'schema.org/WebPageElement', 'schema.org/MedicalWebPage'}
        """
        if isinstance(value, str):
            value = (value,)
        result = None
        stemmer = Path(tempfile.gettempdir(), 'deepdesk.stemmer')
        stemmer.lock()
        for word in [
                w.lower() for w in set(
                    self._stemmer.stemWords(value))
                if w.lower() not in self._search['stopwords']]:
            parts = re.findall('.' * self._search['pathsplit'], word)
            searchindex = ListFile(
                self, "/".join(['search', "/".join(parts), word]))
            if not result:
                result = set(searchindex.load())
            else:
                result = set([
                    line for line in searchindex.load()
                    if line in result])
            if not result:
                stemmer.release()
                return result
        stemmer.release()
        return result

    def Record(self, *args, **kwargs):
        return Record(self, *args, **kwargs)

    def Path(self, *args, **kwargs):
        return Path(self, *args, **kwargs)

    def IndexFile(self, *args, **kwargs):
        return IndexFile(self, *args, **kwargs)

    def ListFile(self, *args, **kwargs):
        return ListFile(self, *args, **kwargs)


class Key(Field):
    """
    Key field wrapper.
    Fields wrapped with key are references to other records.
    The record with the key will have the key added to it's .cit file.
    The record referred to will have the record with the key added
    to it's .ref file.
    """
    @property
    def clean(self):
        key = self.value
        if key.startswith("data/"):
            key = key[5:]
        if key.endswith(".json"):
            key = key[:-5]
        try:
            e = key.split(".")[-1]
            if len(e) != 4:
                raise Exception
            i = int(e)
            key = key[:-5]
        except:
            pass
        return key

    @property
    def location(self):
        if self.value.endswith("/"):
            folder = self.value[:-1]
            id = ""
            extension = ".json"
        else:
            basekey, ext = os.path.splitext(self.value)
            try:
                version = int(ext[1:])
                basekey += ext
                extension = ".json"
            except:
                if ext != ".json":
                    extension = ".json"
                    basekey += ext
                else:
                    extension = ext
            try:
                # versioned record
                e = basekey.split(".")[-1]
                if len(e) != 4:
                    raise Exception
                version = int(e)
                basekey = ".".join(basekey.split(".")[:-1])
            except:
                pass
            try:
                # uuid record
                if basekey[-37] != "/":
                    raise Exception
                id = str(uuid.UUID(value[-36:].replace("/", "-")))
                folder = value[:-37]
            except:
                folder, id = keysplit(basekey)
                if not id:
                    id = folder
                    folder = ""
        if folder.startswith(("template/", "data/", "deepdesk/", "menu/")) or\
                folder in ["template", "data", "deepdesk", "menu"]:
            section = ""
        else:
            if folder == "":
                section = ""
                if id == "":
                    id = "data"
                else:
                    folder = "data"
            else:
                section = "data"
        loc = "/".join([section, folder, id]) + extension
        while loc[0] == "/":
            loc = loc[1:]
        return loc

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Key({})".format(repr(self.clean))

    def __str__(self):
        """x.__str__() <==> str(x)"""
        return self.clean

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {'__key__': self.clean}


class Index(Field):
    """
    Index field wrapper.
    Fields wrapped with index will have their value and the record.key
    stored in the index.
    """
    def __init__(self, value=None, index=""):
        Field.__init__(self, value)
        self.index = index

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Index({}, {})".format(repr(self.value), repr(self.index))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__index__': self.index,
            'value': self.value}


class Access(Field):
    """
    Access field wrapper.
    """
    def __init__(self, value=None, access=PRIVATE):
        Field.__init__(self, value)
        self.access = access

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Access({}, {})".format(repr(self.value), repr(self.access))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__access__': self.access,
            'value': self.value}


class Collect(Field):
    """
    Collect field wrapper.
    Fields wrapped in a Collect will have their unique values stored
    in the collection. If active is False, then no collecting takes place.
    This is useful for prebuilt collections such as country codes where
    the field value should be in the collection, but new values
    should not be added.
    """
    def __init__(self, value=None, collection="", active=True):
        Field.__init__(self, value)
        self.collection = collection
        self.active = active

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Collect({}, {}, {})".format(
            repr(self.value), repr(self.collection), repr(self.active))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__collect__': self.collection,
            'active': self.active,
            'value': self.value}


class Group(Field):
    """
    Group field wrapper.
    Fields wrapped in a group will have their
    record.key stored in the group index for their values.
    """
    def __init__(self, value=None, group=""):
        Field.__init__(self, value)
        self.group = group

    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Group({}, {})".format(repr(self.value), repr(self.group))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__group__': self.group,
            'value': self.value}


class Include(dict):
    """
    Include class for templates.
    Normal records should use Key fields rather than Include.
    """
    def __init__(self, key):
        dict.__init__(self, {'__include__': key})


class Search(Field):
    """
    Search field wrapper.
    Strings wrapped with search will have their words stored in the
    search indices.
    """
    def __repr__(self):
        """x.__repr__() <==> repr(x)"""
        return "Search({})".format(repr(self.value))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {'__search__': self.value}


class Validate(Field):
    """
    Validate field wrapper.
    Provides validation features for the wrapped field.
    """
    @property
    def isvalid(self):
        return validate(self.value, self.rule)

    def __init__(self, value=None, rule=""):
        Field.__init__(self, value)
        self.rule = rule

    def __repr__(self):
        return ("Validate({}, {})".format(repr(self.value), repr(self.rule)))

    def jsonencode(self):
        """Returns a json representation of the object."""
        return {
            '__validate__': self.rule,
            'value': self.value}


# Hooks and Encoder for json

def loadhook(dct):
    if '__key__' in dct:
        return Key(dct['__key__'])
    elif '__validate__' in dct:
        return Validate(dct['value'], dct['__validate__'])
    elif '__access__' in dct:
        return Access(dct['value'], dct['__access__'])
    elif '__collect__' in dct:
        return Collect(dct['value'], dct['__collect__'])
    elif '__group__' in dct:
        return Group(dct['value'], dct['__group__'])
    elif '__index__' in dct:
        return Index(dct['value'], dct['__index__'])
    elif '__search__' in dct:
        return Search(dct['__search__'])
    elif '__include__' in dct:
        return Include(dct['__include__'])
    return dct


def includehook(dct):
    if '__include__' in dct:
        return Record(key=dct['__include__']).fields
    return loadhook(dct)


class Encoder(json.JSONEncoder):
    def default(self, item):
        try:
            return item.jsonencode()
        except:
            return json.JSONEncoder.default(self, item)

encoder = Encoder

