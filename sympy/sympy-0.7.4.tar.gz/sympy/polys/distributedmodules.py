r"""
Sparse distributed elements of free modules over multivariate (generalized)
polynomial rings.

This code and its data structures are very much like the distributed
polynomials, except that the first "exponent" of the monomial is
a module generator index. That is, the multi-exponent ``(i, e_1, ..., e_n)``
represents the "monomial" `x_1^{e_1} \dots x_n^{e_n} f_i` of the free module
`F` generated by `f_1, \dots, f_r` over (a localization of) the ring
`K[x_1, \dots, x_n]`. A module element is simply stored as a list of terms
ordered by the monomial order. Here a term is a pair of a multi-exponent and a
coefficient. In general, this coefficient should never be zero (since it can
then be omitted). The zero module element is stored as an empty list.

The main routines are ``sdm_nf_mora`` and ``sdm_groebner`` which can be used
to compute, respectively, weak normal forms and standard bases. They work with
arbitrary (not necessarily global) monomial orders.

In general, product orders have to be used to construct valid monomial orders
for modules. However, ``lex`` can be used as-is.

Note that the "level" (number of variables, i.e. parameter u+1 in
distributedpolys.py) is never needed in this code.

The main reference for this file is [SCA],
"A Singular Introduction to Commutative Algebra".
"""

from __future__ import print_function, division

from itertools import permutations

from sympy.polys.monomials import (
    monomial_mul, monomial_lcm, monomial_div, monomial_deg, monomial_divides
)

from sympy.polys.polytools import Poly
from sympy.polys.polyutils import parallel_dict_from_expr
from sympy import S, sympify

# Additional monomial tools.


def sdm_monomial_mul(M, X):
    """
    Multiply tuple ``X`` representing a monomial of `K[X]` into the tuple
    ``M`` representing a monomial of `F`.

    Examples
    ========

    Multiplying `xy^3` into `x f_1` yields `x^2 y^3 f_1`:

    >>> from sympy.polys.distributedmodules import sdm_monomial_mul
    >>> sdm_monomial_mul((1, 1, 0), (1, 3))
    (1, 2, 3)
    """
    return (M[0],) + monomial_mul(X, M[1:])


def sdm_monomial_deg(M):
    """
    Return the total degree of ``M``.

    Examples
    ========

    For example, the total degree of `x^2 y f_5` is 3:

    >>> from sympy.polys.distributedmodules import sdm_monomial_deg
    >>> sdm_monomial_deg((5, 2, 1))
    3
    """
    return monomial_deg(M[1:])


def sdm_monomial_lcm(A, B):
    """
    Return the "least common multiple" of ``A`` and ``B``.

    IF `A = M e_j` and `B = N e_j`, where `M` and `N` are polynomial monomials,
    this returns `\lcm(M, N) e_j`. Note that ``A`` and ``B`` involve distinct
    monomials.

    Otherwise the result is undefined.

    >>> from sympy.polys.distributedmodules import sdm_monomial_lcm
    >>> sdm_monomial_lcm((1, 2, 3), (1, 0, 5))
    (1, 2, 5)
    """
    return (A[0],) + monomial_lcm(A[1:], B[1:])


def sdm_monomial_divides(A, B):
    """
    Does there exist a (polynomial) monomial X such that XA = B?

    Examples
    ========

    Positive examples:

    In the following examples, the monomial is given in terms of x, y and the
    generator(s), f_1, f_2 etc. The tuple form of that monomial is used in
    the call to sdm_monomial_divides.
    Note: the generator appears last in the expression but first in the tuple
    and other factors appear in the same order that they appear in the monomial
    expression.

    `A = f_1` divides `B = f_1`

    >>> from sympy.polys.distributedmodules import sdm_monomial_divides
    >>> sdm_monomial_divides((1, 0, 0), (1, 0, 0))
    True

    `A = f_1` divides `B = x^2 y f_1`

    >>> sdm_monomial_divides((1, 0, 0), (1, 2, 1))
    True

    `A = xy f_5` divides `B = x^2 y f_5`

    >>> sdm_monomial_divides((5, 1, 1), (5, 2, 1))
    True

    Negative examples:

    `A = f_1` does not divide `B = f_2`

    >>> sdm_monomial_divides((1, 0, 0), (2, 0, 0))
    False

    `A = x f_1` does not divide `B = f_1`

    >>> sdm_monomial_divides((1, 1, 0), (1, 0, 0))
    False

    `A = xy^2 f_5` does not divide `B = y f_5`

    >>> sdm_monomial_divides((5, 1, 2), (5, 0, 1))
    False
    """
    return A[0] == B[0] and all(a <= b for a, b in zip(A[1:], B[1:]))


# The actual distributed modules code.

def sdm_LC(f, K):
    """Returns the leading coeffcient of ``f``. """
    if not f:
        return K.zero
    else:
        return f[0][1]


def sdm_to_dict(f):
    """Make a dictionary from a distributed polynomial. """
    return dict(f)


def sdm_from_dict(d, O):
    """
    Create an sdm from a dictionary.

    Here ``O`` is the monomial order to use.

    >>> from sympy.polys.distributedmodules import sdm_from_dict
    >>> from sympy.polys import QQ, lex
    >>> dic = {(1, 1, 0): QQ(1), (1, 0, 0): QQ(2), (0, 1, 0): QQ(0)}
    >>> sdm_from_dict(dic, lex)
    [((1, 1, 0), 1), ((1, 0, 0), 2)]
    """
    return sdm_strip(sdm_sort(list(d.items()), O))


def sdm_sort(f, O):
    """Sort terms in ``f`` using the given monomial order ``O``. """
    return sorted(f, key=lambda term: O(term[0]), reverse=True)


def sdm_strip(f):
    """Remove terms with zero coefficients from ``f`` in ``K[X]``. """
    return [ (monom, coeff) for monom, coeff in f if coeff ]


def sdm_add(f, g, O, K):
    """
    Add two module elements ``f``, ``g``.

    Addition is done over the ground field ``K``, monomials are ordered
    according to ``O``.

    Examples
    ========

    All examples use lexicographic order.

    `(xy f_1) + (f_2) = f_2 + xy f_1`

    >>> from sympy.polys.distributedmodules import sdm_add
    >>> from sympy.polys import lex, QQ
    >>> sdm_add([((1, 1, 1), QQ(1))], [((2, 0, 0), QQ(1))], lex, QQ)
    [((2, 0, 0), 1), ((1, 1, 1), 1)]

    `(xy f_1) + (-xy f_1)` = 0`

    >>> sdm_add([((1, 1, 1), QQ(1))], [((1, 1, 1), QQ(-1))], lex, QQ)
    []

    `(f_1) + (2f_1) = 3f_1`

    >>> sdm_add([((1, 0, 0), QQ(1))], [((1, 0, 0), QQ(2))], lex, QQ)
    [((1, 0, 0), 3)]

    `(yf_1) + (xf_1) = xf_1 + yf_1`

    >>> sdm_add([((1, 0, 1), QQ(1))], [((1, 1, 0), QQ(1))], lex, QQ)
    [((1, 1, 0), 1), ((1, 0, 1), 1)]
    """
    h = dict(f)

    for monom, c in g:
        if monom in h:
            coeff = h[monom] + c

            if not coeff:
                del h[monom]
            else:
                h[monom] = coeff
        else:
            h[monom] = c

    return sdm_from_dict(h, O)


def sdm_LM(f):
    r"""
    Returns the leading monomial of ``f``.

    Only valid if `f \ne 0`.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_LM, sdm_from_dict
    >>> from sympy.polys import QQ, lex
    >>> dic = {(1, 2, 3): QQ(1), (4, 0, 0): QQ(1), (4, 0, 1): QQ(1)}
    >>> sdm_LM(sdm_from_dict(dic, lex))
    (4, 0, 1)
    """
    return f[0][0]


def sdm_LT(f):
    r"""
    Returns the leading term of ``f``.

    Only valid if `f \ne 0`.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_LT, sdm_from_dict
    >>> from sympy.polys import QQ, lex
    >>> dic = {(1, 2, 3): QQ(1), (4, 0, 0): QQ(2), (4, 0, 1): QQ(3)}
    >>> sdm_LT(sdm_from_dict(dic, lex))
    ((4, 0, 1), 3)
    """
    return f[0]


def sdm_mul_term(f, term, O, K):
    """
    Multiply a distributed module element ``f`` by a (polynomial) term ``term``.

    Multiplication of coefficients is done over the ground field ``K``, and
    monomials are ordered according to ``O``.

    Examples
    ========

    `0 f_1 = 0`

    >>> from sympy.polys.distributedmodules import sdm_mul_term
    >>> from sympy.polys import lex, QQ
    >>> sdm_mul_term([((1, 0, 0), QQ(1))], ((0, 0), QQ(0)), lex, QQ)
    []

    `x 0 = 0`

    >>> sdm_mul_term([], ((1, 0), QQ(1)), lex, QQ)
    []

    `(x) (f_1) = xf_1`

    >>> sdm_mul_term([((1, 0, 0), QQ(1))], ((1, 0), QQ(1)), lex, QQ)
    [((1, 1, 0), 1)]

    `(2xy) (3x f_1 + 4y f_2) = 8xy^2 f_2 + 6x^2y f_1`

    >>> f = [((2, 0, 1), QQ(4)), ((1, 1, 0), QQ(3))]
    >>> sdm_mul_term(f, ((1, 1), QQ(2)), lex, QQ)
    [((2, 1, 2), 8), ((1, 2, 1), 6)]
    """
    X, c = term

    if not f or not c:
        return []
    else:
        if K.is_one(c):
            return [ (sdm_monomial_mul(f_M, X), f_c) for f_M, f_c in f ]
        else:
            return [ (sdm_monomial_mul(f_M, X), f_c * c) for f_M, f_c in f ]


def sdm_zero():
    """Return the zero module element."""
    return []


def sdm_deg(f):
    """
    Degree of ``f``.

    This is the maximum of the degrees of all its monomials.
    Invalid if ``f`` is zero.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_deg
    >>> sdm_deg([((1, 2, 3), 1), ((10, 0, 1), 1), ((2, 3, 4), 4)])
    7
    """
    return max(sdm_monomial_deg(M[0]) for M in f)


# Conversion

def sdm_from_vector(vec, O, K, **opts):
    """
    Create an sdm from an iterable of expressions.

    Coefficients are created in the ground field ``K``, and terms are ordered
    according to monomial order ``O``. Named arguments are passed on to the
    polys conversion code and can be used to specify for example generators.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_from_vector
    >>> from sympy.abc import x, y, z
    >>> from sympy.polys import QQ, lex
    >>> sdm_from_vector([x**2+y**2, 2*z], lex, QQ)
    [((1, 0, 0, 1), 2), ((0, 2, 0, 0), 1), ((0, 0, 2, 0), 1)]
    """
    dics, gens = parallel_dict_from_expr(sympify(vec), **opts)
    dic = {}
    for i, d in enumerate(dics):
        for k, v in d.items():
            dic[(i,) + k] = K.convert(v)
    return sdm_from_dict(dic, O)


def sdm_to_vector(f, gens, K, n=None):
    """
    Convert sdm ``f`` into a list of polynomial expressions.

    The generators for the polynomial ring are specified via ``gens``. The rank
    of the module is guessed, or passed via ``n``. The ground field is assumed
    to be ``K``.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_to_vector
    >>> from sympy.abc import x, y, z
    >>> from sympy.polys import QQ, lex
    >>> f = [((1, 0, 0, 1), QQ(2)), ((0, 2, 0, 0), QQ(1)), ((0, 0, 2, 0), QQ(1))]
    >>> sdm_to_vector(f, [x, y, z], QQ)
    [x**2 + y**2, 2*z]
    """
    dic = sdm_to_dict(f)
    dics = {}
    for k, v in dic.items():
        dics.setdefault(k[0], []).append((k[1:], v))
    n = n or len(dics)
    res = []
    for k in range(n):
        if k in dics:
            res.append(Poly(dict(dics[k]), gens=gens, domain=K).as_expr())
        else:
            res.append(S.Zero)
    return res

# Algorithms.


def sdm_spoly(f, g, O, K, phantom=None):
    """
    Compute the generalized s-polynomial of ``f`` and ``g``.

    The ground field is assumed to be ``K``, and monomials ordered according to
    ``O``.

    This is invalid if either of ``f`` or ``g`` is zero.

    If the leading terms of `f` and `g` involve different basis elements of
    `F`, their s-poly is defined to be zero. Otherwise it is a certain linear
    combination of `f` and `g` in which the leading terms cancel.
    See [SCA, defn 2.3.6] for details.

    If ``phantom`` is not ``None``, it should be a pair of module elements on
    which to perform the same operation(s) as on ``f`` and ``g``. The in this
    case both results are returned.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_spoly
    >>> from sympy.polys import QQ, lex
    >>> f = [((2, 1, 1), QQ(1)), ((1, 0, 1), QQ(1))]
    >>> g = [((2, 3, 0), QQ(1))]
    >>> h = [((1, 2, 3), QQ(1))]
    >>> sdm_spoly(f, h, lex, QQ)
    []
    >>> sdm_spoly(f, g, lex, QQ)
    [((1, 2, 1), 1)]
    """
    if not f or not g:
        return sdm_zero()
    LM1 = sdm_LM(f)
    LM2 = sdm_LM(g)
    if LM1[0] != LM2[0]:
        return sdm_zero()
    LM1 = LM1[1:]
    LM2 = LM2[1:]
    lcm = monomial_lcm(LM1, LM2)
    m1 = monomial_div(lcm, LM1)
    m2 = monomial_div(lcm, LM2)
    c = K.quo(-sdm_LC(f, K), sdm_LC(g, K))
    r1 = sdm_add(sdm_mul_term(f, (m1, K.one), O, K),
                 sdm_mul_term(g, (m2, c), O, K), O, K)
    if phantom is None:
        return r1
    r2 = sdm_add(sdm_mul_term(phantom[0], (m1, K.one), O, K),
                 sdm_mul_term(phantom[1], (m2, c), O, K), O, K)
    return r1, r2


def sdm_ecart(f):
    """
    Compute the ecart of ``f``.

    This is defined to be the difference of the total degree of `f` and the
    total degree of the leading monomial of `f` [SCA, defn 2.3.7].

    Invalid if f is zero.

    Examples
    ========

    >>> from sympy.polys.distributedmodules import sdm_ecart
    >>> sdm_ecart([((1, 2, 3), 1), ((1, 0, 1), 1)])
    0
    >>> sdm_ecart([((2, 2, 1), 1), ((1, 5, 1), 1)])
    3
    """
    return sdm_deg(f) - sdm_monomial_deg(sdm_LM(f))


def sdm_nf_mora(f, G, O, K, phantom=None):
    r"""
    Compute a weak normal form of ``f`` with respect to ``G`` and order ``O``.

    The ground field is assumed to be ``K``, and monomials ordered according to
    ``O``.

    Weak normal forms are defined in [SCA, defn 2.3.3]. They are not unique.
    This function deterministically computes a weak normal form, depending on
    the order of `G`.

    The most important property of a weak normal form is the following: if
    `R` is the ring associated with the monomial ordering (if the ordering is
    global, we just have `R = K[x_1, \dots, x_n]`, otherwise it is a certain
    localization thereof), `I` any ideal of `R` and `G` a standard basis for
    `I`, then for any `f \in R`, we have `f \in I` if and only if
    `NF(f | G) = 0`.

    This is the generalized Mora algorithm for computing weak normal forms with
    respect to arbitrary monomial orders [SCA, algorithm 2.3.9].

    If ``phantom`` is not ``None``, it should be a pair of "phantom" arguments
    on which to perform the same computations as on ``f``, ``G``, both results
    are then returned.
    """
    from itertools import repeat
    h = f
    T = list(G)
    if phantom is not None:
        # "phantom" variables with suffix p
        hp = phantom[0]
        Tp = list(phantom[1])
        phantom = True
    else:
        Tp = repeat([])
        phantom = False
    while h:
        # TODO better data structure!!!
        Th = [(g, sdm_ecart(g), gp) for g, gp in zip(T, Tp)
              if sdm_monomial_divides(sdm_LM(g), sdm_LM(h))]
        if not Th:
            break
        g, _, gp = min(Th, key=lambda x: x[1])
        if sdm_ecart(g) > sdm_ecart(h):
            T.append(h)
            if phantom:
                Tp.append(hp)
        if phantom:
            h, hp = sdm_spoly(h, g, O, K, phantom=(hp, gp))
        else:
            h = sdm_spoly(h, g, O, K)
    if phantom:
        return h, hp
    return h


def sdm_nf_buchberger(f, G, O, K, phantom=None):
    r"""
    Compute a weak normal form of ``f`` with respect to ``G`` and order ``O``.

    The ground field is assumed to be ``K``, and monomials ordered according to
    ``O``.

    This is the standard Buchberger algorithm for computing weak normal forms with
    respect to *global* monomial orders [SCA, algorithm 1.6.10].

    If ``phantom`` is not ``None``, it should be a pair of "phantom" arguments
    on which to perform the same computations as on ``f``, ``G``, both results
    are then returned.
    """
    from itertools import repeat
    h = f
    T = list(G)
    if phantom is not None:
        # "phantom" variables with suffix p
        hp = phantom[0]
        Tp = list(phantom[1])
        phantom = True
    else:
        Tp = repeat([])
        phantom = False
    while h:
        try:
            g, gp = next((g, gp) for g, gp in zip(T, Tp)
                         if sdm_monomial_divides(sdm_LM(g), sdm_LM(h)))
        except StopIteration:
            break
        if phantom:
            h, hp = sdm_spoly(h, g, O, K, phantom=(hp, gp))
        else:
            h = sdm_spoly(h, g, O, K)
    if phantom:
        return h, hp
    return h


def sdm_nf_buchberger_reduced(f, G, O, K):
    r"""
    Compute a reduced normal form of ``f`` with respect to ``G`` and order ``O``.

    The ground field is assumed to be ``K``, and monomials ordered according to
    ``O``.

    In contrast to weak normal forms, reduced normal forms *are* unique, but
    their computation is more expensive.

    This is the standard Buchberger algorithm for computing reduced normal forms
    with respect to *global* monomial orders [SCA, algorithm 1.6.11].

    The ``pantom`` option is not supported, so this normal form cannot be used
    as a normal form for the "extended" groebner algorithm.
    """
    h = sdm_zero()
    g = f
    while g:
        g = sdm_nf_buchberger(g, G, O, K)
        if g:
            h = sdm_add(h, [sdm_LT(g)], O, K)
            g = g[1:]
    return h


def sdm_groebner(G, NF, O, K, extended=False):
    """
    Compute a minimal standard basis of ``G`` with respect to order ``O``.

    The algorithm uses a normal form ``NF``, for example ``sdm_nf_mora``.
    The ground field is assumed to be ``K``, and monomials ordered according
    to ``O``.

    Let `N` denote the submodule generated by elements of `G`. A standard
    basis for `N` is a subset `S` of `N`, such that `in(S) = in(N)`, where for
    any subset `X` of `F`, `in(X)` denotes the submodule generated by the
    initial forms of elements of `X`. [SCA, defn 2.3.2]

    A standard basis is called minimal if no subset of it is a standard basis.

    One may show that standard bases are always generating sets.

    Minimal standard bases are not unique. This algorithm computes a
    deterministic result, depending on the particular order of `G`.

    If ``extended=True``, also compute the transition matrix from the initial
    generators to the groebner basis. That is, return a list of coefficient
    vectors, expressing the elements of the groebner basis in terms of the
    elements of ``G``.

    This functions implements the "sugar" strategy, see

    Giovini et al: "One sugar cube, please" OR Selection strategies in
    Buchberger algorithm.
    """

    # The critical pair set.
    # A critical pair is stored as (i, j, s, t) where (i, j) defines the pair
    # (by indexing S), s is the sugar of the pair, and t is the lcm of their
    # leading monomials.
    P = []

    # The eventual standard basis.
    S = []
    Sugars = []

    def Ssugar(i, j):
        """Compute the sugar of the S-poly corresponding to (i, j)."""
        LMi = sdm_LM(S[i])
        LMj = sdm_LM(S[j])
        return max(Sugars[i] - sdm_monomial_deg(LMi),
                   Sugars[j] - sdm_monomial_deg(LMj)) \
            + sdm_monomial_deg(sdm_monomial_lcm(LMi, LMj))

    ourkey = lambda p: (p[2], O(p[3]), p[1])

    def update(f, sugar, P):
        """Add f with sugar ``sugar`` to S, update P."""
        if not f:
            return P
        k = len(S)
        S.append(f)
        Sugars.append(sugar)

        LMf = sdm_LM(f)

        def removethis(pair):
            i, j, s, t = pair
            if LMf[0] != t[0]:
                return False
            tik = sdm_monomial_lcm(LMf, sdm_LM(S[i]))
            tjk = sdm_monomial_lcm(LMf, sdm_LM(S[j]))
            return tik != t and tjk != t and sdm_monomial_divides(tik, t) and \
                sdm_monomial_divides(tjk, t)
        # apply the chain criterion
        P = [p for p in P if not removethis(p)]

        # new-pair set
        N = [(i, k, Ssugar(i, k), sdm_monomial_lcm(LMf, sdm_LM(S[i])))
             for i in range(k) if LMf[0] == sdm_LM(S[i])[0]]
        # TODO apply the product criterion?
        N.sort(key=ourkey)
        remove = set()
        for i, p in enumerate(N):
            for j in range(i + 1, len(N)):
                if sdm_monomial_divides(p[3], N[j][3]):
                    remove.add(j)

        # TODO mergesort?
        P.extend(reversed([p for i, p in enumerate(N) if not i in remove]))
        P.sort(key=ourkey, reverse=True)
        # NOTE reverse-sort, because we want to pop from the end
        return P

    # Figure out the number of generators in the ground ring.
    try:
        # NOTE: we look for the first non-zero vector, take its first monomial
        #       the number of generators in the ring is one less than the length
        #       (since the zeroth entry is for the module generators)
        numgens = len(next(x[0] for x in G if x)[0]) - 1
    except StopIteration:
        # No non-zero elements in G ...
        if extended:
            return [], []
        return []

    # This list will store expressions of the elements of S in terms of the
    # initial generators
    coefficients = []

    # First add all the elements of G to S
    for i, f in enumerate(G):
        P = update(f, sdm_deg(f), P)
        if extended and f:
            coefficients.append(sdm_from_dict({(i,) + (0,)*numgens: K(1)}, O))

    # Now carry out the buchberger algorithm.
    while P:
        i, j, s, t = P.pop()
        f, sf, g, sg = S[i], Sugars[i], S[j], Sugars[j]
        if extended:
            sp, coeff = sdm_spoly(f, g, O, K,
                                  phantom=(coefficients[i], coefficients[j]))
            h, hcoeff = NF(sp, S, O, K, phantom=(coeff, coefficients))
            if h:
                coefficients.append(hcoeff)
        else:
            h = NF(sdm_spoly(f, g, O, K), S, O, K)
        P = update(h, Ssugar(i, j), P)

    # Finally interreduce the standard basis.
    # (TODO again, better data structures)
    S = set((tuple(f), i) for i, f in enumerate(S))
    for (a, ai), (b, bi) in permutations(S, 2):
        A = sdm_LM(a)
        B = sdm_LM(b)
        if sdm_monomial_divides(A, B) and (b, bi) in S and (a, ai) in S:
            S.remove((b, bi))

    L = sorted(((list(f), i) for f, i in S), key=lambda p: O(sdm_LM(p[0])),
               reverse=True)
    res = [x[0] for x in L]
    if extended:
        return res, [coefficients[i] for _, i in L]
    return res
