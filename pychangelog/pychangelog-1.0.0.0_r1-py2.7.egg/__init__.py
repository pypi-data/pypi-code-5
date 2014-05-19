#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

"""
The toplevel module for the pychangelog package.
"""

from docit import *
import re
import collections
import types
import datetime
import threading
import abc


#Rel 3   - v1.0.0.2 - 2014-05-18
release_header_re = re.compile(r'^rel\s+(?P<rel>[0-9]+)\s+(?:-\s+)?v(?P<vers>[\.0-9]+)\s+(?:-\s+)(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})\s*$', re.I)
prerelease_header_re = re.compile(r'^pre[ -]?rel(?:ease)?\s+(?P<rel>[0-9]+)(?:\s*$|\s+(?:-\s+)?v(?P<vers>[\.0-9]+)\s+(?:-\s+)(?P<year>[0-9]{4})-(?P<month>[0-9]{1,2})-(?P<day>[0-9]{1,2})\s*$)', re.I)

class ChangeLog(collections.Sequence):
    """
    A ``ChangeLog`` object is simply a sequence of `ReleaseInfo` objects, in order form oldest to newest.
    There are rules used to validate the change log, for instance that each release must be numerically
    next after the previous, version numbers must increase correctly, full-releases cannot follow pre-releases,
    and dates must increase correctly.
    """
    def __init__(self, *releases):
        """
        Pass in the `ReleaseInfo` objects from oldest to newest.
        """
        self.__releases = []
        self.__last_release = None
        self.__lock = threading.Lock()
        for rel in releases:
            self.append(rel)

    def last_release(self):
        """
        Returns the **index** in the sequence of the last **full** release (i.e.,
        not a `~ReleaseInfo.pre_release`).

        Returns ``None`` if no full releases are mentioned in the change log.

        .. seealso::
            `get_last_release` to get the actul corresponding `ReleaseInfo` object.
        """
        return self.__last_release

    def get_last_release(self):
        """
        Returns the `ReleaseIngo` object for the last **full** release in the log
        (i.e., not a `~ReleaseInfo.pre_release`).

        Returns ``None`` if no full releases are mentioned in the change log.

        .. seealso::
            `last_release` to get just the index of the last release.
        """
        if self.__last_release is None:
            return None
        return self.__releases[self.__last_release]

    @docit
    def __len__(self):
        """
        Returns the number of releases in the change log.
        """
        return len(self.__releases)

    @docit
    def __getitem__(self, idx):
        """
        Get the `ReleaseInfo` object at the specified index, where 0 is the oldest.
        """
        return self.__releases[idx]

    def append(self, release):
        """
        Add a new `ReleaseInfo` object to the end (top) of the change log. This should be
        a release after the most recent.
        """
        if len(self.__releases):
            last = self.__releases[-1]
            if release.release_num != last.release_num + 1:
                raise ValueError("Releases are out of order. Expected %d next, found %d." % (last.release_num + 1, release.release_num))

            if last.pre_release and not release.pre_release:
                raise ValueError("Release %d cannot follow pre-release %d." % (release.release_num, last.release_num))

            if last.date is None and release.date is None:
                if release.date < last.date:
                    raise ValueError("Release %d cannot come before release %d." % (release.release_num, last.release_num))

            if last.version is not None and release.version is not None:
                vc_last = len(last.version)
                vc_next = len(release.version)
                vc = max(vc_last, vc_next)
                for i in xrange(vc):
                    vl = last.version[i] if (i < vc_last) else 0
                    vn = release.version[i] if (i < vc_next) else 0
                    if vn > vl:
                        break
                    elif vn < vl:
                        raise ValueError("Version number decreases releative to previous release: %s < %s" % (
                            ".".join(str(v) for f in release.version),
                            ".".join(str(v) for f in last.version),
                        ))
                    
        with self.__lock:
            idx = len(self.__releases)
            self.__releases.append(release)
            if not release.pre_release:
                self.__last_release = idx
                    

class ReleaseInfo(collections.Sequence):
    """
    Encapsulates information about a single release, usually a member of a `ChangeLog`.

    A `ReleaseInfo` object acts as a `~python:collections.Sequence` over the change-lines it
    mentions in the change log (i.e., the entries that describe the changes in the release
    from the previous.

    Each such line must have a type: usually one of `TYPE_MAJOR`, `TYPE_MINOR`, `TYPE_PATCH`,
    or `TYPE_SEMANTIC`, specfiying the scope of the impact on the public interface. However,
    for the first release (release #1), each line should instead be simple a `TYPE_STAR`
    line, since there is no public interface prior to the first release.

    In addition to iterating over all the lines in the release, you can get a `~ReleaseInfo.View`
    ojbect which acts as a Sequence over just a particular type of line. One such View is created
    during initialization for each of the five types of lines, and you can get a handle to these
    View objects using the `major`, `minor`, `patch`, `semantic`, and `starred` properties.

    """

    TYPE_STAR = 0
    TYPE_MAJOR = 1
    TYPE_MINOR = 2
    TYPE_PATCH = 3
    TYPE_SEMANTIC = 4

    def __init__(self, release_num, version_numbers, year, month, day, pre_release=False, *change_lines):
        def parse_int(value, name):
            if isinstance(value, int):
                return value

            try:
                return None if value is None else int(value, 10)
            except ValueError, e:
                raise ValueError("Invalid value for %s: %r" % (name, value,))

        self.__release_num = parse_int(release_num, 'release_num')
        self.__version = None if version_numbers is None else tuple(parse_int(v, 'version number') for v in version_numbers.split('.'))
        self.__year = parse_int(year, 'year')
        self.__month = parse_int(month, 'month')
        self.__day = parse_int(day, 'day')

        self.__pre_release = bool(pre_release)
        if not self.__pre_release:
            if any(x is None for x in (self.__version, self.__year, self.__month, self.__day)):
                raise ValueError("Release info values can only be None for pre-releases.")

        self.__date = None
        date_components = (self.__year, self.__month, self.__day)
        if all(x is not None for x in date_components):
            self.__date = datetime.date(*date_components)

        self.__majors = []
        self.__minors = []
        self.__patches = []
        self.__semantics = []
        self.__starred = []

        self.__major_view = ReleaseInfo.View(self, self.major_count, self.get_major)
        self.__minor_view = ReleaseInfo.View(self, self.minor_count, self.get_minor)
        self.__patch_view = ReleaseInfo.View(self, self.patch_count, self.get_patch)
        self.__semantic_view = ReleaseInfo.View(self, self.semantic_count, self.get_semantic)
        self.__starred_view = ReleaseInfo.View(self, self.starred_count, self.get_starred)

        self.__lock = threading.Lock()

        self.__change_lines = []
        for line in change_lines:
            self.append(line)


    def __str__(self):
        s = 'r%d' % self.release_num
        if self.pre_release:
            s += '*'
        vers = self.version
        if vers is not None:
            s += '-' + '.'.join(str(v) for v in self.version)
        date = self.date
        if date is not None:
            s += ' (%s)' % date.strftime('%x')

        return s

    def __repr__(self):
        return '<%s %s>' % (type(self).__name__, self.__str__(),)

    class View(collections.Sequence):
        def __init__(self, obj, length, getitem):
            self.__obj = obj
            self.__length = length
            self.__getitem = getitem

        def __len__(self):
            return self.__length.__func__(self.__obj)

        def __getitem__(self, idx):
            return self.__getitem.__func__(self.__obj, idx)


    @property
    def major(self):
        return self.__major_view

    @property
    def minor(self):
        return self.__minor_view

    @property
    def patch(self):
        return self.__patch_view

    @property
    def semantic(self):
        return self.__semantic_view

    @property
    def starred(self):
        return self.__starred_view

    def major_count(self):
        return len(self.__majors)

    def get_major(self, idx):
        return self.__change_lines[self.__majors[idx]]

    def minor_count(self):
        return len(self.__minors)

    def get_minor(self, idx):
        return self.__change_lines[self.__minors[idx]]

    def patch_count(self):
        return len(self.__patches)

    def get_patch(self, idx):
        return self.__change_lines[self.__patches[idx]]

    def semantic_count(self):
        return len(self.__semantics)

    def get_semantic(self, idx):
        return self.__change_lines[self.__semantics[idx]]

    def starred_count(self):
        return len(self.__starred)

    def get_starred(self, idx):
        return self.__change_lines[self.__starred[idx]]

    @property
    def pre_release(self):
        return self.__pre_release

    @property
    def release_num(self):
        return self.__release_num

    @property
    def version(self):
        return self.__version

    @property
    def year(self):
        return self.__year

    @property
    def month(self):
        return self.__month

    @property
    def day(self):
        return self.__day

    @property
    def date(self):
        return self.__date

    @property
    def release_num(self):
        return self.__release_num

    def __len__(self):
        return len(self.__change_lines)

    def __getitem__(self, idx):
        return self.__change_lines[idx]

    def iter(self):
        return iter(self.__change_lines)

    def append(self, line):
        ltype, pline = self.parse_line(line)
        if ltype == self.TYPE_STAR:
            if self.release_num != 1:
                raise ValueError("Only the first release (release #1) can have starred changeline. All others must be properly qualified.")
            seq = self.__starred

        else:
            if self.release_num == 1:
                raise ValueError("First release (release #1) should have only starred changelines.")

            if ltype == self.TYPE_MAJOR:
                seq = self.__majors
            elif ltype == self.TYPE_MINOR:
                seq = self.__minors
            elif ltype == self.TYPE_PATCH:
                seq = self.__patches
            elif ltype == self.TYPE_SEMANTIC:
                seq = self.__semantics
            else:
                raise Exception("Unhandled line type: %r" % (ltype,))

        with self.__lock:
            idx = len(self.__change_lines)
            self.__change_lines.append(line)
            seq.append(idx)
            
            

    @classmethod
    def parse_line(cls, line):
        if not isinstance(line, types.StringTypes):
            raise TypeError("Lines must be string types: %r" % line)

        if line.startswith('*'):
            line = line[1:].lstrip()
            return cls.TYPE_STAR, line

        if line.startswith('['):
            line = line[1:].lstrip()
            ltype = None
            if line[0] == 'M':
                ltype = cls.TYPE_MAJOR
            elif line[0] == 'n':
                ltype = cls.TYPE_MINOR
            elif line[0] == 'p':
                ltype = cls.TYPE_PATCH
            elif line[0] == 's':
                ltype = cls.TYPE_SEMANTIC
            elif line[0] == '*':
                ltype = cls.TYPE_STAR

            if ltype is not None:
                line = line[1:].lstrip()
                if line.startswith(']'):
                    line = line[1:].lstrip()
                    return ltype, line

        raise SyntaxError("No qualifying bullet at start of change line: %r" % line)
            



def parse_plain_text(istream):
    """
    Parses a change log in plain-text format, with newst release at the beginning,
    and returns a `ChangeLog` object.
    """
    releases = []
    state = 0
    change_line = None
    indent_1 = None
    indent_2 = None
    linenum = 0
    for line in istream:
        linenum += 1
        if state == 0:
            if len(line):
                if not line[0].isspace():
                    mobj = release_header_re.match(line)
                    if mobj is not None:
                        release_info = ReleaseInfo(
                            release_num = mobj.group('rel'),
                            version_numbers = mobj.group('vers'),
                            year = mobj.group('year'),
                            month = mobj.group('month'),
                            day = mobj.group('day'),
                        )

                        change_line = None
                        indent_1 = None
                        indent_2 = None
                        state = 1

                    else:
                        mobj = prerelease_header_re.match(line)
                        if mobj is not None:
                            release_info = ReleaseInfo(
                                release_num = mobj.group('rel'),
                                version_numbers = mobj.group('vers'),
                                year = mobj.group('year'),
                                month = mobj.group('month'),
                                day = mobj.group('day'),
                                pre_release = True,
                            )

                            change_line = None
                            indent_1 = None
                            indent_2 = None
                            state = 1

                        else:
                            raise SyntaxError("Invalid release header on line %d: %r" % (linenum, line))

                elif len(line.strip()):
                    raise SyntaxError("Invalid syntax on line %d. Expected a release header line: %r" % (linenum, line))

        elif state == 1:
            oline = line
            line = line.strip()
            if len(line) == 0:
                if change_line is not None:
                    release_info.append(change_line)
                    change_line = None
                releases.append(release_info)
                release_info = None
                change_lines = []
                state = 0

            else:
                indent_length = len(oline) - len(line)
                indent = oline[:indent_length-1]
                if indent_1 is None:
                    #First line
                    indent_1 = indent
                    change_line = line

                elif indent == indent_1:
                    #Next line.
                    release_info.append(change_line)
                    change_line = line

                else:
                    #Not the first-level indent.
                    if indent_2 is None:
                        #This should be the second level indent.
                        if not indent.startswith(indent_1):
                            raise SyntaxError("Invalid indent on line %d. Expected a second level indent beyond the first level indent." % (linenum,))

                        indent_2 = indent
                        change_line += line


                    elif indent == indent_2:
                        #Line continued
                        change_line += line

                    else:
                        #Invalid indent
                        raise SyntaxError("Invalid indent on line %d. Expected a first or second level indent." % (linenum,))

    
    if state == 1:
        if change_line is not None:
            release_info.append(change_line)
            change_line = None
        releases.append(release_info)
        release_info = None
        state = 0

    return ChangeLog(*reversed(releases))
                
            

