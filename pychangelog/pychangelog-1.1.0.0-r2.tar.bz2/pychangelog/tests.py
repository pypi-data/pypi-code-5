#! /usr/bin/env python
# vim: set fileencoding=utf-8: 
"""
The ``pychangelog.tests`` module provides some helper functions and classes for
testing your changelog, as well as standard ``version`` modules.

A standard version module is simply a module which you distribute as part of your
package (usually called ``package_name.version``) which includes as public members
a certain set of standard attributes providing information about the version number
of the package. Specifically, it provides the following attributes, which you
can read more about in *this* package's `~pychangelog.version` module:
    * `~pychangelog.version.RELEASE`
    * `~pychangelog.version.MAJOR`
    * `~pychangelog.version.MINOR`
    * `~pychangelog.version.PATCH`
    * `~pychangelog.version.SEMANTIC`
    * `~pychangelog.version.SUFFIX`
    * `~pychangelog.version.YEAR`
    * `~pychangelog.version.MONTH`
    * `~pychangelog.version.DAY`


Nosetests
-------------

Some of the code in this module is intended to work with the nose_ test utility
for python. While none of it strictly depends on nose to function, the ``node``
python package will be imported and used to provide some additional convenience
if it is available.
"""

try:
    from nose.plugins.attrib import attr
except ImportError:
    def attr(*args, **kwargs):
        def wrapper(func):
            return func
        return wrapper

import pychangelog
import unittest

__all__ = []

def public(obj):
    __all__.append(obj.__name__)
    return obj

def raise_(err, *msg):
    if len(msg):
        err = str(msg[0]) + ' '  + err
    raise AssertionError(err)

def ok_(test, *msg):
    if test:
        pass
    else:
        raise_("%r does not evaluate as true." % (test,), *msg)

def none_(test, *msg):
    if test is None:
        pass
    else:
        raise_("%r is not None." % (test,), *msg)

def eq_(a, b, *msg):
    if a == b:
        pass
    else:
        raise_('%r != %r' % (a, b,), *msg)

@public
def verify_version_module(changelog, version):
    """
    Generically tests the contents of a standard ``version`` module against the contents of
    the given `~pychangelog.ChangeLog` object, without any pre-existing assumptions about
    whether or not this is for a release or a development version.

    The latest full release (i.e., not a pre-release) in the changelog should correspond to
    the version and date information in the version module. If there is not full release in
    the change log, then the version module should list major version 0 and release 0.

    Additionally, if the change-log has no pre-release, then we should not be in development
    mode, meaning version.SUFFIX should be None. Otherwise, it should *not* be None.
    """

    last_release = changelog.get_last_release()


    #Contents of the version module should always match the latest full-release in the changelog.
    if last_release is not None:
        eq_(last_release.release_num, version.RELEASE, "Release number is incorrect. Expected latest release in change log to match version.RELEASE.")
        eq_(last_release.version[0], version.MAJOR, "Major version number is incorrect. Expected latest release in change log to match version.MAJOR.")
        eq_(last_release.version[1], version.MINOR, "Minor version number is incorrect. Expected latest release in change log to match version.MINOR.")

        test_version = last_release.version[2] if (len(last_release.version) > 2) else 0
        eq_(test_version, version.PATCH, "Patch version number is incorrect. Expected latest release in change log to match version.PATCH.")

        test_version = last_release.version[3] if (len(last_release.version) > 3) else 0
        eq_(test_version, version.SEMANTIC, "Semantic version number is incorrect. Expected latest release in change log to match version.SEMANTIC.")
    
        eq_(last_release.year, version.YEAR, "Year is incorrect. Expected latest release in change log to match version.YEAR.")
        eq_(last_release.month, version.MONTH, "Month is incorrect. Expected latest release in change log to match version.MONTH.")
        eq_(last_release.day, version.DAY, "Day is incorrect. Expected latest release in change log to match version.DAY.")

    else:
        #If there's no release in the changelog, then the version module should be at major version 0.

        eq_(version.RELEASE, 0, "No releases in changelog, version.RELEASE should be 0.")
        eq_(version.MAJOR, 0, "No releases in changelog, version.MAJOR should be 0.")

    if changelog.last_release() == len(changelog) - 1:
        #The latest entry in the change log is a full release, so we should not have suffix
        none_(version.SUFFIX, "Change log has release ready, version.SUFFIX should be None.")

    else:
        #The latest entry in the change log if a pre-release, so we should have a development suffix.

        ok_(version.SUFFIX is not None, "Change log has pre-release, version.SUFFIX should not be None.")


@public
def verify_for_release(changelog, version):
    """
    Tests a version module and change log for a release version. This calls `verify_version_module` to do
    the generic tests validating the version module against the changelog, and also tests that the version
    module and changelog are both correct for a release version.
    """
    none_(version.SUFFIX, "version.SUFFIX should be None for a release version.")
    eq_(changelog.last_release(), len(changelog)-1, "Changelog should not have a pre-release listing for a release version.")
    verify_version_module(changelog, version)

@public
def verify_for_development(changelog, version):
    """
    Tests a version module and change log for a release version. This calls `verify_version_module` to do
    the generic tests validating the version module against the changelog, and also tests that the version
    module and changelog are both correct for a release version.
    """
    ok_(version.SUFFIX is not None, "version.SUFFIX should not be None for a development version.")
    ok_(changelog.last_release() != len(changelog)-1, "Changelog should have a pre-release listing for a development version.")
    verify_version_module(changelog, version)


@public
class StandardVersionTests(unittest.TestCase):
    """
    This is a simple `~python:unittest.TestCase` class that can be easily extended
    for unittesting to validate your changelog and version module. All you need to
    do is subclass this class and set the `version_mod` attribute to the module
    which contains your project's standard version attributes.

    Alternatively, you can use the `create` factory method to create automatically
    create a new subclass with the specified version module.

    .. seealso::
        * `get_path_to_changelog` can be overridden to change the path from which
            the changelog will be read.
        * `get_changelog` can be overridden to change the way in which the changelog
            is actually loaded and parsed.
        * `get_version_module` can be overridden to change the way the version module
            is fetched, instead of just getting it form the `version_mod` attribute.
    """

    @classmethod
    def create(cls, version_mod):
        """
        Create and return a new subclass of `cls` which sets the `version_mod`
        attribute to the given version module. This is an alternative to statically
        subclassing if for some reason that's easier for you.
        """
        return type('StandardVersionTests_', (cls,), dict(version_mod = version_mod))

    version_mod = None
    """
    The `version_mod` attribute should be set on a subclass of `StandardVersionTests`
    to the module which implememnts your package's standard version attributes.


    .. seealso::
        `get_version_module`
    """

    def get_path_to_changelog(self):
        """
        Returns the filesystem path from which the changelog will be read by
        `get_changelog`.
        """
        return 'CHANGES.txt'

    def get_changelog(self):
        """
        Called from `setUp` to get a `~pychangelog.ChangeLog` object to test with.
        The default implementation opens the path indicates by `get_path_to_changelog`
        and parses it using `~pychangelog.parse_plain_text`.
        """
        with open(self.get_path_to_changelog(), 'r') as change_log_file:
            return pychangelog.parse_plain_text(change_log_file)

    def get_version_module(self):
        """
        Should returns a module which implements your projects standard version
        attributes. The default implementation returns the value of the `version_mod`
        attribute, which subclasses can easily set statically in the class definition.

        If this attribute value is ``None``, will raise a `NotImplementedError`.
        This is what will happen if you actually try to run an instance of this
        class directly, instead of subclassing it to override the value of the 
        version_mod attribute.
        """
        if self.version_mod is None:
            raise NotImplementedError('The version_mod attribute must be set in order to run the tests.')
        return self.version_mod

    def setUp(self):
        """
        Test setup sets a ``change_log`` attribute on the instance to the value returned
        by `get_changelog`.
        """
        self.change_log = self.get_changelog()

    def test_changelog(self):
        """
        Just does the `setUp` to make sure that the changelog can be parsed and
        constructed.
        """
        pass

    def test_version_module(self):
        """
        Invokes `verify_version_module`.
        """
        verify_version_module(self.change_log, self.get_version_module())

    @attr('release')
    def test_for_release(self):
        """
        Invokes `verify_for_release`.
        
        If nose_ is installed, this is tagged
        with the attribute ``release`` using the `~nose:nose.plugins.attrib` 
        plugin. To omit this test, you can invoke :program:`nosetests` using the
        :std:option:`--attr` parameter, for instance in BASH as:

        .. code-block:: bash

            $ nosetest --attr '!release'

        or in DOS as:

        .. code-block:: dos

            > nosetests --attr !release

        """
        verify_for_release(self.change_log, self.get_version_module())
        
    @attr('dev')
    def test_for_dev(self):
        """
        Invokes `verify_for_development`.
        
        If nose_ is installed, this is tagged
        with the attribute ``dev`` using the `~nose:nose.plugins.attrib` 
        plugin. To omit this test, you can invoke :program:`nosetests` using the
        :std:option:`--attr` parameter, for instance in BASH as:

        .. code-block:: bash

            $ nosetest --attr '!dev'

        or in DOS as:

        .. code-block:: dos

            > nosetests --attr !dev

        """
        verify_for_development(self.change_log, self.get_version_module())
        

    
