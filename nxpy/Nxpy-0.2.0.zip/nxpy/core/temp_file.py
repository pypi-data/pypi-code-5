# nxpy.core package ----------------------------------------------------------

# Copyright Nicola Musatti 2010 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Temporary files and directories.

Requires at least Python 2.6

"""

import logging
import os
import shutil
import stat
import tempfile

import nxpy.core.file_object


class TempFile(nxpy.core.file_object.WritableFileObject):
    r"""A temporary file that implements the context manager protocol.
    
    Wrap a :py:func:`tempfile.NamedTemporaryFile` generated file-like object, to ensure it is not
    deleted on close, but rather when the underlying context is closed.
    
    """
    def __init__(self, *args, **kwargs):
        r"""Create a temporary file with the given arguments."""
        # Python 2.5 compatible syntax. Doesn't work, but ensures that tests are skipped rather
        # than broken.
        # file = tempfile.NamedTemporaryFile(*args, delete=False, **kwargs)
        kwargs["delete"] = False
        file_ = tempfile.NamedTemporaryFile(*args, **kwargs)
        super(TempFile, self).__init__(file_)
    
    @property
    def name(self):
        r"""Return the actual file name."""
        return self._file.name

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()
        os.remove(self._file.name)
        return False


class TempDir(object):
    r"""A temporary directory that implements the context manager protocol.
    
    The directory is removed when the context is exited from. Uses :py:func:`tempfile.mkdtemp` to 
    create the actual directory.
    
    """
    def __init__(self, *args, **kwargs):
        r"""Create a temporary directory with the given arguments."""
        self.dir = tempfile.mkdtemp(*args, **kwargs)
        mode = os.stat(self.dir).st_mode
        os.chmod(self.dir, mode | stat.S_IWRITE)

    @property
    def name(self):
        r"""Return the directory name."""
        return self.dir

    def _on_error(self, func, path, ex_info):
        try:
            mode = os.stat(path).st_mode
            if not stat.S_ISLNK(mode):
                os.chmod(path, mode | stat.S_IWRITE)
                if stat.S_ISDIR(mode):
                    os.rmdir(path)
                else:
                    os.remove(path)
            return
        except:
            pass
        logging.error(path + ": not removed")
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dir, ignore_errors=False, onerror=self._on_error)
        return False
