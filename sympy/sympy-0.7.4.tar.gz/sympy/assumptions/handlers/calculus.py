"""
This module contains query handlers responsible for calculus queries:
infinitesimal, bounded, etc.
"""
from __future__ import print_function, division

from sympy.logic.boolalg import conjuncts
from sympy.assumptions import Q, ask
from sympy.assumptions.handlers import CommonHandler


class AskInfinitesimalHandler(CommonHandler):
    """
    Handler for key 'infinitesimal'
    Test that a given expression is equivalent to an infinitesimal
    number
    """

    @staticmethod
    def _number(expr, assumptions):
        # helper method
        return expr.evalf() == 0

    @staticmethod
    def Basic(expr, assumptions):
        if expr.is_number:
            return AskInfinitesimalHandler._number(expr, assumptions)

    @staticmethod
    def Mul(expr, assumptions):
        """
        Infinitesimal*Bounded -> Infinitesimal
        """
        if expr.is_number:
            return AskInfinitesimalHandler._number(expr, assumptions)
        result = False
        for arg in expr.args:
            if ask(Q.infinitesimal(arg), assumptions):
                result = True
            elif ask(Q.bounded(arg), assumptions):
                continue
            else:
                break
        else:
            return result

    Add, Pow = [Mul]*2

    @staticmethod
    def Number(expr, assumptions):
        return expr == 0

    NumberSymbol = Number

    ImaginaryUnit = staticmethod(CommonHandler.AlwaysFalse)


class AskBoundedHandler(CommonHandler):
    """
    Handler for key 'bounded'.

    Test that an expression is bounded respect to all its variables.

    Examples of usage:

    >>> from sympy import Symbol, Q
    >>> from sympy.assumptions.handlers.calculus import AskBoundedHandler
    >>> from sympy.abc import x
    >>> a = AskBoundedHandler()
    >>> a.Symbol(x, Q.positive(x)) == None
    True
    >>> a.Symbol(x, Q.bounded(x))
    True

    """

    @staticmethod
    def Symbol(expr, assumptions):
        """
        Handles Symbol.

        Examples:

        >>> from sympy import Symbol, Q
        >>> from sympy.assumptions.handlers.calculus import AskBoundedHandler
        >>> from sympy.abc import x
        >>> a = AskBoundedHandler()
        >>> a.Symbol(x, Q.positive(x)) == None
        True
        >>> a.Symbol(x, Q.bounded(x))
        True

        """
        if Q.bounded(expr) in conjuncts(assumptions):
            return True
        return None

    @staticmethod
    def Add(expr, assumptions):
        """
        Return True if expr is bounded, False if not and None if unknown.

        Truth Table:

        +-------+-----+-----------+-----------+
        |       |     |           |           |
        |       |  B  |     U     |     ?     |
        |       |     |           |           |
        +-------+-----+---+---+---+---+---+---+
        |       |     |   |   |   |   |   |   |
        |       |     |'+'|'-'|'x'|'+'|'-'|'x'|
        |       |     |   |   |   |   |   |   |
        +-------+-----+---+---+---+---+---+---+
        |       |     |           |           |
        |   B   |  B  |     U     |     ?     |
        |       |     |           |           |
        +---+---+-----+---+---+---+---+---+---+
        |   |   |     |   |   |   |   |   |   |
        |   |'+'|     | U | ? | ? | U | ? | ? |
        |   |   |     |   |   |   |   |   |   |
        |   +---+-----+---+---+---+---+---+---+
        |   |   |     |   |   |   |   |   |   |
        | U |'-'|     | ? | U | ? | ? | U | ? |
        |   |   |     |   |   |   |   |   |   |
        |   +---+-----+---+---+---+---+---+---+
        |   |   |     |           |           |
        |   |'x'|     |     ?     |     ?     |
        |   |   |     |           |           |
        +---+---+-----+---+---+---+---+---+---+
        |       |     |           |           |
        |   ?   |     |           |     ?     |
        |       |     |           |           |
        +-------+-----+-----------+---+---+---+

            * 'B' = Bounded

            * 'U' = Unbounded

            * '?' = unknown boundedness

            * '+' = positive sign

            * '-' = negative sign

            * 'x' = sign unknown

|

            * All Bounded -> True

            * 1 Unbounded and the rest Bounded -> False

            * >1 Unbounded, all with same known sign -> False

            * Any Unknown and unknown sign -> None

            * Else -> None

        When the signs are not the same you can have an undefined
        result as in oo - oo, hence 'bounded' is also undefined.

        """

        sign = -1  # sign of unknown or unbounded
        result = True
        for arg in expr.args:
            _bounded = ask(Q.bounded(arg), assumptions)
            if _bounded:
                continue
            s = ask(Q.positive(arg), assumptions)
            # if there has been more than one sign or if the sign of this arg
            # is None and Bounded is None or there was already
            # an unknown sign, return None
            if sign != -1 and s != sign or \
                    s is None and (s == _bounded or s == sign):
                return None
            else:
                sign = s
            # once False, do not change
            if result is not False:
                result = _bounded
        return result

    @staticmethod
    def Mul(expr, assumptions):
        """
        Return True if expr is bounded, False if not and None if unknown.

        Truth Table:

        +---+---+---+--------+
        |   |   |   |        |
        |   | B | U |   ?    |
        |   |   |   |        |
        +---+---+---+---+----+
        |   |   |   |   |    |
        |   |   |   | s | /s |
        |   |   |   |   |    |
        +---+---+---+---+----+
        |   |   |   |        |
        | B | B | U |   ?    |
        |   |   |   |        |
        +---+---+---+---+----+
        |   |   |   |   |    |
        | U |   | U | U | ?  |
        |   |   |   |   |    |
        +---+---+---+---+----+
        |   |   |   |        |
        | ? |   |   |   ?    |
        |   |   |   |        |
        +---+---+---+---+----+

            * B = Bounded

            * U = Unbounded

            * ? = unknown boundedness

            * s = signed (hence nonzero)

            * /s = not signed

        """
        result = True
        for arg in expr.args:
            _bounded = ask(Q.bounded(arg), assumptions)
            if _bounded:
                continue
            elif _bounded is None:
                if result is None:
                    return None
                if ask(Q.nonzero(arg), assumptions) is None:
                    return None
                if result is not False:
                    result = None
            else:
                result = False
        return result

    @staticmethod
    def Pow(expr, assumptions):
        """
        Unbounded ** NonZero -> Unbounded
        Bounded ** Bounded -> Bounded
        Abs()<=1 ** Positive -> Bounded
        Abs()>=1 ** Negative -> Bounded
        Otherwise unknown
        """
        base_bounded = ask(Q.bounded(expr.base), assumptions)
        exp_bounded = ask(Q.bounded(expr.exp), assumptions)
        if base_bounded is None and exp_bounded is None:  # Common Case
            return None
        if base_bounded is False and ask(Q.nonzero(expr.exp), assumptions):
            return False
        if base_bounded and exp_bounded:
            return True
        if (abs(expr.base) <= 1) is True and ask(Q.positive(expr.exp), assumptions):
            return True
        if (abs(expr.base) >= 1) is True and ask(Q.negative(expr.exp), assumptions):
            return True
        if (abs(expr.base) >= 1) is True and exp_bounded is False:
            return False
        return None

    @staticmethod
    def log(expr, assumptions):
        return ask(Q.bounded(expr.args[0]), assumptions)

    exp = log

    cos, sin, Number, Pi, Exp1, GoldenRatio, ImaginaryUnit, sign = \
        [staticmethod(CommonHandler.AlwaysTrue)]*8

    Infinity, NegativeInfinity = [staticmethod(CommonHandler.AlwaysFalse)]*2
