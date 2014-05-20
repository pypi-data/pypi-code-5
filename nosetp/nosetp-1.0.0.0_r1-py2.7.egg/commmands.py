#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

try:
    from setuptools import Commands
except ImportError:
    pass
else:

    import sys

    class nosetp(Command):
        description = "Run nosetests, with extended options."
        
        user_options = tuple()

        def initialize_options(self):
            pass

        def finalize_options(self):
            pass

        def run(self):
            orig_exit = sys.exit
            exit_code = None
            def exit(code=None):
                exit_code = code
                if exit_code:
                    orig_exit(code)

            sys.exit = exit
            self.run_command('nosetests')
            sys.exit = orig_exit

