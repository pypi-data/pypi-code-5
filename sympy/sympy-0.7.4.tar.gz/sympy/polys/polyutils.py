"""Useful utilities for higher level polynomial classes. """

from __future__ import print_function, division

from sympy.polys.polyerrors import PolynomialError, GeneratorsNeeded, GeneratorsError
from sympy.polys.polyoptions import build_options

from sympy.core.exprtools import decompose_power

from sympy.core import S, Add, Mul, Pow, expand_mul, expand_multinomial
from sympy.assumptions import ask, Q

from sympy.core.compatibility import xrange

import re

_gens_order = {
    'a': 301, 'b': 302, 'c': 303, 'd': 304,
    'e': 305, 'f': 306, 'g': 307, 'h': 308,
    'i': 309, 'j': 310, 'k': 311, 'l': 312,
    'm': 313, 'n': 314, 'o': 315, 'p': 216,
    'q': 217, 'r': 218, 's': 219, 't': 220,
    'u': 221, 'v': 222, 'w': 223, 'x': 124,
    'y': 125, 'z': 126,
}

_max_order = 1000
_re_gen = re.compile(r"^(.+?)(\d*)$")


def _sort_gens(gens, **args):
    """Sort generators in a reasonably intelligent way. """
    opt = build_options(args)

    gens_order, wrt = {}, None

    if opt is not None:
        gens_order, wrt = {}, opt.wrt

        for i, gen in enumerate(opt.sort):
            gens_order[gen] = i + 1

    def order_key(gen):
        gen = str(gen)

        if wrt is not None:
            try:
                return (-len(wrt) + wrt.index(gen), gen, 0)
            except ValueError:
                pass

        name, index = _re_gen.match(gen).groups()

        if index:
            index = int(index)
        else:
            index = 0

        try:
            return ( gens_order[name], name, index)
        except KeyError:
            pass

        try:
            return (_gens_order[name], name, index)
        except KeyError:
            pass

        return (_max_order, name, index)

    try:
        gens = sorted(gens, key=order_key)
    except TypeError:  # pragma: no cover
        pass

    return tuple(gens)


def _unify_gens(f_gens, g_gens):
    """Unify generators in a reasonably intelligent way. """
    f_gens = list(f_gens)
    g_gens = list(g_gens)

    if f_gens == g_gens:
        return tuple(f_gens)

    gens, common, k = [], [], 0

    for gen in f_gens:
        if gen in g_gens:
            common.append(gen)

    for i, gen in enumerate(g_gens):
        if gen in common:
            g_gens[i], k = common[k], k + 1

    for gen in common:
        i = f_gens.index(gen)

        gens.extend(f_gens[:i])
        f_gens = f_gens[i + 1:]

        i = g_gens.index(gen)

        gens.extend(g_gens[:i])
        g_gens = g_gens[i + 1:]

        gens.append(gen)

    gens.extend(f_gens)
    gens.extend(g_gens)

    return tuple(gens)


def _analyze_gens(gens):
    """Support for passing generators as `*gens` and `[gens]`. """
    if len(gens) == 1 and hasattr(gens[0], '__iter__'):
        return tuple(gens[0])
    else:
        return tuple(gens)


def _sort_factors(factors, **args):
    """Sort low-level factors in increasing 'complexity' order. """
    def order_if_multiple_key(factor):
        (f, n) = factor
        return (len(f), n, f)

    def order_no_multiple_key(f):
        return (len(f), f)

    if args.get('multiple', True):
        return sorted(factors, key=order_if_multiple_key)
    else:
        return sorted(factors, key=order_no_multiple_key)


def _not_a_coeff(expr):
    """Do not treat NaN and infinities as valid polynomial coefficients. """
    return expr in [S.NaN, S.Infinity, S.NegativeInfinity, S.ComplexInfinity]


def _parallel_dict_from_expr_if_gens(exprs, opt):
    """Transform expressions into a multinomial form given generators. """
    k, indices = len(opt.gens), {}

    for i, g in enumerate(opt.gens):
        indices[g] = i

    polys = []

    for expr in exprs:
        poly = {}

        if expr.is_Equality:
            expr = expr.lhs - expr.rhs

        for term in Add.make_args(expr):
            coeff, monom = [], [0]*k

            for factor in Mul.make_args(term):
                if not _not_a_coeff(factor) and factor.is_Number:
                    coeff.append(factor)
                else:
                    try:
                        base, exp = decompose_power(factor)

                        if exp < 0:
                            exp, base = -exp, Pow(base, -S.One)

                        monom[indices[base]] = exp
                    except KeyError:
                        if not factor.free_symbols.intersection(opt.gens):
                            coeff.append(factor)
                        else:
                            raise PolynomialError("%s contains an element of the generators set" % factor)

            monom = tuple(monom)

            if monom in poly:
                poly[monom] += Mul(*coeff)
            else:
                poly[monom] = Mul(*coeff)

        polys.append(poly)

    return polys, opt.gens


def _parallel_dict_from_expr_no_gens(exprs, opt):
    """Transform expressions into a multinomial form and figure out generators. """
    if opt.domain is not None:
        def _is_coeff(factor):
            return factor in opt.domain
    elif opt.extension is True:
        def _is_coeff(factor):
            return ask(Q.algebraic(factor))
    elif opt.greedy is not False:
        def _is_coeff(factor):
            return False
    else:
        def _is_coeff(factor):
            return factor.is_number

    gens, reprs = set([]), []

    for expr in exprs:
        terms = []

        if expr.is_Equality:
            expr = expr.lhs - expr.rhs

        for term in Add.make_args(expr):
            coeff, elements = [], {}

            for factor in Mul.make_args(term):
                if not _not_a_coeff(factor) and (factor.is_Number or _is_coeff(factor)):
                    coeff.append(factor)
                else:
                    base, exp = decompose_power(factor)

                    if exp < 0:
                        exp, base = -exp, Pow(base, -S.One)

                    elements[base] = exp
                    gens.add(base)

            terms.append((coeff, elements))

        reprs.append(terms)

    if not gens:
        if len(exprs) == 1:
            arg = exprs[0]
        else:
            arg = (exprs,)

        raise GeneratorsNeeded("specify generators to give %s a meaning" % arg)

    gens = _sort_gens(gens, opt=opt)
    k, indices = len(gens), {}

    for i, g in enumerate(gens):
        indices[g] = i

    polys = []

    for terms in reprs:
        poly = {}

        for coeff, term in terms:
            monom = [0]*k

            for base, exp in term.items():
                monom[indices[base]] = exp

            monom = tuple(monom)

            if monom in poly:
                poly[monom] += Mul(*coeff)
            else:
                poly[monom] = Mul(*coeff)

        polys.append(poly)

    return polys, tuple(gens)


def _dict_from_expr_if_gens(expr, opt):
    """Transform an expression into a multinomial form given generators. """
    (poly,), gens = _parallel_dict_from_expr_if_gens((expr,), opt)
    return poly, gens


def _dict_from_expr_no_gens(expr, opt):
    """Transform an expression into a multinomial form and figure out generators. """
    (poly,), gens = _parallel_dict_from_expr_no_gens((expr,), opt)
    return poly, gens


def parallel_dict_from_expr(exprs, **args):
    """Transform expressions into a multinomial form. """
    reps, opt = _parallel_dict_from_expr(exprs, build_options(args))
    return reps, opt.gens


def _parallel_dict_from_expr(exprs, opt):
    """Transform expressions into a multinomial form. """
    if opt.expand is not False:
        exprs = [ expr.expand() for expr in exprs ]

    if any(expr.is_commutative is False for expr in exprs):
        raise PolynomialError('non-commutative expressions are not supported')

    if opt.gens:
        reps, gens = _parallel_dict_from_expr_if_gens(exprs, opt)
    else:
        reps, gens = _parallel_dict_from_expr_no_gens(exprs, opt)

    return reps, opt.clone({'gens': gens})


def dict_from_expr(expr, **args):
    """Transform an expression into a multinomial form. """
    rep, opt = _dict_from_expr(expr, build_options(args))
    return rep, opt.gens


def _dict_from_expr(expr, opt):
    """Transform an expression into a multinomial form. """
    if expr.is_commutative is False:
        raise PolynomialError('non-commutative expressions are not supported')

    def _is_expandable_pow(expr):
        return (expr.is_Pow and expr.exp.is_positive and expr.exp.is_Integer
                and expr.base.is_Add)

    if opt.expand is not False:
        expr = expr.expand()
        # TODO: Integrate this into expand() itself
        while any(_is_expandable_pow(i) or i.is_Mul and
            any(_is_expandable_pow(j) for j in i.args) for i in
                Add.make_args(expr)):

            expr = expand_multinomial(expr)
        while any(i.is_Mul and any(j.is_Add for j in i.args) for i in Add.make_args(expr)):
            expr = expand_mul(expr)

    if opt.gens:
        rep, gens = _dict_from_expr_if_gens(expr, opt)
    else:
        rep, gens = _dict_from_expr_no_gens(expr, opt)

    return rep, opt.clone({'gens': gens})


def expr_from_dict(rep, *gens):
    """Convert a multinomial form into an expression. """
    result = []

    for monom, coeff in rep.items():
        term = [coeff]
        for g, m in zip(gens, monom):
            if m:
                term.append(Pow(g, m))

        result.append(Mul(*term))

    return Add(*result)

parallel_dict_from_basic = parallel_dict_from_expr
dict_from_basic = dict_from_expr
basic_from_dict = expr_from_dict


def _dict_reorder(rep, gens, new_gens):
    """Reorder levels using dict representation. """
    gens = list(gens)

    monoms = rep.keys()
    coeffs = rep.values()

    new_monoms = [ [] for _ in xrange(len(rep)) ]
    used_indices = set()

    for gen in new_gens:
        try:
            j = gens.index(gen)
            used_indices.add(j)

            for M, new_M in zip(monoms, new_monoms):
                new_M.append(M[j])
        except ValueError:
            for new_M in new_monoms:
                new_M.append(0)

    for i, _ in enumerate(gens):
        if i not in used_indices:
            for monom in monoms:
                if monom[i]:
                    raise GeneratorsError("unable to drop generators")

    return map(tuple, new_monoms), coeffs


class PicklableWithSlots(object):
    """
    Mixin class that allows to pickle objects with ``__slots__``.

    Examples
    --------

    First define a class that mixes :class:`PicklableWithSlots` in::

        >>> from sympy.polys.polyutils import PicklableWithSlots
        >>> class Some(PicklableWithSlots):
        ...     __slots__ = ['foo', 'bar']
        ...
        ...     def __init__(self, foo, bar):
        ...         self.foo = foo
        ...         self.bar = bar

    To make :mod:`pickle` happy in doctest we have to use this hack::

        >>> from sympy.core.compatibility import builtins
        >>> builtins.Some = Some

    Next lets see if we can create an instance, pickle it and unpickle::

        >>> some = Some('abc', 10)
        >>> some.foo, some.bar
        ('abc', 10)

        >>> from pickle import dumps, loads
        >>> some2 = loads(dumps(some))

        >>> some2.foo, some2.bar
        ('abc', 10)

    """

    __slots__ = []

    def __getstate__(self, cls=None):
        if cls is None:
            # This is the case for the instance that gets pickled
            cls = self.__class__

        d = {}

        # Get all data that should be stored from super classes
        for c in cls.__bases__:
            if hasattr(c, "__getstate__"):
                d.update(c.__getstate__(self, c))

        # Get all information that should be stored from cls and return the dict
        for name in cls.__slots__:
            if hasattr(self, name):
                d[name] = getattr(self, name)

        return d

    def __setstate__(self, d):
        # All values that were pickled are now assigned to a fresh instance
        for name, value in d.items():
            try:
                setattr(self, name, value)
            except AttributeError:    # This is needed in cases like Rational :> Half
                pass
