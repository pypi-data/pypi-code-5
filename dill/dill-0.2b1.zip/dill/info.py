# THIS FILE GENERATED FROM SETUP.PY
this_version = '0.2b1'
stable_version = '0.2b1'
readme = '''---------------------------------------------------
dill: a utility for serialization of python objects
---------------------------------------------------

Dill extends python's 'pickle' module for serializing and de-serializing
python objects to the majority of the built-in python types. Serialization
is the process of converting an object to a byte stream, and the inverse
of which is converting a byte stream back to on python object hierarchy.

Dill provides the user the same interface as the 'pickle' module, and
also includes some additional features. In addition to pickling python
objects, dill provides the ability to save the state of an interpreter
session in a single command.  Hence, it would be feasable to save a
interpreter session, close the interpreter, ship the pickled file to
another computer, open a new interpreter, unpickle the session and
thus continue from the 'saved' state of the original interpreter
session.

Dill can be used to store python objects to a file, but the primary
usage is to send python objects across the network as a byte stream.
Dill is quite flexible, and allows arbitrary user defined classes
and funcitons to be serialized.  Thus dill is not intended to be
secure against erroneously or maliciously constructed data. It is
left to the user to decide whether the data they unpickle is from
a trustworthy source.

Dill is part of pathos, a python framework for heterogeneous computing.
Dill is in the early development stages, and any user feedback is
highly appreciated. Contact Mike McKerns [mmckerns at caltech dot edu] with
comments, suggestions, and any bugs you may find.  A list of known issues
is maintained at http://trac.mystic.cacr.caltech.edu/project/pathos/query.


Major Features
==============

Dill can pickle the following standard types::

    - none, type, bool, int, long, float, complex, str, unicode,
    - tuple, list, dict, file, buffer, builtin,
    - both old and new style classes,
    - instances of old and new style classes,
    - set, frozenset, array, functions, exceptions

Dill can also pickle more 'exotic' standard types::

    - functions with yields, nested functions, lambdas,
    - cell, method, unboundmethod, module, code, methodwrapper,
    - dictproxy, methoddescriptor, getsetdescriptor, memberdescriptor,
    - wrapperdescriptor, xrange, slice,
    - notimplemented, ellipsis, quit

Dill cannot yet pickle these standard types::

    - frame, generator, traceback

Dill also provides the capability to::

    - save and load python interpreter sessions
    - save and extract the source code from functions and classes
    - interactively diagnose pickling errors


Current Release
===============

This release version is dill-0.2b1. You can download it here.
The latest released version of dill is always available from::

    http://dev.danse.us/trac/pathos

Dill is distributed under a 3-clause BSD license.


Development Release
===================

You can get the latest development release with all the shiny new features at::

    http://dev.danse.us/packages

or even better, fork us on our github mirror of the svn trunk::

    https://github.com/uqfoundation


Installation
============

Dill is packaged to install from source, so you must
download the tarball, unzip, and run the installer::

    [download]
    $ tar -xvzf dill-0.2b1.tgz
    $ cd dill-0.2b1
    $ python setup py build
    $ python setup py install

You will be warned of any missing dependencies and/or settings
after you run the "build" step above. 

Alternately, dill can be installed with easy_install or pip::

    [download]
    $ easy_install -f . dill


Requirements
============

Dill requires::

    - python2, version >= 2.5  *or*  python3, version >= 3.1

Optional requirements::

    - setuptools, version >= 0.6
    - objgraph, version >= 1.7.2


Usage Notes
===========

Probably the best way to get started is to look at the tests
that are provide within dill. See `dill.tests` for a set of scripts
that test dill's ability to serialize different python objects.
Since dill conforms to the 'pickle' interface, the examples and
documentation at http://docs.python.org/library/pickle.html also
apply to dill if one will `import dill as pickle`.


License
=======

Dill is distributed under a 3-clause BSD license.

    >>> import dill
    >>> print (dill.license())


Citation
========

If you use dill to do research that leads to publication,
we ask that you acknowledge use of dill by citing the
following in your publication::

    M.M. McKerns, L. Strand, T. Sullivan, A. Fang, M.A.G. Aivazis,
    "Building a framework for predictive science", Proceedings of
    the 10th Python in Science Conference, 2011;
    http://arxiv.org/pdf/1202.1056

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    http://dev.danse.us/trac/pathos


More Information
================

Please see http://dev.danse.us/trac/pathos or http://arxiv.org/pdf/1202.1056 for further information.

'''
license = '''This software is part of the open-source mystic project at the California
Institute of Technology, and is available subject to the conditions and
terms laid out below. By downloading and using this software you are
agreeing to the following conditions.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met::

    - Redistribution of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

    - Redistribution in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentations and/or other materials provided with the distribution.

    - Neither the name of the California Institute of Technology nor
      the names of its contributors may be used to endorse or promote
      products derived from this software without specific prior written
      permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Copyright (c) 2013 California Institute of Technology. All rights reserved.

'''
