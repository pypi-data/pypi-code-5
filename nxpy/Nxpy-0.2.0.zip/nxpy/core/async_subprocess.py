# nxpy.core package ----------------------------------------------------------

# Copyright Nicola Musatti 2008 - 2014
# Use, modification, and distribution are subject to the Boost Software
# License, Version 1.0. (See accompanying file LICENSE.txt or copy at
# http://www.boost.org/LICENSE_1_0.txt)

# See http://nxpy.sourceforge.net for library home page. ---------------------

r"""
Allow asynchronous interaction with a subprocess.

This module was taken from `this recipe 
<http://code.activestate.com/recipes/440554-module-to-allow-asynchronous-subprocess-use-on-win/>`_ 
in the `ActiveState Code Recipes website 
<http://code.activestate.com/recipes/langs/python/>`_, with only minor
modifications. This is the original description: ::

  Title:        Module to allow Asynchronous subprocess use on Windows and Posix platforms
  Submitter:    Josiah Carlson (other recipes)
  Last Updated: 2006/12/01
  Version no:   1.9
  Category:     System 

"""

import os
import subprocess
import errno
import time
import sys

## PIPE = subprocess.PIPE

if subprocess.mswindows:
    from win32file import ReadFile, WriteFile
    from win32pipe import PeekNamedPipe
    import msvcrt
else:
    import select
    import fcntl

class AsyncPopen(subprocess.Popen):
    r"""
    An asynchronous variant to :py:class:`subprocess.Popen`, which doesn't block on incomplete I/O 
    operations.
    
    Note that the terms input, output and error refer to the controlled program streams,
    so we receive from output or error and we send to input.
    
    """

    def recv(self, maxsize=None):
        r"""Receive at most *maxsize* bytes from the subprocess's standard output."""
        return self._recv('stdout', maxsize)
    
    def recv_err(self, maxsize=None):
        r"""Receive at most *maxsize* bytes from the subprocess's standard error."""
        return self._recv('stderr', maxsize)

    def send_recv(self, input_='', maxsize=None):
        r"""
        Send *input_* to the subprocess's standard input and then receive at most *maxsize* bytes
        from both its standard output and standard error.

        """
        return self.send(input_), self.recv(maxsize), self.recv_err(maxsize)

    def get_conn_maxsize(self, which, maxsize):
        r"""
        Return *which* output pipe (either stdout or stderr) and *maxsize* constrained to the 
        [1, 1024] interval in a tuple.
        
        """
        if maxsize is None:
            maxsize = 1024
        elif maxsize < 1:
            maxsize = 1
        return getattr(self, which), maxsize
    
    def _close(self, which):
        getattr(self, which).close()
        setattr(self, which, None)
    
    if subprocess.mswindows:
        def send(self, input_):
            r"""Send *input_* to the subprocess's standard input."""
            if not self.stdin:
                return None

            try:
                x = msvcrt.get_osfhandle(self.stdin.fileno())
                (errCode, written) = WriteFile(x, input_)
            except ValueError:
                return self._close('stdin')
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None
            
            try:
                x = msvcrt.get_osfhandle(conn.fileno())
                (read, nAvail, nMessage) = PeekNamedPipe(x, 0)
                if maxsize < nAvail:
                    nAvail = maxsize
                if nAvail > 0:
                    (errCode, read) = ReadFile(x, nAvail, None)
            except ValueError:
                return self._close(which)
            except (subprocess.pywintypes.error, Exception), why:
                if why[0] in (109, errno.ESHUTDOWN):
                    return self._close(which)
                raise
            
            if self.universal_newlines:
                read = self._translate_newlines(read)
            return read

    else:
        def send(self, input_):
            r"""Send *input_* to the subprocess's standard input."""
            if not self.stdin:
                return None

            if not select.select([], [self.stdin], [], 0)[1]:
                return 0

            try:
                written = os.write(self.stdin.fileno(), input_)
            except OSError, why:
                if why[0] == errno.EPIPE: #broken pipe
                    return self._close('stdin')
                raise

            return written

        def _recv(self, which, maxsize):
            conn, maxsize = self.get_conn_maxsize(which, maxsize)
            if conn is None:
                return None
            
            flags = fcntl.fcntl(conn, fcntl.F_GETFL)
            if not conn.closed:
                fcntl.fcntl(conn, fcntl.F_SETFL, flags| os.O_NONBLOCK)
            
            try:
                if not select.select([conn], [], [], 0)[0]:
                    return ''
                
                r = conn.read(maxsize)
                if not r:
                    return self._close(which)
    
                if self.universal_newlines:
                    r = self._translate_newlines(r)
                return r
            finally:
                if not conn.closed:
                    fcntl.fcntl(conn, fcntl.F_SETFL, flags)

message = "Other end disconnected!"

def recv_some(p, t=.1, e=1, tr=5, stderr=0):
    r"""
    Try and receive data from :py:class:`.AsyncPopen` object *p*'s stdout in at most *tr* tries and
    with a timeout of *t*. If *stderr* is True receive from the subprocess's stderr instead.
    
    """
    if tr < 1:
        tr = 1
    x = time.time()+t
    y = []
    r = ''
    pr = p.recv
    if stderr:
        pr = p.recv_err
    while time.time() < x or r:
        r = pr()
        if r is None:
            if e:
                raise Exception(message)
            else:
                break
        elif r:
            y.append(r)
        else:
            time.sleep(max((x-time.time())/tr, 0))
    return ''.join(y)
    
def send_all(p, data):
    r"""Send all of *data* to :py:class:`.AsyncPopen` object *p*'s stdin."""
    while len(data):
        sent = p.send(data)
        if sent is None:
            raise Exception(message)
        data = buffer(data, sent)
