#! /usr/bin/env python
# vim: set fileencoding=utf-8: 

"""
This is the actual |SPHINX| extension. Enable it in your
`conf.py <http://sphinx-doc.org/config.html>`_
by putting ``'docit.ext'`` in your ``extensions`` list.
"""

event_listener__autodoc_skip_member = None
"""
The sphinx "listener ID" this extension uses to listen to the 
|autodoc-skip-member| event. This is set when `setup` is called by |SPHINX|,
and the `docit_skip_member` handler is connected to the event with
`~sphinx:sphinx.application.Sphinx.connect`. If for some reason you want to 
remove the handler, you can use sphinx'
`~sphinx:sphinx.application.Sphinx.disconnect` method, but then the ``docit``
extension won't work any more.
"""

def setup(app):
    """
    Called by |SPHINX| when the this module is loaded as an extension. This
    connects the `docit_skip_member` function to the |autodoc-skip-member|
    event.
    """
    event_listener__autodoc_skip_member = app.connect('autodoc-skip-member', docit_skip_member)


def docit_skip_member(app, what, name, obj, skip, options):
    """
    A handler function that can be attached to the |SPHINX| ``autodoc-skip-memeber``
    event, which will handle the special flag added to functions by the
    `docit` and `nodoc` decorator.

    If the given `obj` has a ``docit_do`` attribute and the attribute's value
    evaluates as true, then the function returns ``False``, indicating it should
    _not_ be skipped (i.e., documentation should be generated for it).
    
    If it has the ``docit_do`` attribute and it evaluates to false, then the
    function returns ``True``, indicating the the object should be skipped.
    
    Otherwise,
    returns ``None``, indicating that we don't know wether or not to include it,
    and Sphinx will have to use another means to decide. Normally, this means it
    uses autodoc's built-in decision making based on the flags and configuration.
    """
    if hasattr(obj, 'docit_do'):
        return not obj.docit_do
    return None


