# THIS FILE GENERATED FROM SETUP.PY
this_version = '0.1.1'
stable_version = '0.1.1'
readme = '''---------------------------------------------------
klepto: persistent caching to memory, disk, or database
---------------------------------------------------

Klepto extends python's 'lru_cache' to utilize different keymaps and
alternate caching algorithms, such as 'lfu_cache' and 'mru_cache'.
While caching is meant for fast access to saved results, klepto also
has archiving capabilities, for longer-term storage. Klepto uses a
simple dictionary-sytle interface for all caches and archives, and all
caches can be applied to any python function as a decorator. Keymaps
are algorithms for converting a function's input signature to a unique
dictionary, where the function's results are the dictionary value.
Thus for y = f(x), y will be stored in cache[x] (e.g. {x:y}).

Klepto provides both standard and 'safe' caching, where safe caches
are slower but can recover from hashing errors. Klepto is intended
to be used for distributed and parallel computing, where several of
the keymaps serialize the stored objects. Caches and archives are
intended to be read/write accessible from different threads and
processes. Klepto enables a user to decorate a function, save the
results to a file or database archive, close the interpreter,
start a new session, and reload the function and it's cache.

Klepto is part of pathos, a python framework for heterogenous computing.
Klepto is in the early development stages, and any user feedback is
highly appreciated. Contact Mike McKerns [mmckerns at caltech dot edu]
with comments, suggestions, and any bugs you may find. A list of known
issues is maintained at http://dev.danse.us/trac/pathos/query.


Major Features
==============

Klepto has standard and 'safe' variants of the following::

    - 'lfu_cache' - the least-frequently-used caching algorithm
    - 'lru_cache' - the least-recently-used caching algorithm
    - 'mru_cache' - the most-recently-used caching algorithm
    - 'rr_cache' - the random-replacement caching algorithm
    - 'no_cache' - a dummy caching interface to archiving
    - 'inf_cache' - an infinitely-growing cache

Klepto has the following archive types::

    - 'file_archive' - a dictionary-style interface to a file
    - 'dir_archive' - a dictionary-style interface to a folder of files
    - 'sqltable_archive' - a dictionary-style interface to a sql database table
    - 'sql_archive' - a dictionary-style interface to a sql database
    - 'dict_archive' - a dictionary with an archive interface
    - 'null_archive' - a dictionary-style interface to a dummy archive 

Klepto provides the following keymaps::

    - 'keymap' - keys are raw python objects
    - 'hashmap' - keys are a hash for the python object
    - 'stringmap' - keys are the python object cast as a string
    - 'picklemap' - keys are the serialized python object

Klepto also includes a few useful decorators providing::

    - simple, shallow, or deep rounding of function arguments
    - cryptographic key generation, with masking of selected arguments


Current Release
===============

This release version is klepto-0.1.1. You can download it here.
The latest released version of klepto is always available from::

    http://dev.danse.us/trac/pathos

Klepto is distributed under a 3-clause BSD license.


Development Release
===================

You can get the latest development release with all the shiny new features at::

    http://dev.danse.us/packages

or even better, fork us on our github mirror of the svn trunk::

    https://github.com/uqfoundation


Installation
============

Klepto is packaged to install from source, so you must
download the tarball, unzip, and run the installer::

    [download]
    $ tar -xvzf klepto-0.1.1.tgz
    $ cd klepto-0.1.1
    $ python setup py build
    $ python setup py install

You will be warned of any missing dependencies and/or settings
after you run the "build" step above. 

Alternately, klepto can be installed with easy_install or pip::

    [download]
    $ easy_install -f . klepto


Requirements
============

Klepto requires::

    - python2, version >= 2.5  *or*  python3, version >= 3.1
    - dill, version >= 0.2.1
    - pox, version >= 0.2

Optional requirements::

    - sqlalchemy, version >= 0.8.4
    - setuptools, version >= 0.6


Usage Notes
===========

Probably the best way to get started is to look at the tests
that are provide within klepto. See `klepto.tests` for a set of scripts
that test klepto's caching and archiving functionalities. Klepto's
source code is also generally well documented, so further questions may
be resolved by inspecting the code itself.


License
=======

Klepto is distributed under a 3-clause BSD license.

    >>> import klepto
    >>> print (klepto.license())


Citation
========

If you use klepto to do research that leads to publication,
we ask that you acknowledge use of klepto by citing the
following in your publication::

    Michael McKerns and Michael Aivazis,
    "pathos: a framework for heterogeneous computing", 2010- ;
    http://dev.danse.us/trac/pathos


More Information
================

Please see http://dev.danse.us/trac/pathos for further information.

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

Copyright (c) 2014 California Institute of Technology. All rights reserved.

'''
