#! /usr/bin/env python
# vim: set fileencoding=utf-8: 
"""
Defines additional `commands <setuptools:setuptools.Command>` for setuptools_.
"""

try:
    from setuptools import Command
except ImportError:
    Command = nosetp = None
else:

    import sys
    from docit import nodoc, docit
    from nose.commands import nosetests

    __all__ = ['nosetp']

    _nosetests_options = list(nosetests.user_options)
    _nosetests_options.append(('nosetp-chain', None, 'Exit if any tests fail, otherwise continue with subsequent commands.'))

    class nosetp(nosetests):
        """
        .. program:: nosetp

        Provides the :program:`nosetp` command for setuptools_, which is simply
        a wrapper around the `nosetests <nose:nose.commands.nosetests>` command with some
        added functionality and options.

        .. option:: --nosetp-chain

            This option inhibits the normal exit behavior of the `nosetests <nose:nose.commands.nosetests>`
            command so that it exits after running the tests if and only if the tests
            failed, otherwise it continues on. This allows you to chain additional
            :program:`setup.py` commands after the :program:`nosetp`
            command, which will only be run if the tests pass. Very useful for aliases,
            particularly for :ref:`uploading <setuptools:upload>` your program to
            the pypi server.

        .. seealso::

            `nose:nose.commands`
        """

        description = "Run nosetests, with extended options."
        """
        The help description for the command, shown by :program:`setup.py`
        """
        
        user_options = _nosetests_options

        def initialize_options(self):
            """
            Called to initialize all available `user_options` as corresponding
            attributes on ``self``.
            """
            nosetests.initialize_options(self)
            self.nosetp_chain = False

        def run(self):
            """
            Overrides the default in the ``nosetests`` base class to implement
            the additional functionality. In general, it delegates to the
            base class.
            """
            orig_exit = sys.exit
            exit_code = None
            def exit(code=None):
                exit_code = code
                if exit_code:
                    orig_exit(code)

            if getattr(self, 'nosetp_chain', False):
                sys.exit = exit
            nosetests.run(self)
            sys.exit = orig_exit

