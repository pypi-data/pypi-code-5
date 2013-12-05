__title__ = 'starbase.exceptions'
__author__ = 'Artur Barseghyan'
__copyright__ = 'Copyright (c) 2013 Artur Barseghyan'
__license__ = 'GPL 2.0/LGPL 2.1'
__all__ = ('ImproperlyConfigured', 'InvalidArguments')

class ImproperlyConfigured(Exception):
    """
    Exception raised when developer didn't configure the code properly.
    """

class InvalidArguments(ValueError):
    """
    Exception raised when invalid arguments supplied.
    """
