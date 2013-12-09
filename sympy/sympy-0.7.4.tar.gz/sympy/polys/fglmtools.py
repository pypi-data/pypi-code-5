"""Implementation of matrix FGLM Groebner basis conversion algorithm. """

from __future__ import print_function, division

from sympy.polys.monomials import monomial_mul, monomial_div
from sympy.core.compatibility import xrange

def matrix_fglm(F, ring, O_to):
    """
    Converts the reduced Groebner basis ``F`` of a zero-dimensional
    ideal w.r.t. ``O_from`` to a reduced Groebner basis
    w.r.t. ``O_to``.

    References
    ==========

    J.C. Faugere, P. Gianni, D. Lazard, T. Mora (1994). Efficient
    Computation of Zero-dimensional Groebner Bases by Change of
    Ordering
    """
    domain = ring.domain
    ngens = ring.ngens

    ring_to = ring.clone(order=O_to)

    old_basis = _basis(F, ring)
    M = _representing_matrices(old_basis, F, ring)

    # V contains the normalforms (wrt O_from) of S
    S = [ring.zero_monom]
    V = [[domain.one] + [domain.zero] * (len(old_basis) - 1)]
    G = []

    L = [(i, 0) for i in xrange(ngens)]  # (i, j) corresponds to x_i * S[j]
    L.sort(key=lambda k_l: O_to(_incr_k(S[k_l[1]], k_l[0])), reverse=True)
    t = L.pop()

    P = _identity_matrix(len(old_basis), domain)

    while True:
        s = len(S)
        v = _matrix_mul(M[t[0]], V[t[1]])
        _lambda = _matrix_mul(P, v)

        if all(_lambda[i] == domain.zero for i in xrange(s, len(old_basis))):
            # there is a linear combination of v by V
            lt = ring.term_new(_incr_k(S[t[1]], t[0]), domain.one)
            rest = ring.from_dict(dict([ (S[i], _lambda[i]) for i in xrange(s) ]))

            g = (lt - rest).set_ring(ring_to)
            if g:
                G.append(g)
        else:
            # v is linearly independant from V
            P = _update(s, _lambda, P)
            S.append(_incr_k(S[t[1]], t[0]))
            V.append(v)

            L.extend([(i, s) for i in xrange(ngens)])
            L = list(set(L))
            L.sort(key=lambda k_l: O_to(_incr_k(S[k_l[1]], k_l[0])), reverse=True)

        L = [(k, l) for (k, l) in L if all(monomial_div(_incr_k(S[l], k), g.LM) is None for g in G)]

        if not L:
            G = [ g.monic() for g in G ]
            return sorted(G, key=lambda g: O_to(g.LM), reverse=True)

        t = L.pop()


def _incr_k(m, k):
    return tuple(list(m[:k]) + [m[k] + 1] + list(m[k + 1:]))


def _identity_matrix(n, domain):
    M = [[domain.zero]*n for _ in xrange(n)]

    for i in xrange(n):
        M[i][i] = domain.one

    return M


def _matrix_mul(M, v):
    return [sum([row[i] * v[i] for i in xrange(len(v))]) for row in M]


def _update(s, _lambda, P):
    """
    Update ``P`` such that for the updated `P'` `P' v = e_{s}`.
    """
    k = min([j for j in xrange(s, len(_lambda)) if _lambda[j] != 0])

    for r in xrange(len(_lambda)):
        if r != k:
            P[r] = [P[r][j] - (P[k][j] * _lambda[r]) / _lambda[k] for j in xrange(len(P[r]))]

    P[k] = [P[k][j] / _lambda[k] for j in xrange(len(P[k]))]
    P[k], P[s] = P[s], P[k]

    return P


def _representing_matrices(basis, G, ring):
    """
    Compute the matrices corresponding to the linear maps `m \mapsto
    x_i m` for all variables `x_i`.
    """
    domain = ring.domain
    u = ring.ngens-1

    def var(i):
        return tuple([0] * i + [1] + [0] * (u - i))

    def representing_matrix(m):
        M = [[domain.zero] * len(basis) for _ in xrange(len(basis))]

        for i, v in enumerate(basis):
            r = ring.term_new(monomial_mul(m, v), domain.one).rem(G)

            for monom, coeff in r.terms():
                j = basis.index(monom)
                M[j][i] = coeff

        return M

    return [representing_matrix(var(i)) for i in xrange(u + 1)]


def _basis(G, ring):
    """
    Computes a list of monomials which are not divisible by the leading
    monomials wrt to ``O`` of ``G``. These monomials are a basis of
    `K[X_1, \ldots, X_n]/(G)`.
    """
    order = ring.order

    leading_monomials = [g.LM for g in G]
    candidates = [ring.zero_monom]
    basis = []

    while candidates:
        t = candidates.pop()
        basis.append(t)

        new_candidates = [_incr_k(t, k) for k in xrange(ring.ngens)
            if all(monomial_div(_incr_k(t, k), lmg) is None
            for lmg in leading_monomials)]
        candidates.extend(new_candidates)
        candidates.sort(key=lambda m: order(m), reverse=True)

    basis = list(set(basis))

    return sorted(basis, key=lambda m: order(m))
