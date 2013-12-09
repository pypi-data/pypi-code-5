from __future__ import print_function, division

from sympy.core.basic import C
from sympy.core.expr import Expr
from sympy.core.relational import Eq
from sympy.core.sets import Interval
from sympy.core.singleton import S
from sympy.core.symbol import (Dummy, Wild, Symbol)
from sympy.core.sympify import sympify
from sympy.core.compatibility import is_sequence, xrange
from sympy.core.containers import Tuple
from sympy.functions.elementary.piecewise import piecewise_fold, Piecewise
from sympy.utilities import flatten




def _process_limits(*symbols):
    """Process the list of symbols and convert them to canonical limits,
    storing them as Tuple(symbol, lower, upper). The orientation of
    the function is also returned when the upper limit is missing
    so (x, 1, None) becomes (x, None, 1) and the orientation is changed.
    """
    limits = []
    orientation = 1
    for V in symbols:
        if isinstance(V, Symbol):
            limits.append(Tuple(V))
            continue
        elif is_sequence(V, Tuple):
            V = sympify(flatten(V))
            if V[0].is_Symbol:
                newsymbol = V[0]
                if len(V) == 2 and isinstance(V[1], Interval):
                    V[1:] = [V[1].start, V[1].end]

                if len(V) == 3:
                    if V[1] is None and V[2] is not None:
                        nlim = [V[2]]
                    elif V[1] is not None and V[2] is None:
                        orientation *= -1
                        nlim = [V[1]]
                    elif V[1] is None and V[2] is None:
                        nlim = []
                    else:
                        nlim = V[1:]
                    limits.append(Tuple(newsymbol, *nlim ))
                    continue
                elif len(V) == 1 or (len(V) == 2 and V[1] is None):
                    limits.append(Tuple(newsymbol))
                    continue
                elif len(V) == 2:
                    limits.append(Tuple(newsymbol, V[1]))
                    continue

        raise ValueError('Invalid limits given: %s' % str(symbols))

    return limits, orientation

class ExprWithLimits(Expr):
    __slots__ = ['is_commutative']

    def __new__(cls, function, *symbols, **assumptions):
        # Any embedded piecewise functions need to be brought out to the
        # top level so that integration can go into piecewise mode at the
        # earliest possible moment.
        function = piecewise_fold(sympify(function))

        if function is S.NaN:
            return S.NaN

        if symbols:
            limits, orientation = _process_limits(*symbols)
        else:
            # symbol not provided -- we can still try to compute a general form
            free = function.free_symbols
            if len(free) != 1:
                raise ValueError(
                    "specify dummy variables for %s" % function)
            limits, orientation = [Tuple(s) for s in free], 1

        # denest any nested calls
        while cls == type(function):
            limits = list(function.limits) + limits
            function = function.function

        # Only limits with lower and upper bounds are supported; the indefinite form
        # is not supported
        if any(len(l) != 3 or None in l for l in limits):
            raise ValueError('ExprWithLimits requires values for lower and upper bounds.')

        obj = Expr.__new__(cls, **assumptions)
        arglist = [function]
        arglist.extend(limits)
        obj._args = tuple(arglist)
        obj.is_commutative = function.is_commutative  # limits already checked

        return obj

    @property
    def function(self):
        """Return the function applied across limits.

        Examples
        ========

        >>> from sympy import Integral
        >>> from sympy.abc import x
        >>> Integral(x**2, (x,)).function
        x**2

        See Also
        ========

        limits, variables, free_symbols
        """
        return self._args[0]

    @property
    def limits(self):
        """Return the limits of expression.

        Examples
        ========

        >>> from sympy import Integral
        >>> from sympy.abc import x, i
        >>> Integral(x**i, (i, 1, 3)).limits
        ((i, 1, 3),)

        See Also
        ========

        function, variables, free_symbols
        """
        return self._args[1:]

    @property
    def variables(self):
        """Return a list of the dummy variables

        >>> from sympy import Sum
        >>> from sympy.abc import x, i
        >>> Sum(x**i, (i, 1, 3)).variables
        [i]

        See Also
        ========

        function, limits, free_symbols
        as_dummy : Rename dummy variables
        transform : Perform mapping on the dummy variable
        """
        return [l[0] for l in self.limits]

    @property
    def free_symbols(self):
        if self.function.is_zero:
            return set()
        return self._free_symbols()

    def as_dummy(self):
        """
        see _as_dummy() for documentation
        """
        return self._as_dummy()

    def _free_symbols(self):
        """
        This method returns the symbols that will exist when the object is
        evaluated. This is useful if one is trying to determine whether the
        objet contains a certain symbol or not.

        Examples
        ========

        >>> from sympy import Sum
        >>> from sympy.abc import x, y
        >>> Sum(x, (x, y, 1)).free_symbols
        set([y])
        """
        function, limits = self.function, self.limits
        if function.is_zero:
            return set()
        isyms = function.free_symbols
        for xab in limits:
            if len(xab) == 1:
                isyms.add(xab[0])
                continue
            # take out the target symbol
            if xab[0] in isyms:
                isyms.remove(xab[0])
            # add in the new symbols
            for i in xab[1:]:
                isyms.update(i.free_symbols)
        return isyms

    def _as_dummy(self):
        """
        Replace instances of the given dummy variables with explicit dummy
        counterparts to make clear what are dummy variables and what
        are real-world symbols in an object.

        Examples
        ========

        >>> from sympy import Integral
        >>> from sympy.abc import x, y
        >>> Integral(x, (x, x, y), (y, x, y)).as_dummy()
        Integral(_x, (_x, x, _y), (_y, x, y))

        If the object supperts the "integral at" limit ``(x,)`` it
        is not treated as a dummy, but the explicit form, ``(x, x)``
        of length 2 does treat the variable as a dummy.

        >>> Integral(x, x).as_dummy()
        Integral(x, x)
        >>> Integral(x, (x, x)).as_dummy()
        Integral(_x, (_x, x))

        If there were no dummies in the original expression, then the
        the symbols which cannot be changed by subs() are clearly seen as
        those with an underscore prefix.

        See Also
        ========

        variables : Lists the integration variables
        transform : Perform mapping on the integration variable
        """
        reps = {}
        f = self.function
        limits = list(self.limits)
        for i in xrange(-1, -len(limits) - 1, -1):
            xab = list(limits[i])
            if len(xab) == 1:
                continue
            x = xab[0]
            xab[0] = x.as_dummy()
            for j in range(1, len(xab)):
                xab[j] = xab[j].subs(reps)
            reps[x] = xab[0]
            limits[i] = xab
        f = f.subs(reps)
        return self.func(f, *limits)

    def _eval_subs(self, old, new):
        """
        Perform substitutions over non-dummy variables
        of an expression with limits.  Also, can be used
        to specify point-evaluation of an abstract antiderivative.

        Examples
        ========

        >>> from sympy import Sum, oo
        >>> from sympy.abc import s,n
        >>> Sum(1/n**s, (n, 1, oo)).subs(s, 2)
        Sum(n**(-2), (n, 1, oo))

        >>> from sympy import Integral
        >>> from sympy.abc import x,a
        >>> Integral(a*x**2,x).subs(x,4)
        Integral(a*x**2, (x, 4))

        See Also
        ========

        variables : Lists the integration variables
        transform : Perform mapping on the dummy variable for intgrals
        change_index : Perform mapping on the sum and product dummy variables

        """
        func, limits = self.function, list(self.limits)

        # If one of the expressions we are replacing is used as a func index
        # one of two things happens.
        #   - the old variable first appears as a free variable
        #     so we perform all free substitutions before it becomes
        #     a func index.
        #   - the old variable first appears as a func index, in
        #     which case we ignore.  See change_index.

        # Reorder limits to match standard mathematical practice for scoping
        limits.reverse()

        if not isinstance(old, C.Symbol) or \
                old.free_symbols.intersection(self.free_symbols):
            sub_into_func = True
            for i, xab in enumerate(limits):
                if 1 == len(xab) and old == xab[0]:
                    xab = (old, old)
                limits[i] = Tuple(xab[0], *[l._subs(old, new) for l in xab[1:]])
                if len(xab[0].free_symbols.intersection(old.free_symbols)) != 0:
                    sub_into_func = False
                    break
            if isinstance(old,C.AppliedUndef) or isinstance(old,C.UndefinedFunction):
                sy2 = set(self.variables).intersection(set(new.atoms(Symbol)))
                sy1 = set(self.variables).intersection(set(old.args))
                if not sy2.issubset(sy1):
                    raise ValueError(
                        "substitution can not create dummy dependencies")
                sub_into_func = True
            if sub_into_func:
                func = func.subs(old, new)
        else:
            # old is a Symbol and a dummy variable of some limit
            for i, xab in enumerate(limits):
                if len(xab) == 3:
                    limits[i] = Tuple(xab[0], *[l._subs(old, new) for l in xab[1:]])
                    if old == xab[0]:
                        break
        # simplify redundant limits (x, x)  to (x, )
        for i, xab in enumerate(limits):
            if len(xab) == 2 and (xab[0] - xab[1]).is_zero:
                limits[i] = Tuple(xab[0], )

        # Reorder limits back to representation-form
        limits.reverse()

        return self.func(func, *limits)

class AddWithLimits(ExprWithLimits):
    r"""Represents unevaluated oriented additions of integer sequences.
    """

    def __new__(cls, function, *symbols, **assumptions):
        # Any embedded piecewise functions need to be brought out to the
        # top level so that integration can go into piecewise mode at the
        # earliest possible moment.
        #
        # This constructor only differs from ExprWithLimits
        # in the application of the orientation variable.  Perhaps merge?
        function = piecewise_fold(sympify(function))

        if function is S.NaN:
            return S.NaN

        if symbols:
            limits, orientation = _process_limits(*symbols)
        else:
            # symbol not provided -- we can still try to compute a general form
            free = function.free_symbols
            if len(free) != 1:
                raise ValueError(
                    "specify dummy variables for %s" % function)
            limits, orientation = [Tuple(s) for s in free], 1

        # denest any nested calls
        while cls == type(function):
            limits = list(function.limits) + limits
            function = function.function

        obj = Expr.__new__(cls, **assumptions)
        arglist = [orientation*function]
        arglist.extend(limits)
        obj._args = tuple(arglist)
        obj.is_commutative = function.is_commutative  # limits already checked

        return obj

    def _eval_adjoint(self):
        if all([x.is_real for x in flatten(self.limits)]):
            return self.func(self.function.adjoint(), *self.limits)
        return None

    def _eval_conjugate(self):
        if all([x.is_real for x in flatten(self.limits)]):
            return self.func(self.function.conjugate(), *self.limits)
        return None

    def _eval_transpose(self):
        if all([x.is_real for x in flatten(self.limits)]):
            return self.func(self.function.transpose(), *self.limits)
        return None

    def _eval_factor(self, **hints):
        summand = self.function.factor(**hints)
        keep_inside = []
        pull_outside = []
        if summand.is_Mul and summand.is_commutative:
            for i in summand.args:
                if not i.atoms(C.Symbol).intersection(self.variables):
                    pull_outside.append(i)
                else:
                    keep_inside.append(i)
            return C.Mul(*pull_outside) * self.func(C.Mul(*keep_inside), *self.limits)
        return self

    def _eval_expand_basic(self, **hints):
        summand = self.function.expand(**hints)
        if summand.is_Add and summand.is_commutative:
            return C.Add(*[ self.func(i, *self.limits) for i in summand.args ])
        elif summand != self.function:
            return self.func(summand, *self.limits)
        return self
