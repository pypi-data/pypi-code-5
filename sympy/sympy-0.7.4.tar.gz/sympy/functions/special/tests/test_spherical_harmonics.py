from sympy import Symbol, sqrt, pi, sin, cos, cot, exp, I, S, diff, conjugate
from sympy.functions.special.spherical_harmonics import Ynm, Znm, Ynm_c
from sympy.utilities.pytest import XFAIL


def test_Ynm():
    # http://en.wikipedia.org/wiki/Spherical_harmonics
    th, ph = Symbol("theta", real=True), Symbol("phi", real=True)
    from sympy.abc import n,m

    assert Ynm(0, 0, th, ph).expand(func=True) == 1/(2*sqrt(pi))
    assert Ynm(1, -1, th, ph) == -exp(-2*I*ph)*Ynm(1, 1, th, ph)
    assert Ynm(1, -1, th, ph).expand(func=True) == sqrt(6)*sqrt(-cos(th)**2 + 1)*exp(-I*ph)/(4*sqrt(pi))
    assert Ynm(1, -1, th, ph).expand(func=True) == sqrt(6)*sqrt(-cos(th)**2 + 1)*exp(-I*ph)/(4*sqrt(pi))
    assert Ynm(1, 0, th, ph).expand(func=True) == sqrt(3)*cos(th)/(2*sqrt(pi))
    assert Ynm(1, 1, th, ph).expand(func=True) == -sqrt(6)*sqrt(-cos(th)**2 + 1)*exp(I*ph)/(4*sqrt(pi))
    assert Ynm(2, 0, th, ph).expand(func=True) == 3*sqrt(5)*cos(th)**2/(4*sqrt(pi)) - sqrt(5)/(4*sqrt(pi))
    assert Ynm(2, 1, th, ph).expand(func=True) == -sqrt(30)*sqrt(-cos(th)**2 + 1)*exp(I*ph)*cos(th)/(4*sqrt(pi))
    assert Ynm(2, -2, th, ph).expand(func=True) == (-sqrt(30)*exp(-2*I*ph)*cos(th)**2/(8*sqrt(pi))
                                                    + sqrt(30)*exp(-2*I*ph)/(8*sqrt(pi)))
    assert Ynm(2, 2, th, ph).expand(func=True) == (-sqrt(30)*exp(2*I*ph)*cos(th)**2/(8*sqrt(pi))
                                                   + sqrt(30)*exp(2*I*ph)/(8*sqrt(pi)))

    assert diff(Ynm(n, m, th, ph), th) == (m*cot(th)*Ynm(n, m, th, ph)
                                           + sqrt((-m + n)*(m + n + 1))*exp(-I*ph)*Ynm(n, m + 1, th, ph))
    assert diff(Ynm(n, m, th, ph), ph) == I*m*Ynm(n, m, th, ph)

    assert conjugate(Ynm(n, m, th, ph)) == (-1)**(2*m)*exp(-2*I*m*ph)*Ynm(n, m, th, ph)

    assert Ynm(n, m, -th, ph) == Ynm(n, m, th, ph)
    assert Ynm(n, m, th, -ph) == exp(-2*I*m*ph)*Ynm(n, m, th, ph)
    assert Ynm(n, -m, th, ph) == (-1)**m*exp(-2*I*m*ph)*Ynm(n, m, th, ph)


def test_Ynm_c():
    th, ph = Symbol("theta", real=True), Symbol("phi", real=True)
    from sympy.abc import n,m

    assert Ynm_c(n, m, th, ph) == (-1)**(2*m)*exp(-2*I*m*ph)*Ynm(n, m, th, ph)


def test_Znm():
    # http://en.wikipedia.org/wiki/Solid_harmonics#List_of_lowest_functions
    th, ph = Symbol("theta", real=True), Symbol("phi", real=True)
    from sympy.abc import n,m

    assert Znm(0, 0, th, ph) == Ynm(0, 0, th, ph)
    assert Znm(1, -1, th, ph) == (-sqrt(2)*I*(Ynm(1, 1, th, ph)
                                  - exp(-2*I*ph)*Ynm(1, 1, th, ph))/2)
    assert Znm(1, 0, th, ph) == Ynm(1, 0, th, ph)
    assert Znm(1, 1, th, ph) == (sqrt(2)*(Ynm(1, 1, th, ph)
                                 + exp(-2*I*ph)*Ynm(1, 1, th, ph))/2)
    assert Znm(0, 0, th, ph).expand(func=True) == 1/(2*sqrt(pi))
    assert Znm(1, -1, th, ph).expand(func=True) == (sqrt(3)*I*sqrt(-cos(th)**2 + 1)*exp(I*ph)/(4*sqrt(pi))
                                                    - sqrt(3)*I*sqrt(-cos(th)**2 + 1)*exp(-I*ph)/(4*sqrt(pi)))
    assert Znm(1, 0, th, ph).expand(func=True) == sqrt(3)*cos(th)/(2*sqrt(pi))
    assert Znm(1, 1, th, ph).expand(func=True) == (-sqrt(3)*sqrt(-cos(th)**2 + 1)*exp(I*ph)/(4*sqrt(pi))
                                                   - sqrt(3)*sqrt(-cos(th)**2 + 1)*exp(-I*ph)/(4*sqrt(pi)))
    assert Znm(2, -1, th, ph).expand(func=True) == (sqrt(15)*I*sqrt(-cos(th)**2 + 1)*exp(I*ph)*cos(th)/(4*sqrt(pi))
                                                    - sqrt(15)*I*sqrt(-cos(th)**2 + 1)*exp(-I*ph)*cos(th)/(4*sqrt(pi)))
    assert Znm(2, 0, th, ph).expand(func=True) == 3*sqrt(5)*cos(th)**2/(4*sqrt(pi)) - sqrt(5)/(4*sqrt(pi))
    assert Znm(2, 1, th, ph).expand(func=True) == (-sqrt(15)*sqrt(-cos(th)**2 + 1)*exp(I*ph)*cos(th)/(4*sqrt(pi))
                                                   - sqrt(15)*sqrt(-cos(th)**2 + 1)*exp(-I*ph)*cos(th)/(4*sqrt(pi)))
