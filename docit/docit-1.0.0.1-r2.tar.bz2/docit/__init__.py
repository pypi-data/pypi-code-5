#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

"""
The ``docit`` package can be loaded as a Sphinx_ extension, and provides some
functionality for controlling whether or not members are documented by the
|autodoc| extension.

To use this extension, simply enable it in your Sphinx `conf.py <http://sphinx-doc.org/config.html>`_

    .. code:: python

        extensions = [
            'sphinx.ext.autodoc',
            'docit.ext',
            # ...
        ]

Note that you'll still need to enable the |autodoc| extension in order to
actually use autodoc.

To control in your code whether or not an object gets included by |autodoc|,
use the `docit` and `nodoc` wrappers on classes and functions. For instance:

    .. code:: python

        from docit import docit, nodoc

        class MyClass(object):
            
            @docit
            def __str__(self):
                \"\"\"
                This function is not normally included unless the
                ``:special-members:`` flag is set for the relevenat autodoc
                directive.

                However, by using the ``docit`` decorator, we can force it to be
                included.
                \"\"\"
                return "foo"

            @nodoc
            def frob(self):
                \"\"\"
                This function will not be included in the autodoc, because of the
                ``nodoc`` decorator on it.
                \"\"\"
                pass

        

.. seealso::

    `autodoc-skip-member`_ event
    
.. _autodoc-skip-member: http://sphinx-doc.org/ext/autodoc.html#event-autodoc-skip-member

"""


def docit(obj):
    """
    Decorator that forces a function to be documented by the |autodoc|
    extension by setting the ``docit_do`` attribute on it. This requires a
    corresponding handler function attached to the
    ``autodoc-skip-member`` event, for instance, `~docit.ext.docit_skip_member`,
    which is `setup <docit.ext.setup>` when the ``docit.ext`` extension is
    loaded in Sphinx.
    """
    obj.docit_do = True
    return obj

def nodoc(obj):
    """
    Does the opposite of `docit`, set the ``docit_do`` attribute of the given
    ``obj`` to ``False``. The `~docit.ext.docit_skip_member` function will then instruct
    Sphinx not to generate autodoc for the given object.
    """
    obj.docit_do = False
    return obj

    
