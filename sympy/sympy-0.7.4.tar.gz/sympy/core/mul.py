from __future__ import print_function, division

from collections import defaultdict
import operator

from sympy.core.sympify import sympify
from sympy.core.basic import Basic, C
from sympy.core.singleton import S
from sympy.core.operations import AssocOp
from sympy.core.cache import cacheit
from sympy.core.logic import fuzzy_not
from sympy.core.compatibility import cmp_to_key, reduce, xrange
from sympy.core.expr import Expr

# internal marker to indicate:
#   "there are still non-commutative objects -- don't forget to process them"


class NC_Marker:
    is_Order = False
    is_Mul = False
    is_Number = False
    is_Poly = False

    is_commutative = False


# Key for sorting commutative args in canonical order
_args_sortkey = cmp_to_key(Basic.compare)
def _mulsort(args):
    # in-place sorting of args
    args.sort(key=_args_sortkey)


def _unevaluated_Mul(*args):
    """Return a well-formed unevaluated Mul: Numbers are collected and
    put in slot 0 and args are sorted. Use this when args have changed
    but you still want to return an unevaluated Mul.

    Examples
    ========

    >>> from sympy.core.mul import _unevaluated_Mul as uMul
    >>> from sympy import S, sqrt, Mul
    >>> from sympy.abc import x
    >>> a = uMul(*[S(3.0), x, S(2)])
    >>> a.args[0]
    6.00000000000000
    >>> a.args[1]
    x

    Beyond the Number being in slot 0, there is no other flattening of
    arguments, but two unevaluated Muls with the same arguments will
    always compare as equal during testing:

    >>> m = uMul(sqrt(2), sqrt(3))
    >>> m == uMul(sqrt(3), sqrt(2))
    True
    >>> m == Mul(*m.args)
    False

    """
    args = list(args)
    newargs = []
    ncargs = []
    co = S.One
    while args:
        a = args.pop()
        if a.is_Mul:
            c, nc = a.args_cnc()
            args.extend(c)
            if nc:
                ncargs.append(Mul._from_args(nc))
        elif a.is_Number:
            co *= a
        else:
            newargs.append(a)
    _mulsort(newargs)
    if co is not S.One:
        newargs.insert(0, co)
    if ncargs:
        newargs.append(Mul._from_args(ncargs))
    return Mul._from_args(newargs)


class Mul(Expr, AssocOp):

    __slots__ = []

    is_Mul = True

    #identity = S.One
    # cyclic import, so defined in numbers.py

    @classmethod
    def flatten(cls, seq):
        """Return commutative, noncommutative and order arguments by
        combining related terms.

        Notes
        =====
            * In an expression like ``a*b*c``, python process this through sympy
              as ``Mul(Mul(a, b), c)``. This can have undesirable consequences.

              -  Sometimes terms are not combined as one would like:
                 {c.f. http://code.google.com/p/sympy/issues/detail?id=1497}

                >>> from sympy import Mul, sqrt
                >>> from sympy.abc import x, y, z
                >>> 2*(x + 1) # this is the 2-arg Mul behavior
                2*x + 2
                >>> y*(x + 1)*2
                2*y*(x + 1)
                >>> 2*(x + 1)*y # 2-arg result will be obtained first
                y*(2*x + 2)
                >>> Mul(2, x + 1, y) # all 3 args simultaneously processed
                2*y*(x + 1)
                >>> 2*((x + 1)*y) # parentheses can control this behavior
                2*y*(x + 1)

                Powers with compound bases may not find a single base to
                combine with unless all arguments are processed at once.
                Post-processing may be necessary in such cases.
                {c.f. http://code.google.com/p/sympy/issues/detail?id=2629}

                >>> a = sqrt(x*sqrt(y))
                >>> a**3
                (x*sqrt(y))**(3/2)
                >>> Mul(a,a,a)
                (x*sqrt(y))**(3/2)
                >>> a*a*a
                x*sqrt(y)*sqrt(x*sqrt(y))
                >>> _.subs(a.base, z).subs(z, a.base)
                (x*sqrt(y))**(3/2)

              -  If more than two terms are being multiplied then all the
                 previous terms will be re-processed for each new argument.
                 So if each of ``a``, ``b`` and ``c`` were :class:`Mul`
                 expression, then ``a*b*c`` (or building up the product
                 with ``*=``) will process all the arguments of ``a`` and
                 ``b`` twice: once when ``a*b`` is computed and again when
                 ``c`` is multiplied.

                 Using ``Mul(a, b, c)`` will process all arguments once.

            * The results of Mul are cached according to arguments, so flatten
              will only be called once for ``Mul(a, b, c)``. If you can
              structure a calculation so the arguments are most likely to be
              repeats then this can save time in computing the answer. For
              example, say you had a Mul, M, that you wished to divide by ``d[i]``
              and multiply by ``n[i]`` and you suspect there are many repeats
              in ``n``. It would be better to compute ``M*n[i]/d[i]`` rather
              than ``M/d[i]*n[i]`` since every time n[i] is a repeat, the
              product, ``M*n[i]`` will be returned without flattening -- the
              cached value will be returned. If you divide by the ``d[i]``
              first (and those are more unique than the ``n[i]``) then that will
              create a new Mul, ``M/d[i]`` the args of which will be traversed
              again when it is multiplied by ``n[i]``.

              {c.f. http://code.google.com/p/sympy/issues/detail?id=2607}

              This consideration is moot if the cache is turned off.

            NB
            --
              The validity of the above notes depends on the implementation
              details of Mul and flatten which may change at any time. Therefore,
              you should only consider them when your code is highly performance
              sensitive.

              Removal of 1 from the sequence is already handled by AssocOp.__new__.
        """

        rv = None
        if len(seq) == 2:
            a, b = seq
            if b.is_Rational:
                a, b = b, a
            assert not a is S.One
            if not a.is_zero and a.is_Rational:
                r, b = b.as_coeff_Mul()
                if b.is_Add:
                    if r is not S.One:  # 2-arg hack
                        # leave the Mul as a Mul
                        rv = [cls(a*r, b, evaluate=False)], [], None
                    elif b.is_commutative:
                        if a is S.One:
                            rv = [b], [], None
                        else:
                            r, b = b.as_coeff_Add()
                            bargs = [_keep_coeff(a, bi) for bi in Add.make_args(b)]
                            _addsort(bargs)
                            ar = a*r
                            if ar:
                                bargs.insert(0, ar)
                            bargs = [Add._from_args(bargs)]
                            rv = bargs, [], None
            if rv:
                return rv

        # apply associativity, separate commutative part of seq
        c_part = []         # out: commutative factors
        nc_part = []        # out: non-commutative factors

        nc_seq = []

        coeff = S.One       # standalone term
                            # e.g. 3 * ...

        c_powers = []       # (base,exp)      n
                            # e.g. (x,n) for x

        num_exp = []        # (num-base, exp)           y
                            # e.g.  (3, y)  for  ... * 3  * ...

        neg1e = S.Zero      # exponent on -1 extracted from Number-based Pow and I

        pnum_rat = {}       # (num-base, Rat-exp)          1/2
                            # e.g.  (3, 1/2)  for  ... * 3     * ...

        order_symbols = None

        # --- PART 1 ---
        #
        # "collect powers and coeff":
        #
        # o coeff
        # o c_powers
        # o num_exp
        # o neg1e
        # o pnum_rat
        #
        # NOTE: this is optimized for all-objects-are-commutative case
        for o in seq:
            # O(x)
            if o.is_Order:
                o, order_symbols = o.as_expr_variables(order_symbols)

            # Mul([...])
            if o.is_Mul:
                if o.is_commutative:
                    seq.extend(o.args)    # XXX zerocopy?

                else:
                    # NCMul can have commutative parts as well
                    for q in o.args:
                        if q.is_commutative:
                            seq.append(q)
                        else:
                            nc_seq.append(q)

                    # append non-commutative marker, so we don't forget to
                    # process scheduled non-commutative objects
                    seq.append(NC_Marker)

                continue

            # 3
            elif o.is_Number:
                if o is S.NaN or coeff is S.ComplexInfinity and o is S.Zero:
                    # we know for sure the result will be nan
                    return [S.NaN], [], None
                elif coeff.is_Number:  # it could be zoo
                    coeff *= o
                    if coeff is S.NaN:
                        # we know for sure the result will be nan
                        return [S.NaN], [], None
                continue

            elif o is S.ComplexInfinity:
                if not coeff:
                    # 0 * zoo = NaN
                    return [S.NaN], [], None
                if coeff is S.ComplexInfinity:
                    # zoo * zoo = zoo
                    return [S.ComplexInfinity], [], None
                coeff = S.ComplexInfinity
                continue

            elif o is S.ImaginaryUnit:
                neg1e += S.Half
                continue

            elif o.is_commutative:
                #      e
                # o = b
                b, e = o.as_base_exp()

                #  y
                # 3
                if o.is_Pow:
                    if b.is_Number:

                        # get all the factors with numeric base so they can be
                        # combined below, but don't combine negatives unless
                        # the exponent is an integer
                        if e.is_Rational:
                            if e.is_Integer:
                                coeff *= Pow(b, e)  # it is an unevaluated power
                                continue
                            elif e.is_negative:    # also a sign of an unevaluated power
                                seq.append(Pow(b, e))
                                continue
                            elif b.is_negative:
                                neg1e += e
                                b = -b
                            if b is not S.One:
                                pnum_rat.setdefault(b, []).append(e)
                            continue
                        elif b.is_positive or e.is_integer:
                            num_exp.append((b, e))
                            continue

                    elif b is S.ImaginaryUnit and e.is_Rational:
                        neg1e += e/2
                        continue

                c_powers.append((b, e))

            # NON-COMMUTATIVE
            # TODO: Make non-commutative exponents not combine automatically
            else:
                if o is not NC_Marker:
                    nc_seq.append(o)

                # process nc_seq (if any)
                while nc_seq:
                    o = nc_seq.pop(0)
                    if not nc_part:
                        nc_part.append(o)
                        continue

                    #                             b    c       b+c
                    # try to combine last terms: a  * a   ->  a
                    o1 = nc_part.pop()
                    b1, e1 = o1.as_base_exp()
                    b2, e2 = o.as_base_exp()
                    new_exp = e1 + e2
                    # Only allow powers to combine if the new exponent is
                    # not an Add. This allow things like a**2*b**3 == a**5
                    # if a.is_commutative == False, but prohibits
                    # a**x*a**y and x**a*x**b from combining (x,y commute).
                    if b1 == b2 and (not new_exp.is_Add):
                        o12 = b1 ** new_exp

                        # now o12 could be a commutative object
                        if o12.is_commutative:
                            seq.append(o12)
                            continue
                        else:
                            nc_seq.insert(0, o12)

                    else:
                        nc_part.append(o1)
                        nc_part.append(o)

        # We do want a combined exponent if it would not be an Add, such as
        #  y    2y     3y
        # x  * x   -> x
        # We determine if two exponents have the same term by using
        # as_coeff_Mul.
        #
        # Unfortunately, this isn't smart enough to consider combining into
        # exponents that might already be adds, so things like:
        #  z - y    y
        # x      * x  will be left alone.  This is because checking every possible
        # combination can slow things down.

        # gather exponents of common bases...
        def _gather(c_powers):
            new_c_powers = []
            common_b = {}  # b:e
            for b, e in c_powers:
                co = e.as_coeff_Mul()
                common_b.setdefault(b, {}).setdefault(co[1], []).append(co[0])
            for b, d in common_b.items():
                for di, li in d.items():
                    d[di] = Add(*li)
            for b, e in common_b.items():
                for t, c in e.items():
                    new_c_powers.append((b, c*t))
            return new_c_powers

        # in c_powers
        c_powers = _gather(c_powers)

        # and in num_exp
        num_exp = _gather(num_exp)

        # --- PART 2 ---
        #
        # o process collected powers  (x**0 -> 1; x**1 -> x; otherwise Pow)
        # o combine collected powers  (2**x * 3**x -> 6**x)
        #   with numeric base

        # ................................
        # now we have:
        # - coeff:
        # - c_powers:    (b, e)
        # - num_exp:     (2, e)
        # - pnum_rat:    {(1/3, [1/3, 2/3, 1/4])}

        #  0             1
        # x  -> 1       x  -> x
        for b, e in c_powers:
            if e is S.One:
                if b.is_Number:
                    coeff *= b
                else:
                    c_part.append(b)
            elif e is not S.Zero:
                c_part.append(Pow(b, e))

        #  x    x     x
        # 2  * 3  -> 6
        inv_exp_dict = {}   # exp:Mul(num-bases)     x    x
                            # e.g.  x:6  for  ... * 2  * 3  * ...
        for b, e in num_exp:
            inv_exp_dict.setdefault(e, []).append(b)
        for e, b in inv_exp_dict.items():
            inv_exp_dict[e] = cls(*b)
        c_part.extend([Pow(b, e) for e, b in inv_exp_dict.items() if e])

        # b, e -> e' = sum(e), b
        # {(1/5, [1/3]), (1/2, [1/12, 1/4]} -> {(1/3, [1/5, 1/2])}
        comb_e = {}
        for b, e in pnum_rat.items():
            comb_e.setdefault(Add(*e), []).append(b)
        del pnum_rat
        # process them, reducing exponents to values less than 1
        # and updating coeff if necessary else adding them to
        # num_rat for further processing
        num_rat = []
        for e, b in comb_e.items():
            b = cls(*b)
            if e.q == 1:
                coeff *= Pow(b, e)
                continue
            if e.p > e.q:
                e_i, ep = divmod(e.p, e.q)
                coeff *= Pow(b, e_i)
                e = Rational(ep, e.q)
            num_rat.append((b, e))
        del comb_e

        # extract gcd of bases in num_rat
        # 2**(1/3)*6**(1/4) -> 2**(1/3+1/4)*3**(1/4)
        pnew = defaultdict(list)
        i = 0  # steps through num_rat which may grow
        while i < len(num_rat):
            bi, ei = num_rat[i]
            grow = []
            for j in range(i + 1, len(num_rat)):
                bj, ej = num_rat[j]
                g = bi.gcd(bj)
                if g is not S.One:
                    # 4**r1*6**r2 -> 2**(r1+r2)  *  2**r1 *  3**r2
                    # this might have a gcd with something else
                    e = ei + ej
                    if e.q == 1:
                        coeff *= Pow(g, e)
                    else:
                        if e.p > e.q:
                            e_i, ep = divmod(e.p, e.q)  # change e in place
                            coeff *= Pow(g, e_i)
                            e = Rational(ep, e.q)
                        grow.append((g, e))
                    # update the jth item
                    num_rat[j] = (bj/g, ej)
                    # update bi that we are checking with
                    bi = bi/g
                    if bi is S.One:
                        break
            if bi is not S.One:
                obj = Pow(bi, ei)
                if obj.is_Number:
                    coeff *= obj
                else:
                    # changes like sqrt(12) -> 2*sqrt(3)
                    for obj in Mul.make_args(obj):
                        if obj.is_Number:
                            coeff *= obj
                        else:
                            assert obj.is_Pow
                            bi, ei = obj.args
                            pnew[ei].append(bi)

            num_rat.extend(grow)
            i += 1

        # combine bases of the new powers
        for e, b in pnew.items():
            pnew[e] = cls(*b)

        # handle -1 and I
        if neg1e:
            # treat I as (-1)**(1/2) and compute -1's total exponent
            p, q =  neg1e.as_numer_denom()
            # if the integer part is odd, extract -1
            n, p = divmod(p, q)
            if n % 2:
                coeff = -coeff
            # if it's a multiple of 1/2 extract I
            if q == 2:
                c_part.append(S.ImaginaryUnit)
            elif p:
                # see if there is any positive base this power of
                # -1 can join
                neg1e = Rational(p, q)
                for e, b in pnew.items():
                    if e == neg1e and b.is_positive:
                        pnew[e] = -b
                        break
                else:
                    # keep it separate; we've already evaluated it as
                    # much as possible so evaluate=False
                    c_part.append(Pow(S.NegativeOne, neg1e, evaluate=False))

        # add all the pnew powers
        c_part.extend([Pow(b, e) for e, b in pnew.items()])

        # oo, -oo
        if (coeff is S.Infinity) or (coeff is S.NegativeInfinity):
            def _handle_for_oo(c_part, coeff_sign):
                new_c_part = []
                for t in c_part:
                    if t.is_positive:
                        continue
                    if t.is_negative:
                        coeff_sign *= -1
                        continue
                    new_c_part.append(t)
                return new_c_part, coeff_sign
            c_part, coeff_sign = _handle_for_oo(c_part, 1)
            nc_part, coeff_sign = _handle_for_oo(nc_part, coeff_sign)
            coeff *= coeff_sign

        # zoo
        if coeff is S.ComplexInfinity:
            # zoo might be
            #   unbounded_real + bounded_im
            #   bounded_real + unbounded_im
            #   unbounded_real + unbounded_im
            # and non-zero real or imaginary will not change that status.
            c_part = [c for c in c_part if not (c.is_nonzero and
                                                c.is_real is not None)]
            nc_part = [c for c in nc_part if not (c.is_nonzero and
                                                  c.is_real is not None)]

        # 0
        elif coeff is S.Zero:
            # we know for sure the result will be 0
            return [coeff], [], order_symbols

        # order commutative part canonically
        _mulsort(c_part)

        # current code expects coeff to be always in slot-0
        if coeff is not S.One:
            c_part.insert(0, coeff)

        # we are done
        if (not nc_part and len(c_part) == 2 and c_part[0].is_Number and
                c_part[1].is_Add):
            # 2*(1+a) -> 2 + 2 * a
            coeff = c_part[0]
            c_part = [Add(*[coeff*f for f in c_part[1].args])]

        return c_part, nc_part, order_symbols

    def _eval_power(b, e):

        # don't break up NC terms: (A*B)**3 != A**3*B**3, it is A*B*A*B*A*B
        cargs, nc = b.args_cnc(split_1=False)

        if e.is_Integer:
            return Mul(*[Pow(b, e, evaluate=False) for b in cargs]) * \
                Pow(Mul._from_args(nc), e, evaluate=False)

        p = Pow(b, e, evaluate=False)

        if e.is_Rational or e.is_Float:
            return p._eval_expand_power_base()

        return p

    @classmethod
    def class_key(cls):
        return 3, 0, cls.__name__

    def _eval_evalf(self, prec):
        c, m = self.as_coeff_Mul()
        if c is S.NegativeOne:
            if m.is_Mul:
                rv = -AssocOp._eval_evalf(m, prec)
            else:
                mnew = m._eval_evalf(prec)
                if mnew is not None:
                    m = mnew
                rv = -m
        else:
            rv = AssocOp._eval_evalf(self, prec)
        if rv.is_number:
            return rv.expand()
        return rv

    @cacheit
    def as_two_terms(self):
        """Return head and tail of self.

        This is the most efficient way to get the head and tail of an
        expression.

        - if you want only the head, use self.args[0];
        - if you want to process the arguments of the tail then use
          self.as_coef_mul() which gives the head and a tuple containing
          the arguments of the tail when treated as a Mul.
        - if you want the coefficient when self is treated as an Add
          then use self.as_coeff_add()[0]

        >>> from sympy.abc import x, y
        >>> (3*x*y).as_two_terms()
        (3, x*y)
        """
        args = self.args

        if len(args) == 1:
            return S.One, self
        elif len(args) == 2:
            return args

        else:
            return args[0], self._new_rawargs(*args[1:])

    @cacheit
    def as_coeff_mul(self, *deps):
        if deps:
            l1 = []
            l2 = []
            for f in self.args:
                if f.has(*deps):
                    l2.append(f)
                else:
                    l1.append(f)
            return self._new_rawargs(*l1), tuple(l2)
        args = self.args
        if args[0].is_Rational:
            return args[0], args[1:]
        elif args[0] is S.NegativeInfinity:
            return S.NegativeOne, (-args[0],) + args[1:]
        return S.One, args

    def as_coeff_Mul(self, rational=False):
        """Efficiently extract the coefficient of a product. """
        coeff, args = self.args[0], self.args[1:]

        if coeff.is_Number and not (rational and not coeff.is_Rational):
            if len(args) == 1:
                return coeff, args[0]
            else:
                return coeff, self._new_rawargs(*args)
        else:
            return S.One, self

    def as_real_imag(self, deep=True, **hints):
        from sympy import expand_mul
        other = []
        coeff = S.One
        addterms = S.One
        for a in self.args:
            if a.is_real or a.is_imaginary:
                coeff *= a
            elif a.is_commutative:
                # search for complex conjugate pairs:
                for i, x in enumerate(other):
                    if x == a.conjugate():
                        coeff *= C.Abs(x)**2
                        del other[i]
                        break
                else:
                    if a.is_Add:
                        addterms *= a
                    else:
                        other.append(a)
            else:
                other.append(a)
        addre, addim = expand_mul(addterms, deep=False).as_real_imag()
        m = self.func(*other)
        if hints.get('ignore') == m:
            return None
        else:
            if coeff.is_real:
                return (coeff*(C.re(m)*addre - C.im(m)*addim), coeff*(C.im(m)*addre + C.re(m)*addim))
            else:
                re = - C.im(coeff)*C.im(m)
                im = C.im(coeff)*C.re(m)
                return (re*addre - im*addim, re*addim + im*addre)

    @staticmethod
    def _expandsums(sums):
        """
        Helper function for _eval_expand_mul.

        sums must be a list of instances of Basic.
        """

        L = len(sums)
        if L == 1:
            return sums[0].args
        terms = []
        left = Mul._expandsums(sums[:L//2])
        right = Mul._expandsums(sums[L//2:])

        terms = [Mul(a, b) for a in left for b in right]
        added = Add(*terms)
        return Add.make_args(added)  # it may have collapsed down to one term

    def _eval_expand_mul(self, **hints):
        from sympy import fraction

        # Handle things like 1/(x*(x + 1)), which are automatically converted
        # to 1/x*1/(x + 1)
        expr = self
        n, d = fraction(expr)
        if d.is_Mul:
            n, d = [i._eval_expand_mul(**hints) if i.is_Mul else i
                for i in (n, d)]
            expr = n/d
            if not expr.is_Mul:
                return expr

        plain, sums, rewrite = [], [], False
        for factor in expr.args:
            if factor.is_Add:
                sums.append(factor)
                rewrite = True
            else:
                if factor.is_commutative:
                    plain.append(factor)
                else:
                    sums.append(Basic(factor))  # Wrapper

        if not rewrite:
            return expr
        else:
            plain = self.func(*plain)
            if sums:
                terms = self.func._expandsums(sums)
                args = []
                for term in terms:
                    t = self.func(plain, term)
                    if t.is_Mul and any(a.is_Add for a in t.args):
                        t = t._eval_expand_mul()
                    args.append(t)
                return Add(*args)
            else:
                return plain

    def _eval_derivative(self, s):
        terms = list(self.args)
        factors = []
        for i in xrange(len(terms)):
            t = terms[i].diff(s)
            if t is S.Zero:
                continue
            factors.append(self.func(*(terms[:i] + [t] + terms[i + 1:])))
        return Add(*factors)

    def _matches_simple(self, expr, repl_dict):
        # handle (w*3).matches('x*5') -> {w: x*5/3}
        coeff, terms = self.as_coeff_Mul()
        terms = Mul.make_args(terms)
        if len(terms) == 1:
            newexpr = self.__class__._combine_inverse(expr, coeff)
            return terms[0].matches(newexpr, repl_dict)
        return

    def matches(self, expr, repl_dict={}, old=False):
        expr = sympify(expr)
        if self.is_commutative and expr.is_commutative:
            return AssocOp._matches_commutative(self, expr, repl_dict, old)
        elif self.is_commutative is not expr.is_commutative:
            return None
        c1, nc1 = self.args_cnc()
        c2, nc2 = expr.args_cnc()
        repl_dict = repl_dict.copy()
        if c1:
            if not c2:
                c2 = [1]
            a = self.func(*c1)
            if isinstance(a, AssocOp):
                repl_dict = a._matches_commutative(self.func(*c2), repl_dict, old)
            else:
                repl_dict = a.matches(self.func(*c2), repl_dict)
        if repl_dict:
            a = self.func(*nc1)
            if isinstance(a, self.func):
                repl_dict = a._matches(self.func(*nc2), repl_dict)
            else:
                repl_dict = a.matches(self.func(*nc2), repl_dict)
        return repl_dict or None

    def _matches(self, expr, repl_dict={}):
        # weed out negative one prefixes
        sign = 1
        a, b = self.as_two_terms()
        if a is S.NegativeOne:
            if b.is_Mul:
                sign = -sign
            else:
                # the remainder, b, is not a Mul anymore
                return b.matches(-expr, repl_dict)
        expr = sympify(expr)
        if expr.is_Mul and expr.args[0] is S.NegativeOne:
            expr = -expr
            sign = -sign

        if not expr.is_Mul:
            # expr can only match if it matches b and a matches +/- 1
            if len(self.args) == 2:
                # quickly test for equality
                if b == expr:
                    return a.matches(Rational(sign), repl_dict)
                # do more expensive match
                dd = b.matches(expr, repl_dict)
                if dd is None:
                    return None
                dd = a.matches(Rational(sign), dd)
                return dd
            return None

        d = repl_dict.copy()

        # weed out identical terms
        pp = list(self.args)
        ee = list(expr.args)
        for p in self.args:
            if p in expr.args:
                ee.remove(p)
                pp.remove(p)

        # only one symbol left in pattern -> match the remaining expression
        if len(pp) == 1 and isinstance(pp[0], C.Wild):
            if len(ee) == 1:
                d[pp[0]] = sign * ee[0]
            else:
                d[pp[0]] = sign * expr.func(*ee)
            return d

        if len(ee) != len(pp):
            return None

        for p, e in zip(pp, ee):
            d = p.xreplace(d).matches(e, d)
            if d is None:
                return None
        return d

    @staticmethod
    def _combine_inverse(lhs, rhs):
        """
        Returns lhs/rhs, but treats arguments like symbols, so things like
        oo/oo return 1, instead of a nan.
        """
        if lhs == rhs:
            return S.One

        def check(l, r):
            if l.is_Float and r.is_comparable:
                # if both objects are added to 0 they will share the same "normalization"
                # and are more likely to compare the same. Since Add(foo, 0) will not allow
                # the 0 to pass, we use __add__ directly.
                return l.__add__(0) == r.evalf().__add__(0)
            return False
        if check(lhs, rhs) or check(rhs, lhs):
            return S.One
        if lhs.is_Mul and rhs.is_Mul:
            a = list(lhs.args)
            b = [1]
            for x in rhs.args:
                if x in a:
                    a.remove(x)
                elif -x in a:
                    a.remove(-x)
                    b.append(-1)
                else:
                    b.append(x)
            return lhs.func(*a)/rhs.func(*b)
        return lhs/rhs

    def as_powers_dict(self):
        d = defaultdict(int)
        for term in self.args:
            b, e = term.as_base_exp()
            d[b] += e
        return d

    def as_numer_denom(self):
        # don't use _from_args to rebuild the numerators and denominators
        # as the order is not guaranteed to be the same once they have
        # been separated from each other
        numers, denoms = list(zip(*[f.as_numer_denom() for f in self.args]))
        return self.func(*numers), self.func(*denoms)

    def as_base_exp(self):
        e1 = None
        bases = []
        nc = 0
        for m in self.args:
            b, e = m.as_base_exp()
            if not b.is_commutative:
                nc += 1
            if e1 is None:
                e1 = e
            elif e != e1 or nc > 1:
                return self, S.One
            bases.append(b)
        return self.func(*bases), e1

    def _eval_is_polynomial(self, syms):
        return all(term._eval_is_polynomial(syms) for term in self.args)

    def _eval_is_rational_function(self, syms):
        return all(term._eval_is_rational_function(syms) for term in self.args)

    def _eval_is_algebraic_expr(self, syms):
        return all(term._eval_is_algebraic_expr(syms) for term in self.args)

    _eval_is_bounded = lambda self: self._eval_template_is_attr('is_bounded')
    _eval_is_commutative = lambda self: self._eval_template_is_attr(
        'is_commutative')
    _eval_is_rational = lambda self: self._eval_template_is_attr('is_rational',
        when_multiple=None)

    def _eval_is_integer(self):
        is_rational = self.is_rational

        if is_rational:
            n, d = self.as_numer_denom()
            if d is S.One:
                return True
            elif d is S(2):
                return n.is_even
        elif is_rational is False:
            return False

    def _eval_is_polar(self):
        has_polar = any(arg.is_polar for arg in self.args)
        return has_polar and \
            all(arg.is_polar or arg.is_positive for arg in self.args)

    # I*I -> R,  I*I*I -> -I
    def _eval_is_real(self):
        im_count = 0
        is_neither = False
        for t in self.args:
            if t.is_imaginary:
                im_count += 1
                continue
            t_real = t.is_real
            if t_real:
                continue
            elif t_real is False:
                if is_neither:
                    return None
                else:
                    is_neither = True
            else:
                return None
        if is_neither:
            return False

        return (im_count % 2 == 0)

    def _eval_is_imaginary(self):
        im_count = 0
        is_neither = False
        for t in self.args:
            if t.is_imaginary:
                im_count += 1
                continue
            t_real = t.is_real
            if t_real:
                continue
            elif t_real is False:
                if is_neither:
                    return None
                else:
                    is_neither = True
            else:
                return None
        if is_neither:
            return False

        return (im_count % 2 == 1)

    def _eval_is_hermitian(self):
        nc_count = 0
        im_count = 0
        is_neither = False
        for t in self.args:
            if not t.is_commutative:
                nc_count += 1
                if nc_count > 1:
                    return None
            if t.is_antihermitian:
                im_count += 1
                continue
            t_real = t.is_hermitian
            if t_real:
                continue
            elif t_real is False:
                if is_neither:
                    return None
                else:
                    is_neither = True
            else:
                return None
        if is_neither:
            return False

        return (im_count % 2 == 0)

    def _eval_is_antihermitian(self):
        nc_count = 0
        im_count = 0
        is_neither = False
        for t in self.args:
            if not t.is_commutative:
                nc_count += 1
                if nc_count > 1:
                    return None
            if t.is_antihermitian:
                im_count += 1
                continue
            t_real = t.is_hermitian
            if t_real:
                continue
            elif t_real is False:
                if is_neither:
                    return None
                else:
                    is_neither = True
            else:
                return None
        if is_neither:
            return False

        return (im_count % 2 == 1)

    def _eval_is_irrational(self):
        for t in self.args:
            a = t.is_irrational
            if a:
                others = list(self.args)
                others.remove(t)
                if all(x.is_rational is True for x in others):
                    return True
                return None
            if a is None:
                return
        return False

    def _eval_is_zero(self):
        zero = None
        for a in self.args:
            if a.is_zero:
                zero = True
                continue
            bound = a.is_bounded
            if not bound:
                return bound
        if zero:
            return True

    def _eval_is_positive(self):
        """Return True if self is positive, False if not, and None if it
        cannot be determined.

        This algorithm is non-recursive and works by keeping track of the
        sign which changes when a negative or nonpositive is encountered.
        Whether a nonpositive or nonnegative is seen is also tracked since
        the presence of these makes it impossible to return True, but
        possible to return False if the end result is nonpositive. e.g.

            pos * neg * nonpositive -> pos or zero -> None is returned
            pos * neg * nonnegative -> neg or zero -> False is returned
        """

        sign = 1
        saw_NON = False
        for t in self.args:
            if t.is_positive:
                continue
            elif t.is_negative:
                sign = -sign
            elif t.is_zero:
                return False
            elif t.is_nonpositive:
                sign = -sign
                saw_NON = True
            elif t.is_nonnegative:
                saw_NON = True
            else:
                return
        if sign == 1 and saw_NON is False:
            return True
        if sign < 0:
            return False

    def _eval_is_negative(self):
        """Return True if self is negative, False if not, and None if it
        cannot be determined.

        This algorithm is non-recursive and works by keeping track of the
        sign which changes when a negative or nonpositive is encountered.
        Whether a nonpositive or nonnegative is seen is also tracked since
        the presence of these makes it impossible to return True, but
        possible to return False if the end result is nonnegative. e.g.

            pos * neg * nonpositive -> pos or zero -> False is returned
            pos * neg * nonnegative -> neg or zero -> None is returned
        """

        sign = 1
        saw_NON = False
        for t in self.args:
            if t.is_positive:
                continue
            elif t.is_negative:
                sign = -sign
            elif t.is_zero:
                return False
            elif t.is_nonpositive:
                sign = -sign
                saw_NON = True
            elif t.is_nonnegative:
                saw_NON = True
            else:
                return
        if sign == -1 and saw_NON is False:
            return True
        if sign > 0:
            return False

    def _eval_is_odd(self):
        is_integer = self.is_integer

        if is_integer:
            r, acc = True, 1
            for t in self.args:
                if not t.is_integer:
                    return None
                elif t.is_even:
                    r = False
                elif t.is_integer:
                    if r is False:
                        pass
                    elif acc != 1 and (acc + t).is_odd:
                        r = False
                    elif t.is_odd is None:
                        r = None
                acc = t
            return r

        # !integer -> !odd
        elif is_integer is False:
            return False

    def _eval_is_even(self):
        is_integer = self.is_integer

        if is_integer:
            return fuzzy_not(self._eval_is_odd())

        elif is_integer is False:
            return False

    def _eval_subs(self, old, new):
        from sympy.functions.elementary.complexes import sign
        from sympy.ntheory.factor_ import multiplicity
        from sympy.simplify.simplify import powdenest, fraction

        if not old.is_Mul:
            return None

        # try keep replacement literal so -2*x doesn't replace 4*x
        if old.args[0].is_Number and old.args[0] < 0:
            if self.args[0].is_Number:
                if self.args[0] < 0:
                    return self._subs(-old, -new)
                return None

        def base_exp(a):
            # if I and -1 are in a Mul, they get both end up with
            # a -1 base (see issue 3322); all we want here are the
            # true Pow or exp separated into base and exponent
            if a.is_Pow or a.func is C.exp:
                return a.as_base_exp()
            return a, S.One

        def breakup(eq):
            """break up powers of eq when treated as a Mul:
                   b**(Rational*e) -> b**e, Rational
                commutatives come back as a dictionary {b**e: Rational}
                noncommutatives come back as a list [(b**e, Rational)]
            """

            (c, nc) = (defaultdict(int), list())
            for a in Mul.make_args(eq):
                a = powdenest(a)
                (b, e) = base_exp(a)
                if e is not S.One:
                    (co, _) = e.as_coeff_mul()
                    b = Pow(b, e/co)
                    e = co
                if a.is_commutative:
                    c[b] += e
                else:
                    nc.append([b, e])
            return (c, nc)

        def rejoin(b, co):
            """
            Put rational back with exponent; in general this is not ok, but
            since we took it from the exponent for analysis, it's ok to put
            it back.
            """

            (b, e) = base_exp(b)
            return Pow(b, e*co)

        def ndiv(a, b):
            """if b divides a in an extractive way (like 1/4 divides 1/2
            but not vice versa, and 2/5 does not divide 1/3) then return
            the integer number of times it divides, else return 0.
            """
            if not b.q % a.q or not a.q % b.q:
                return int(a/b)
            return 0

        # give Muls in the denominator a chance to be changed (see issue 2552)
        # rv will be the default return value
        rv = None
        n, d = fraction(self)
        if d is not S.One:
            self2 = n._subs(old, new)/d._subs(old, new)
            if not self2.is_Mul:
                return self2._subs(old, new)
            if self2 != self:
                self = rv = self2

        # Now continue with regular substitution.

        # handle the leading coefficient and use it to decide if anything
        # should even be started; we always know where to find the Rational
        # so it's a quick test

        co_self = self.args[0]
        co_old = old.args[0]
        co_xmul = None
        if co_old.is_Rational and co_self.is_Rational:
            # if coeffs are the same there will be no updating to do
            # below after breakup() step; so skip (and keep co_xmul=None)
            if co_old != co_self:
                co_xmul = co_self.extract_multiplicatively(co_old)
        elif co_old.is_Rational:
            return rv

        # break self and old into factors

        (c, nc) = breakup(self)
        (old_c, old_nc) = breakup(old)

        # update the coefficients if we had an extraction
        # e.g. if co_self were 2*(3/35*x)**2 and co_old = 3/5
        # then co_self in c is replaced by (3/5)**2 and co_residual
        # is 2*(1/7)**2

        if co_xmul and co_xmul.is_Rational and abs(co_old) != 1:
            mult = S(multiplicity(abs(co_old), co_self))
            c.pop(co_self)
            if co_old in c:
                c[co_old] += mult
            else:
                c[co_old] = mult
            co_residual = co_self/co_old**mult
        else:
            co_residual = 1

        # do quick tests to see if we can't succeed

        ok = True
        if len(old_nc) > len(nc):
            # more non-commutative terms
            ok = False
        elif len(old_c) > len(c):
            # more commutative terms
            ok = False
        elif set(i[0] for i in old_nc).difference(set(i[0] for i in nc)):
            # unmatched non-commutative bases
            ok = False
        elif set(old_c).difference(set(c)):
            # unmatched commutative terms
            ok = False
        elif any(sign(c[b]) != sign(old_c[b]) for b in old_c):
            # differences in sign
            ok = False
        if not ok:
            return rv

        if not old_c:
            cdid = None
        else:
            rat = []
            for (b, old_e) in old_c.items():
                c_e = c[b]
                rat.append(ndiv(c_e, old_e))
                if not rat[-1]:
                    return rv
            cdid = min(rat)

        if not old_nc:
            ncdid = None
            for i in range(len(nc)):
                nc[i] = rejoin(*nc[i])
        else:
            ncdid = 0  # number of nc replacements we did
            take = len(old_nc)  # how much to look at each time
            limit = cdid or S.Infinity  # max number that we can take
            failed = []  # failed terms will need subs if other terms pass
            i = 0
            while limit and i + take <= len(nc):
                hit = False

                # the bases must be equivalent in succession, and
                # the powers must be extractively compatible on the
                # first and last factor but equal inbetween.

                rat = []
                for j in range(take):
                    if nc[i + j][0] != old_nc[j][0]:
                        break
                    elif j == 0:
                        rat.append(ndiv(nc[i + j][1], old_nc[j][1]))
                    elif j == take - 1:
                        rat.append(ndiv(nc[i + j][1], old_nc[j][1]))
                    elif nc[i + j][1] != old_nc[j][1]:
                        break
                    else:
                        rat.append(1)
                    j += 1
                else:
                    ndo = min(rat)
                    if ndo:
                        if take == 1:
                            if cdid:
                                ndo = min(cdid, ndo)
                            nc[i] = Pow(new, ndo)*rejoin(nc[i][0],
                                    nc[i][1] - ndo*old_nc[0][1])
                        else:
                            ndo = 1

                            # the left residual

                            l = rejoin(nc[i][0], nc[i][1] - ndo*
                                    old_nc[0][1])

                            # eliminate all middle terms

                            mid = new

                            # the right residual (which may be the same as the middle if take == 2)

                            ir = i + take - 1
                            r = (nc[ir][0], nc[ir][1] - ndo*
                                 old_nc[-1][1])
                            if r[1]:
                                if i + take < len(nc):
                                    nc[i:i + take] = [l*mid, r]
                                else:
                                    r = rejoin(*r)
                                    nc[i:i + take] = [l*mid*r]
                            else:

                                # there was nothing left on the right

                                nc[i:i + take] = [l*mid]

                        limit -= ndo
                        ncdid += ndo
                        hit = True
                if not hit:

                    # do the subs on this failing factor

                    failed.append(i)
                i += 1
            else:

                if not ncdid:
                    return rv

                # although we didn't fail, certain nc terms may have
                # failed so we rebuild them after attempting a partial
                # subs on them

                failed.extend(range(i, len(nc)))
                for i in failed:
                    nc[i] = rejoin(*nc[i]).subs(old, new)

        # rebuild the expression

        if cdid is None:
            do = ncdid
        elif ncdid is None:
            do = cdid
        else:
            do = min(ncdid, cdid)

        margs = []
        for b in c:
            if b in old_c:

                # calculate the new exponent

                e = c[b] - old_c[b]*do
                margs.append(rejoin(b, e))
            else:
                margs.append(rejoin(b.subs(old, new), c[b]))
        if cdid and not ncdid:

            # in case we are replacing commutative with non-commutative,
            # we want the new term to come at the front just like the
            # rest of this routine

            margs = [Pow(new, cdid)] + margs
        return co_residual*self.func(*margs)*self.func(*nc)

    def _eval_nseries(self, x, n, logx):
        from sympy import powsimp
        terms = [t.nseries(x, n=n, logx=logx) for t in self.args]
        res = powsimp(self.func(*terms).expand(), combine='exp', deep=True)
        if res.has(C.Order):
            res += C.Order(x**n, x)
        return res

    def _eval_as_leading_term(self, x):
        return self.func(*[t.as_leading_term(x) for t in self.args])

    def _eval_conjugate(self):
        return self.func(*[t.conjugate() for t in self.args])

    def _eval_transpose(self):
        return self.func(*[t.transpose() for t in self.args[::-1]])

    def _eval_adjoint(self):
        return self.func(*[t.adjoint() for t in self.args[::-1]])

    def _sage_(self):
        s = 1
        for x in self.args:
            s *= x._sage_()
        return s

    def as_content_primitive(self, radical=False):
        """Return the tuple (R, self/R) where R is the positive Rational
        extracted from self.

        Examples
        ========

        >>> from sympy import sqrt
        >>> (-3*sqrt(2)*(2 - 2*sqrt(2))).as_content_primitive()
        (6, -sqrt(2)*(-sqrt(2) + 1))

        See docstring of Expr.as_content_primitive for more examples.
        """

        coef = S.One
        args = []
        for i, a in enumerate(self.args):
            c, p = a.as_content_primitive(radical=radical)
            coef *= c
            if p is not S.One:
                args.append(p)
        # don't use self._from_args here to reconstruct args
        # since there may be identical args now that should be combined
        # e.g. (2+2*x)*(3+3*x) should be (6, (1 + x)**2) not (6, (1+x)*(1+x))
        return coef, self.func(*args)

    def as_ordered_factors(self, order=None):
        """Transform an expression into an ordered list of factors.

        Examples
        ========

        >>> from sympy import sin, cos
        >>> from sympy.abc import x, y

        >>> (2*x*y*sin(x)*cos(x)).as_ordered_factors()
        [2, x, y, sin(x), cos(x)]

        """
        cpart, ncpart = self.args_cnc()
        cpart.sort(key=lambda expr: expr.sort_key(order=order))
        return cpart + ncpart

    @property
    def _sorted_args(self):
        return self.as_ordered_factors()


def prod(a, start=1):
    """Return product of elements of a. Start with int 1 so if only
       ints are included then an int result is returned.

    Examples
    ========

    >>> from sympy import prod, S
    >>> prod(range(3))
    0
    >>> type(_) is int
    True
    >>> prod([S(2), 3])
    6
    >>> _.is_Integer
    True

    You can start the product at something other than 1:
    >>> prod([1, 2], 3)
    6

    """
    return reduce(operator.mul, a, start)


def _keep_coeff(coeff, factors, clear=True, sign=False):
    """Return ``coeff*factors`` unevaluated if necessary.

    If ``clear`` is False, do not keep the coefficient as a factor
    if it can be distributed on a single factor such that one or
    more terms will still have integer coefficients.

    If ``sign`` is True, allow a coefficient of -1 to remain factored out.

    Examples
    ========

    >>> from sympy.core.mul import _keep_coeff
    >>> from sympy.abc import x, y
    >>> from sympy import S

    >>> _keep_coeff(S.Half, x + 2)
    (x + 2)/2
    >>> _keep_coeff(S.Half, x + 2, clear=False)
    x/2 + 1
    >>> _keep_coeff(S.Half, (x + 2)*y, clear=False)
    y*(x + 2)/2
    >>> _keep_coeff(S(-1), x + y)
    -x - y
    >>> _keep_coeff(S(-1), x + y, sign=True)
    -(x + y)
    """

    if not coeff.is_Number:
        if factors.is_Number:
            factors, coeff = coeff, factors
        else:
            return coeff*factors
    if coeff is S.One:
        return factors
    elif coeff is S.NegativeOne and not sign:
        return -factors
    elif factors.is_Add:
        if not clear and coeff.is_Rational and coeff.q != 1:
            q = S(coeff.q)
            for i in factors.args:
                c, t = i.as_coeff_Mul()
                r = c/q
                if r == int(r):
                    return coeff*factors
        return Mul._from_args((coeff, factors))
    elif factors.is_Mul:
        margs = list(factors.args)
        if margs[0].is_Number:
            margs[0] *= coeff
            if margs[0] == 1:
                margs.pop(0)
        else:
            margs.insert(0, coeff)
        return Mul._from_args(margs)
    else:
        return coeff*factors


def expand_2arg(e):
    from sympy.simplify.simplify import bottom_up
    def do(e):
        if e.is_Mul:
            c, r = e.as_coeff_Mul()
            if c.is_Number and r.is_Add:
                return _unevaluated_Add(*[c*ri for ri in r.args])
        return e
    return bottom_up(e, do)


from .numbers import Rational
from .power import Pow
from .add import Add, _addsort, _unevaluated_Add
