"""
This module provides convenient functions to transform sympy expressions to
lambda functions which can be used to calculate numerical values very fast.
"""

from __future__ import print_function, division

from sympy.external import import_module
from sympy.core.compatibility import exec_, is_sequence, iterable, string_types

import inspect

# These are the namespaces the lambda functions will use.
MATH = {}
MPMATH = {}
NUMPY = {}
SYMPY = {}

# Default namespaces, letting us define translations that can't be defined
# by simple variable maps, like I => 1j
# These are separate from the names above because the above names are modified
# throughout this file, whereas these should remain unmodified.
MATH_DEFAULT = {}
MPMATH_DEFAULT = {}
NUMPY_DEFAULT = {"I": 1j}
SYMPY_DEFAULT = {}

# Mappings between sympy and other modules function names.
MATH_TRANSLATIONS = {
    "Abs": "fabs",
    "ceiling": "ceil",
    "E": "e",
    "ln": "log",
}

MPMATH_TRANSLATIONS = {
    "elliptic_k": "ellipk",
    "elliptic_f": "ellipf",
    "elliptic_e": "ellipe",
    "elliptic_pi": "ellippi",
    "ceiling": "ceil",
    "chebyshevt": "chebyt",
    "chebyshevu": "chebyu",
    "E": "e",
    "I": "j",
    "ln": "log",
    #"lowergamma":"lower_gamma",
    "oo": "inf",
    #"uppergamma":"upper_gamma",
    "LambertW": "lambertw",
    "Matrix": "matrix",
    "MutableDenseMatrix": "matrix",
    "ImmutableMatrix": "matrix",
    "conjugate": "conj",
    "dirichlet_eta": "altzeta",
    "Ei": "ei",
    "Shi": "shi",
    "Chi": "chi",
    "Si": "si",
    "Ci": "ci"
}

NUMPY_TRANSLATIONS = {
    "Abs": "abs",
    "acos": "arccos",
    "acosh": "arccosh",
    "arg": "angle",
    "asin": "arcsin",
    "asinh": "arcsinh",
    "atan": "arctan",
    "atan2": "arctan2",
    "atanh": "arctanh",
    "ceiling": "ceil",
    "E": "e",
    "im": "imag",
    "ln": "log",
    "Matrix": "matrix",
    "MutableDenseMatrix": "matrix",
    "ImmutableMatrix": "matrix",
    "Max": "amax",
    "Min": "amin",
    "oo": "inf",
    "re": "real",
}

# Available modules:
MODULES = {
    "math": (MATH, MATH_DEFAULT, MATH_TRANSLATIONS, ("from math import *",)),
    "mpmath": (MPMATH, MPMATH_DEFAULT, MPMATH_TRANSLATIONS, ("from sympy.mpmath import *",)),
    "numpy": (NUMPY, NUMPY_DEFAULT, NUMPY_TRANSLATIONS, ("import_module('numpy')",)),
    "sympy": (SYMPY, SYMPY_DEFAULT, {}, (
        "from sympy.functions import *",
        "from sympy.matrices import *",
        "from sympy import Integral, pi, oo, nan, zoo, E, I",)),
}


def _import(module, reload="False"):
    """
    Creates a global translation dictionary for module.

    The argument module has to be one of the following strings: "math",
    "mpmath", "numpy", "sympy".
    These dictionaries map names of python functions to their equivalent in
    other modules.
    """
    try:
        namespace, namespace_default, translations, import_commands = MODULES[
            module]
    except KeyError:
        raise NameError(
            "'%s' module can't be used for lambdification" % module)

    # Clear namespace or exit
    if namespace != namespace_default:
        # The namespace was already generated, don't do it again if not forced.
        if reload:
            namespace.clear()
            namespace.update(namespace_default)
        else:
            return

    for import_command in import_commands:
        if import_command.startswith('import_module'):
            module = eval(import_command)

            if module is not None:
                namespace.update(module.__dict__)
                continue
        else:
            try:
                exec_(import_command, {}, namespace)
                continue
            except ImportError:
                pass

        raise ImportError(
            "can't import '%s' with '%s' command" % (module, import_command))

    # Add translated names to namespace
    for sympyname, translation in translations.items():
        namespace[sympyname] = namespace[translation]


def lambdify(args, expr, modules=None, printer=None, use_imps=True):
    """
    Returns a lambda function for fast calculation of numerical values.

    If not specified differently by the user, SymPy functions are replaced as
    far as possible by either python-math, numpy (if available) or mpmath
    functions - exactly in this order. To change this behavior, the "modules"
    argument can be used. It accepts:

     - the strings "math", "mpmath", "numpy", "sympy"
     - any modules (e.g. math)
     - dictionaries that map names of sympy functions to arbitrary functions
     - lists that contain a mix of the arguments above, with higher priority
       given to entries appearing first.

    The default behavior is to substitute all arguments in the provided
    expression with dummy symbols. This allows for applied functions (e.g.
    f(t)) to be supplied as arguments. Call the function with dummify=False if
    dummy substitution is unwanted.
    If you want to view the lambdified function or provide "sympy" as the
    module, you should probably set dummify=False.

    Usage
    =====

    (1) Use one of the provided modules:

        >> f = lambdify(x, sin(x), "math")

        Attention: Functions that are not in the math module will throw a name
                   error when the lambda function is evaluated! So this would
                   be better:

        >> f = lambdify(x, sin(x)*gamma(x), ("math", "mpmath", "sympy"))

    (2) Use some other module:

        >> import numpy
        >> f = lambdify((x,y), tan(x*y), numpy)

        Attention: There are naming differences between numpy and sympy. So if
                   you simply take the numpy module, e.g. sympy.atan will not be
                   translated to numpy.arctan. Use the modified module instead
                   by passing the string "numpy":

        >> f = lambdify((x,y), tan(x*y), "numpy")
        >> f(1, 2)
        -2.18503986326
        >> from numpy import array
        >> f(array([1, 2, 3]), array([2, 3, 5]))
        [-2.18503986 -0.29100619 -0.8559934 ]

    (3) Use own dictionaries:

        >> def my_cool_function(x): ...
        >> dic = {"sin" : my_cool_function}
        >> f = lambdify(x, sin(x), dic)

        Now f would look like:

        >> lambda x: my_cool_function(x)

    Examples
    ========

    >>> from sympy.utilities.lambdify import implemented_function, lambdify
    >>> from sympy import sqrt, sin, Matrix
    >>> from sympy import Function
    >>> from sympy.abc import x, y, z

    >>> f = lambdify(x, x**2)
    >>> f(2)
    4
    >>> f = lambdify((x, y, z), [z, y, x])
    >>> f(1,2,3)
    [3, 2, 1]
    >>> f = lambdify(x, sqrt(x))
    >>> f(4)
    2.0
    >>> f = lambdify((x, y), sin(x*y)**2)
    >>> f(0, 5)
    0.0
    >>> f = lambdify((x, y), Matrix((x, x + y)).T, modules='sympy')
    >>> f(1, 2)
    Matrix([[1, 3]])

    Functions present in `expr` can also carry their own numerical
    implementations, in a callable attached to the ``_imp_``
    attribute.  Usually you attach this using the
    ``implemented_function`` factory:

    >>> f = implemented_function(Function('f'), lambda x: x+1)
    >>> func = lambdify(x, f(x))
    >>> func(4)
    5

    ``lambdify`` always prefers ``_imp_`` implementations to implementations
    in other namespaces, unless the ``use_imps`` input parameter is False.
    """
    from sympy.core.symbol import Symbol

    # If the user hasn't specified any modules, use what is available.
    module_provided = True
    if modules is None:
        module_provided = False
        # Use either numpy (if available) or python.math where possible.
        # XXX: This leads to different behaviour on different systems and
        #      might be the reason for irreproducible errors.
        modules = ["math", "mpmath", "sympy"]

        try:
            _import("numpy")
        except ImportError:
            pass
        else:
            modules.insert(1, "numpy")


    # Get the needed namespaces.
    namespaces = []
    # First find any function implementations
    if use_imps:
        namespaces.append(_imp_namespace(expr))
    # Check for dict before iterating
    if isinstance(modules, (dict, str)) or not hasattr(modules, '__iter__'):
        namespaces.append(modules)
    else:
        namespaces += list(modules)
    # fill namespace with first having highest priority
    namespace = {}
    for m in namespaces[::-1]:
        buf = _get_namespace(m)
        namespace.update(buf)

    if hasattr(expr, "atoms"):
        #Try if you can extract symbols from the expression.
        #Move on if expr.atoms in not implemented.
        syms = expr.atoms(Symbol)
        for term in syms:
            namespace.update({str(term): term})

    # Create lambda function.
    lstr = lambdastr(args, expr, printer=printer, dummify=True)
    return eval(lstr, namespace)


def _get_namespace(m):
    """
    This is used by _lambdify to parse its arguments.
    """
    if isinstance(m, str):
        _import(m)
        return MODULES[m][0]
    elif isinstance(m, dict):
        return m
    elif hasattr(m, "__dict__"):
        return m.__dict__
    else:
        raise TypeError("Argument must be either a string, dict or module but it is: %s" % m)


def lambdastr(args, expr, printer=None, dummify=False):
    """
    Returns a string that can be evaluated to a lambda function.

    >>> from sympy.abc import x, y, z
    >>> from sympy.utilities.lambdify import lambdastr
    >>> lambdastr(x, x**2)
    'lambda x: (x**2)'
    >>> lambdastr((x,y,z), [z,y,x])
    'lambda x,y,z: ([z, y, x])'

    """
    # Transforming everything to strings.
    from sympy.matrices import DeferredVector
    from sympy import Dummy, sympify, Symbol, Function

    if printer is not None:
        if inspect.isfunction(printer):
            lambdarepr = printer
        else:
            if inspect.isclass(printer):
                lambdarepr = lambda expr: printer().doprint(expr)
            else:
                lambdarepr = lambda expr: printer.doprint(expr)
    else:
        #XXX: This has to be done here because of circular imports
        from sympy.printing.lambdarepr import lambdarepr

    def sub_args(args, dummies_dict):
        if isinstance(args, str):
            return args
        elif isinstance(args, DeferredVector):
            return str(args)
        elif iterable(args):
            flatten = lambda *n: (e for a in n for e in
                                  (flatten(*a) if iterable(a) else (a,)))
            dummies = flatten([sub_args(a, dummies_dict) for a in args])
            return ",".join(str(a) for a in dummies)
        else:
            if isinstance(args, Function):
                dummies = Dummy()
                dummies_dict.update({args : dummies})
                return str(dummies)
            else:
                return str(args)

    def sub_expr(expr, dummies_dict):
        try:
            expr = sympify(expr).xreplace(dummies_dict)
        except:
            if isinstance(expr, DeferredVector):
                pass
            elif isinstance(expr, dict):
                k = [sub_expr(sympify(a), dummies_dict) for a in expr.keys()]
                v = [sub_expr(sympify(a), dummies_dict) for a in expr.values()]
                expr = dict(zip(k, v))
            elif isinstance(expr, tuple):
                expr = tuple(sub_expr(sympify(a), dummies_dict) for a in expr)
            elif isinstance(expr, list):
                expr = [sub_expr(sympify(a), dummies_dict) for a in expr]
        return expr

    # Transform args
    dummies_dict = {}
    if dummify:
        args = sub_args(args, dummies_dict)
    else:
        if isinstance(args, str):
            pass
        elif iterable(args, exclude=DeferredVector):
            args = ",".join(str(a) for a in args)

    # Transform expr
    if dummify:
        if isinstance(expr, str):
            pass
        else:
            expr = sub_expr(expr, dummies_dict)
    expr = lambdarepr(expr)

    return "lambda %s: (%s)" % (args, expr)


def _imp_namespace(expr, namespace=None):
    """ Return namespace dict with function implementations

    We need to search for functions in anything that can be thrown at
    us - that is - anything that could be passed as `expr`.  Examples
    include sympy expressions, as well as tuples, lists and dicts that may
    contain sympy expressions.

    Parameters
    ----------
    expr : object
       Something passed to lambdify, that will generate valid code from
       ``str(expr)``.
    namespace : None or mapping
       Namespace to fill.  None results in new empty dict

    Returns
    -------
    namespace : dict
       dict with keys of implemented function names within `expr` and
       corresponding values being the numerical implementation of
       function

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.utilities.lambdify import implemented_function, _imp_namespace
    >>> from sympy import Function
    >>> f = implemented_function(Function('f'), lambda x: x+1)
    >>> g = implemented_function(Function('g'), lambda x: x*10)
    >>> namespace = _imp_namespace(f(g(x)))
    >>> sorted(namespace.keys())
    ['f', 'g']
    """
    # Delayed import to avoid circular imports
    from sympy.core.function import FunctionClass
    if namespace is None:
        namespace = {}
    # tuples, lists, dicts are valid expressions
    if is_sequence(expr):
        for arg in expr:
            _imp_namespace(arg, namespace)
        return namespace
    elif isinstance(expr, dict):
        for key, val in expr.items():
            # functions can be in dictionary keys
            _imp_namespace(key, namespace)
            _imp_namespace(val, namespace)
        return namespace
    # sympy expressions may be Functions themselves
    func = getattr(expr, 'func', None)
    if isinstance(func, FunctionClass):
        imp = getattr(func, '_imp_', None)
        if imp is not None:
            name = expr.func.__name__
            if name in namespace and namespace[name] != imp:
                raise ValueError('We found more than one '
                                 'implementation with name '
                                 '"%s"' % name)
            namespace[name] = imp
    # and / or they may take Functions as arguments
    if hasattr(expr, 'args'):
        for arg in expr.args:
            _imp_namespace(arg, namespace)
    return namespace


def implemented_function(symfunc, implementation):
    """ Add numerical ``implementation`` to function ``symfunc``.

    ``symfunc`` can be an ``UndefinedFunction`` instance, or a name string.
    In the latter case we create an ``UndefinedFunction`` instance with that
    name.

    Be aware that this is a quick workaround, not a general method to create
    special symbolic functions. If you want to create a symbolic function to be
    used by all the machinery of sympy you should subclass the ``Function``
    class.

    Parameters
    ----------
    symfunc : ``str`` or ``UndefinedFunction`` instance
       If ``str``, then create new ``UndefinedFunction`` with this as
       name.  If `symfunc` is a sympy function, attach implementation to it.
    implementation : callable
       numerical implementation to be called by ``evalf()`` or ``lambdify``

    Returns
    -------
    afunc : sympy.FunctionClass instance
       function with attached implementation

    Examples
    --------
    >>> from sympy.abc import x
    >>> from sympy.utilities.lambdify import lambdify, implemented_function
    >>> from sympy import Function
    >>> f = implemented_function(Function('f'), lambda x: x+1)
    >>> lam_f = lambdify(x, f(x))
    >>> lam_f(4)
    5
    """
    # Delayed import to avoid circular imports
    from sympy.core.function import UndefinedFunction
    # if name, create function to hold implementation
    if isinstance(symfunc, string_types):
        symfunc = UndefinedFunction(symfunc)
    elif not isinstance(symfunc, UndefinedFunction):
        raise ValueError('symfunc should be either a string or'
                         ' an UndefinedFunction instance.')
    # We need to attach as a method because symfunc will be a class
    symfunc._imp_ = staticmethod(implementation)
    return symfunc
