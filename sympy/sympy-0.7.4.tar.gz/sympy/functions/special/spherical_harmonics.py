from __future__ import print_function, division

from sympy import pi, I
from sympy.core.basic import C
from sympy.core.singleton import S
from sympy.core import Dummy, sympify
from sympy.core.function import Function, ArgumentIndexError
from sympy.functions import assoc_legendre
from sympy.functions.elementary.trigonometric import sin, cos
from sympy.functions.elementary.complexes import Abs
from sympy.functions.elementary.miscellaneous import sqrt

_x = Dummy("x")

class Ynm(Function):
    r"""
    Spherical harmonics defined as

    .. math::
        Y_n^m(\theta, \varphi) := \sqrt{\frac{(2n+1)(n-m)!}{4\pi(n+m)!}}
                                  \exp(i m \varphi)
                                  \mathrm{P}_n^m\left(\cos(\theta)\right)

    Ynm() gives the spherical harmonic function of order `n` and `m`
    in `\theta` and `\varphi`, `Y_n^m(\theta, \varphi)`. The four
    parameters are as follows: `n \geq 0` an integer and `m` an integer
    such that `-n \leq m \leq n` holds. The two angles are real-valued
    with `\theta \in [0, \pi]` and `\varphi \in [0, 2\pi]`.

    Examples
    ========

    >>> from sympy import Ynm, Symbol
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> Ynm(n, m, theta, phi)
    Ynm(n, m, theta, phi)

    Several symmetries are known, for the order

    >>> from sympy import Ynm, Symbol
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> Ynm(n, -m, theta, phi)
    (-1)**m*exp(-2*I*m*phi)*Ynm(n, m, theta, phi)

    as well as for the angles

    >>> from sympy import Ynm, Symbol, simplify
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> Ynm(n, m, -theta, phi)
    Ynm(n, m, theta, phi)

    >>> Ynm(n, m, theta, -phi)
    exp(-2*I*m*phi)*Ynm(n, m, theta, phi)

    For specific integers n and m we can evalute the harmonics
    to more useful expressions

    >>> simplify(Ynm(0, 0, theta, phi).expand(func=True))
    1/(2*sqrt(pi))

    >>> simplify(Ynm(1, -1, theta, phi).expand(func=True))
    sqrt(6)*exp(-I*phi)*sin(theta)/(4*sqrt(pi))

    >>> simplify(Ynm(1, 0, theta, phi).expand(func=True))
    sqrt(3)*cos(theta)/(2*sqrt(pi))

    >>> simplify(Ynm(1, 1, theta, phi).expand(func=True))
    -sqrt(6)*exp(I*phi)*sin(theta)/(4*sqrt(pi))

    >>> simplify(Ynm(2, -2, theta, phi).expand(func=True))
    sqrt(30)*exp(-2*I*phi)*sin(theta)**2/(8*sqrt(pi))

    >>> simplify(Ynm(2, -1, theta, phi).expand(func=True))
    sqrt(30)*exp(-I*phi)*sin(2*theta)/(8*sqrt(pi))

    >>> simplify(Ynm(2, 0, theta, phi).expand(func=True))
    sqrt(5)*(3*cos(theta)**2 - 1)/(4*sqrt(pi))

    >>> simplify(Ynm(2, 1, theta, phi).expand(func=True))
    -sqrt(30)*exp(I*phi)*sin(2*theta)/(8*sqrt(pi))

    >>> simplify(Ynm(2, 2, theta, phi).expand(func=True))
    sqrt(30)*exp(2*I*phi)*sin(theta)**2/(8*sqrt(pi))

    We can differentiate the functions with respect
    to both angles

    >>> from sympy import Ynm, Symbol, diff
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> diff(Ynm(n, m, theta, phi), theta)
    m*cot(theta)*Ynm(n, m, theta, phi) + sqrt((-m + n)*(m + n + 1))*exp(-I*phi)*Ynm(n, m + 1, theta, phi)

    >>> diff(Ynm(n, m, theta, phi), phi)
    I*m*Ynm(n, m, theta, phi)

    Further we can compute the complex conjugation

    >>> from sympy import Ynm, Symbol, conjugate
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> conjugate(Ynm(n, m, theta, phi))
    (-1)**(2*m)*exp(-2*I*m*phi)*Ynm(n, m, theta, phi)

    To get back the well known expressions in spherical
    coordinates we use full expansion

    >>> from sympy import Ynm, Symbol, expand_func
    >>> from sympy.abc import n,m
    >>> theta = Symbol("theta")
    >>> phi = Symbol("phi")

    >>> expand_func(Ynm(n, m, theta, phi))
    sqrt((2*n + 1)*factorial(-m + n)/factorial(m + n))*exp(I*m*phi)*assoc_legendre(n, m, cos(theta))/(2*sqrt(pi))

    See Also
    ========

    Ynm_c, Znm

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Spherical_harmonics
    .. [2] http://mathworld.wolfram.com/SphericalHarmonic.html
    .. [3] http://functions.wolfram.com/Polynomials/SphericalHarmonicY/
    .. [4] http://dlmf.nist.gov/14.30
    """

    nargs = 4

    @classmethod
    def eval(cls, n, m, theta, phi):
        n, m, theta, phi = [sympify(x) for x in (n, m, theta, phi)]

        # Handle negative index m and arguments theta, phi
        if m.could_extract_minus_sign():
            m = -m
            return S.NegativeOne**m * C.exp(-2*I*m*phi) * Ynm(n, m, theta, phi)
        if theta.could_extract_minus_sign():
            theta = -theta
            return Ynm(n, m, theta, phi)
        if phi.could_extract_minus_sign():
            phi = -phi
            return C.exp(-2*I*m*phi) * Ynm(n, m, theta, phi)

        # TODO Add more simplififcation here

    def _eval_expand_func(self, **hints):
        n, m, theta, phi = self.args
        return (sqrt((2*n + 1)/(4*pi) * C.factorial(n - m)/C.factorial(n + m)) *
                C.exp(I*m*phi) * assoc_legendre(n, m, C.cos(theta)))

    def fdiff(self, argindex=4):
        if argindex == 1:
            # Diff wrt n
            raise ArgumentIndexError(self, argindex)
        elif argindex == 2:
            # Diff wrt m
            raise ArgumentIndexError(self, argindex)
        elif argindex == 3:
            # Diff wrt theta
            n, m, theta, phi = self.args
            return (m * C.cot(theta) * Ynm(n, m, theta, phi) +
                    sqrt((n - m)*(n + m + 1)) * C.exp(-I*phi) * Ynm(n, m + 1, theta, phi))
        elif argindex == 4:
            # Diff wrt phi
            n, m, theta, phi = self.args
            return I * m * Ynm(n, m, theta, phi)
        else:
            raise ArgumentIndexError(self, argindex)

    def _eval_rewrite_as_polynomial(self, n, m, theta, phi):
        # TODO: Make sure n \in N
        # TODO: Assert |m| <= n ortherwise we should return 0
        return self.expand(func=True)

    def _eval_rewrite_as_sin(self, n, m, theta, phi):
        return self.rewrite(cos)

    def _eval_rewrite_as_cos(self, n, m, theta, phi):
        # This method can be expensive due to extensive use of simplification!
        from sympy.simplify import simplify, trigsimp
        # TODO: Make sure n \in N
        # TODO: Assert |m| <= n ortherwise we should return 0
        term = simplify(self.expand(func=True))
        # We can do this because of the range of theta
        term = term.xreplace({Abs(sin(theta)):sin(theta)})
        return simplify(trigsimp(term))

    def _eval_conjugate(self):
        # TODO: Make sure theta \in R and phi \in R
        n, m, theta, phi = self.args
        return S.NegativeOne**m * self.func(n, -m, theta, phi)

    def as_real_imag(self, deep=True, **hints):
        # TODO: Handle deep and hints
        n, m, theta, phi = self.args
        re = (sqrt((2*n + 1)/(4*pi) * C.factorial(n - m)/C.factorial(n + m)) *
              C.cos(m*phi) * assoc_legendre(n, m, C.cos(theta)))
        im = (sqrt((2*n + 1)/(4*pi) * C.factorial(n - m)/C.factorial(n + m)) *
              C.sin(m*phi) * assoc_legendre(n, m, C.cos(theta)))
        return (re, im)

    def _eval_evalf(self, prec):
        # Note: works without this function by just calling
        #       mpmath for Legendre polynomials. But using
        #       the dedicated function directly is cleaner.
        from sympy.mpmath import mp
        from sympy import Expr
        n = self.args[0]._to_mpmath(prec)
        m = self.args[1]._to_mpmath(prec)
        theta = self.args[2]._to_mpmath(prec)
        phi = self.args[3]._to_mpmath(prec)
        oprec = mp.prec
        mp.prec = prec
        res = mp.spherharm(n, m, theta, phi)
        mp.prec = oprec
        return Expr._from_mpmath(res, prec)


def Ynm_c(n, m, theta, phi):
    r"""Conjugate spherical harmonics defined as

    .. math::
        \overline{Y_n^m(\theta, \varphi)} := (-1)^m Y_n^{-m}(\theta, \varphi)

    See Also
    ========

    Ynm, Znm

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Spherical_harmonics
    .. [2] http://mathworld.wolfram.com/SphericalHarmonic.html
    .. [3] http://functions.wolfram.com/Polynomials/SphericalHarmonicY/
    """
    from sympy import conjugate
    return conjugate(Ynm(n, m, theta, phi))


class Znm(Function):
    r"""
    Real spherical harmonics defined as

    .. math::

        Z_n^m(\theta, \varphi) :=
        \begin{cases}
          \frac{Y_n^m(\theta, \varphi) + \overline{Y_n^m(\theta, \varphi)}}{\sqrt{2}} &\quad m > 0 \\
          Y_n^m(\theta, \varphi) &\quad m = 0 \\
          \frac{Y_n^m(\theta, \varphi) - \overline{Y_n^m(\theta, \varphi)}}{i \sqrt{2}} &\quad m < 0 \\
        \end{cases}

    which gives in simplified form

    .. math::

        Z_n^m(\theta, \varphi) =
        \begin{cases}
          \frac{Y_n^m(\theta, \varphi) + (-1)^m Y_n^{-m}(\theta, \varphi)}{\sqrt{2}} &\quad m > 0 \\
          Y_n^m(\theta, \varphi) &\quad m = 0 \\
          \frac{Y_n^m(\theta, \varphi) - (-1)^m Y_n^{-m}(\theta, \varphi)}{i \sqrt{2}} &\quad m < 0 \\
        \end{cases}

    See Also
    ========

    Ynm, Ynm_c

    References
    ==========

    .. [1] http://en.wikipedia.org/wiki/Spherical_harmonics
    .. [2] http://mathworld.wolfram.com/SphericalHarmonic.html
    .. [3] http://functions.wolfram.com/Polynomials/SphericalHarmonicY/
    """

    nargs = 4

    @classmethod
    def eval(cls, n, m, theta, phi):
        n, m, th, ph = [sympify(x) for x in (n, m, theta, phi)]

        if m.is_positive:
            zz = (Ynm(n, m, th, ph) + Ynm_c(n, m, th, ph)) / sqrt(2)
            #zz = zz.expand(complex=True)
            #zz = simplify(zz)
            return zz
        elif m.is_zero:
            return Ynm(n, m, th, ph)
        elif m.is_negative:
            zz = (Ynm(n, m, th, ph) - Ynm_c(n, m, th, ph)) / (sqrt(2)*I)
            #zz = zz.expand(complex=True)
            #zz = simplify(zz)
            return zz
