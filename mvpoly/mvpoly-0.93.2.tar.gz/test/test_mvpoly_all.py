# tests which are applied to all sublcasses -- these do not
# use the internal representation of the subclass

import mvpoly
import mvpoly.cube
import mvpoly.dict
import numpy as np
import unittest
import warnings
import itertools

classes = [mvpoly.cube.MVPolyCube, mvpoly.dict.MVPolyDict]

def example_polynomials(C) :
    x, y, z = C.monomials(3)
    return [x**2 + z - 3,
            y**3 + 7,
            (x + y - 3*z + 1)**3]

class TestMVPolyRingAxioms(unittest.TestCase) :

    def test_addition_associative(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            self.assertTrue((p+q)+r == p+(q+r), "associativity")

    def test_additive_identity(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            z = C.zero()
            self.assertTrue(z+p == p, "additive identity")
            self.assertTrue(q+z == q, "additive identity")

    def test_additive_inverse(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            z = C.zero()
            self.assertTrue(p-p == z, "additive inverse")
            self.assertTrue(z == q-q, "additive inverse")

    def test_addition_commutative(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            self.assertTrue(p+q == q+p, "addition commutative")

    def test_multiplication_associative(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            self.assertTrue((p*q)*r == p*(q*r), "associativity")

    def test_mutiplicative_identity(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            one = C.one()
            self.assertTrue(one*p == p, "multiplicative identity")
            self.assertTrue(q*one == q, "multiplicative identity")

    def test_multiplication_commutative(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            self.assertTrue(p*q == q*p, "multiplication commutative")

    def test_distributive(self) :
        for C in classes :
            p, q, r = example_polynomials(C)
            self.assertTrue(p*(q+r) == p*q + p*r, "left distribute")
            self.assertTrue((p+q)*r == p*r + q*r, "right distribute")


class TestMVPolyInit(unittest.TestCase) :

    def test_init_sameclass(self) :
        for C in classes :
            x, y = C.monomials(2)
            p = (x + 2*y - 4)**3
            q = C(p)
            self.assertTrue(p == q, "init from same class")

    def test_roundtrip(self) :
        perms = itertools.permutations(classes, 2)        
        for perm in perms :
            for dtype in [int, float, np.float64] :
                x, y = perm[0].monomials(2, dtype=dtype)
                p = (x + y + 1)**3
                q = perm[1](p)
                r = perm[0](q)
                self.assertTrue(p == r, "equality")
                self.assertTrue(p.dtype == r.dtype, "dtype")


class TestMVPolyGetitem(unittest.TestCase) :

    def test_getitem_numargs_zero(self) :
        for C in classes :
            p = C.zero(dtype = np.int32)
            self.assertTrue(p[()]  == 0, "getitem zero, 0 arg")
            self.assertTrue(p[0]   == 0, "getitem zero, 1 arg")
            self.assertTrue(p[0,0] == 0, "getitem zero, 2 args")

    def test_getitem_numargs_const(self) :
        for C in classes :
            p = C.one(dtype = np.int32) * 7
            self.assertTrue(p[()]  == 7, "getitem const, 0 arg")
            self.assertTrue(p[0]   == 7, "getitem const, 1 arg")
            self.assertTrue(p[3]   == 0, "getitem const, 1 arg")
            self.assertTrue(p[0,0] == 7, "getitem const, 2 args")
            self.assertTrue(p[7,9] == 0, "getitem const, 2 args")

    def test_getitem_numargs_univar(self) :
        for C in classes :
            print C
            x, = C.monomials(1, dtype=np.int32)
            p = 4 + 3*x + 2*x**2
            self.assertTrue(p[()]  == 4, "getitem 1-D, 0 arg")
            self.assertTrue(p[0]   == 4, "getitem 1-D, 1 arg")
            self.assertTrue(p[1]   == 3, "getitem 1-D, 1 arg")
            self.assertTrue(p[2]   == 2, "getitem 1-D, 1 arg")
            self.assertTrue(p[3]   == 0, "getitem 1-D, 1 arg")
            self.assertTrue(p[0,0] == 4, "getitem 1-D, 2 args")
            self.assertTrue(p[7,9] == 0, "getitem 1-D, 2 args")

    def test_getitem_numargs_bivar(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=np.int32)
            p = 4 + 3*y + 2*x**2
            self.assertTrue(p[()]  == 4, "getitem 2-D, 0 arg")
            self.assertTrue(p[0]   == 4, "getitem 2-D, 1 arg")
            self.assertTrue(p[0,1] == 3, "getitem 2-D, 2 arg")
            self.assertTrue(p[2,0] == 2, "getitem 2-D, 1 arg")
            self.assertTrue(p[2]   == 2, "getitem 2-D, 1 arg (implicit)")
            self.assertTrue(p[3]   == 0, "getitem 2-D, 1 arg")
            self.assertTrue(p[0,0] == 4, "getitem 2-D, 2 args")
            self.assertTrue(p[7,9] == 0, "getitem 2-D, 2 args")


class TestMVPolySetitem(unittest.TestCase) :

    def test_setitem_constant(self) :
        for C in classes :
            p = C.zero(dtype=int)
            p[0,0,0] = 3
            q = 3*C.one(dtype=int)
            self.assertTrue(p == q, "setitem value")

    def test_setitem_monomial(self) :
        for C in classes :
            for dtype in [np.int32, np.float] :
                x, y, z = C.monomials(3, dtype=dtype)
                q = 2 * x**3 * y**2 * z**4
                p = C.zero(dtype = dtype)
                p[3,2,4] = 2
                self.assertTrue(p == q, "setitem value")
                self.assertTrue(p.dtype == dtype, "setitem dtype")
            

class TestMVPolyDegrees(unittest.TestCase) :

    def test_degrees_zero(self) :
        for C in classes :
            p = C.zero(dtype=np.int32)
            self.assertTrue(p.degrees == (),
                            "degrees of zero polynomial")

    def test_degrees_constant(self) :
        for C in classes :
            p = 3 * C.one(dtype = np.int32)
            print p, C, p.degrees
            self.assertTrue(p.degrees == (),
                            "degrees of constant polynomial")

    def test_degrees_1d(self) :
        for C in classes :
            x, = C.monomials(1)
            p = (x+1)**2
            self.assertTrue(p.degrees == (2,),
                            "degrees of univariate polynomial")

    def test_degrees_2d(self) :
        for C in classes :
            x, y, z = C.monomials(3)
            p = x + z**2 + 7
            self.assertTrue(p.degrees == (1, 0, 2),
                            "degrees of multivariate polynomial")


class TestMVPolyDegree(unittest.TestCase) :

    def test_degree_zero(self) :
        for C in classes :
            p = C.zero(dtype=int)
            self.assertTrue(p.degree == -1, 
                            "degree of zero polynomial") 

    def test_degree_0d(self) :
        for C in classes :
            one = C.one(dtype=int)
            self.assertTrue((5*one).degree == 0,
                            "degree of constant polynomial")

    def test_degree_1d(self) :
        for C in classes :
            x, = C.monomials(1, dtype=int)
            p = x**5 + x + 3
            self.assertTrue(p.degree == 5, 
                            "degree of univariate polynomial")

    def test_degree_2d(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = (x**5 + x + 3)*y**2 + y 
            obt = p.degree
            self.assertTrue(p.degree == 7, 
                            "degree of bivariate polynomial")


class TestMVPolyEval(unittest.TestCase) :

    def test_eval_dtype(self) :
        for C in classes :
            for dt in [int, float] :
                x, y = C.monomials(2, dtype=dt)
                p = x + y + 1
                self.assertTrue(p.dtype == dt)
                xg = np.array([1, 2], dtype=dt)
                yg = np.array([-2, 0], dtype=dt)
                self.assertTrue(p(xg, yg).dtype == dt, "bad type")

    def test_eval_regression(self) :
        for C in classes :
            for dt in [int, float] :
                x, y = C.monomials(2, dtype=dt)
                p = 2*x**2 + 3*y
                self.assertTrue(p(1,1) == 5, "regression A")
                p = 2*x + 3*y**2
                self.assertTrue(p(1,1) == 5, "regression B")
                x, y, z = C.monomials(3, dtype=dt)
                p = 3*x**2 + y + z
                self.assertTrue(p(1,1,1) == 5, "regression C")

    def test_eval_univar(self) :
        for C in classes :
            x, = C.monomials(1)
            p = x**2 + 1
            self.assertTrue(p(2) == 5, "univar")

    def test_eval_1d_in_2d(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = x**2 + 1
            self.assertTrue(p.eval(2, 1) == 5, "2 in 1")

    def test_eval_return_type(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = x**2 + y
            self.assertTrue(isinstance(p.eval(2, 1), int), "int return")

    def test_eval_complex(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=complex)
            p = x**2 - y
            self.assertTrue(p.eval(1.0j, 1.0) == -2, "complex eval") 


class TestMVPolyCompose(unittest.TestCase) :
    
    def test_compose_1d(self) :
        for C in classes :
            x, = C.monomials(1, dtype=int)
            p = x**2 + 1
            q = p.compose(x-1)
            exp = (x-1)**2 + 1
            obt = q
            self.assertTrue(exp == obt, 
                            "bad compose\n%s\n%s" % (repr(obt), repr(exp)))

    def test_compose_2d(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = x**2 + y + 1
            q = p.compose(2*y, x)
            exp = (2*y)**2 + x + 1
            obt = q
            self.assertTrue(exp == obt, 
                            "bad compose\n%s\n%s" % (repr(obt), repr(exp)))

    def test_compose_distribute_over_eval(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = (x + 3*y - 1)**2
            u = x - y
            v = x + y
            for i in range(5) :
                for j in range(5) :
                    exp = p.compose(u, v).eval(i, j)
                    obt = p.eval(u.eval(i, j), v.eval(i, j))
                    self.assertTrue(exp == obt, 
                                    "bad compose\n%s\n%s" % (repr(obt), repr(exp)))

    def test_call_compose(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = x + y
            self.assertTrue(isinstance(p(1, y), C), "bad call/compose")
            self.assertTrue(isinstance(p(1, 2), int), "bad call/eval")

    def test_compose_1of2(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)        
            p = x + 1
            q = p.compose(y, x)
            self.assertTrue(q(1, 0) == 1, "bad compose")


class TestMVPolyDiff(unittest.TestCase) :

    def test_diff_1d(self) :
        for C in classes :
            x, = C.monomials(1)
            p = x**5 + 2*x**2 + 1
            exp = 5*x**4 + 4*x
            obt = p.diff(1)
            self.assertTrue(exp == obt,
                            "bad 1D-derivative\n%s\n%s" % (repr(obt), repr(exp)))

    def test_diff_2d(self) :
        for C in classes :
            x, y = C.monomials(2, dtype = int)
            p = x**2 + x*y + y**3
            exp = 2*x + y 
            obt = p.diff(1, 0)
            self.assertTrue(exp == obt,
                            "bad x-derivative\n%s\n%s" % (repr(obt), repr(exp)))
            exp = x + 3*y**2
            obt = p.diff(0, 1)
            self.assertTrue(exp == obt,
                            "bad y-derivative\n%s\n%s" % (repr(obt), repr(exp)))

    def test_diff_dtype(self) :
        for C in classes :
            for dt in (np.int32, np.float64) :
                x, y = C.monomials(2, dtype=dt)
                p = 2*x**2 + 3*y**3
                exp = dt
                obt = p.diff(2,1).dtype
                self.assertTrue(exp == obt, 
                                "bad datatype %s %s" % (repr(obt), repr(exp)))


class TestMVPolyInt(unittest.TestCase) :

    def test_int_1d(self) :
        for C in classes :
            x, = C.monomials(1, dtype = np.double)
            p = 5*x**4 + 4*x
            exp = x**5 + 2*x**2
            obt = p.int(1)
            self.assertTrue(exp == obt,
                            "bad 1D indefinite integral \n%s\n%s" % \
                                (repr(obt), repr(exp)))

    def test_int2_1d(self) :
        for C in classes :
            x, = C.monomials(1, dtype = np.double)
            p = 6*x + 2
            exp = (x + 1) * x**2
            obt = p.int(2)
            self.assertTrue(exp == obt,
                            "bad 1D indefinite integral \n%s\n%s" % \
                                (repr(obt), repr(exp)))

    def test_int_2d_x(self) :
        for C in classes :
            x, y = C.monomials(2, dtype = np.double)
            p = 3*x**2 + 4*x*y + 3*y**2
            exp = x**3 + 2*y*(x**2) + 3*x*y**2
            obt = p.int(1, 0)
            self.assertTrue(exp == obt,
                            "bad indefinite integral (x) \n%s\n%s" % \
                                (repr(obt), repr(exp)))

    def test_int_2d_y(self) :
        for C in classes :
            x, y = C.monomials(2, dtype = np.double)
            p = 3*x**2 + 4*x*y + 3*y**2
            exp = 3*y*x**2 + 2*x*y**2 + y**3
            obt = p.int(0, 1)
            self.assertTrue(exp == obt,
                            "bad indefinite integral (y) \n%s\n%s" % \
                                (repr(obt), repr(exp)))

    def test_int_invariant(self) :
        for C in classes :
            x, = C.monomials(1, dtype = np.double)
            p0 = 2*x
            p1 = 2*x
            p0.int(1)
            self.assertTrue(p0 == p1, 
                            "ingegration side-effect %s %s" % \
                                (repr(p0), repr(p1)))
        
    def test_int_dtype(self) :
        for C in classes :
            for dt in [np.float32, np.float64, np.complex] :
                x, y = C.monomials(2, dtype = int)
                p = (x+y)**2
                q = p.int(1, 1, dtype=dt)
                exp = dt
                obt = q.dtype
                self.assertTrue(exp == obt, 
                                "bad datatype %s %s" % (repr(obt), repr(exp)))

    def test_int_integer_warning(self) :
        for C in classes :
            x, y = C.monomials(2, dtype=int)
            p = 3*x + 4*y
            with warnings.catch_warnings(record=True) as w :
                warnings.simplefilter('always')
                p.int(1, 1)
                self.assertTrue(len(w), "expected 1 warning, got %i" % (len(w)))
                wcat = w[0].category
                self.assertTrue(issubclass(wcat, RuntimeWarning),
                                "expected RuntimeWarning, got %s" % (wcat))
                

class TestMVPolyIntd(unittest.TestCase) :

    def test_intd_bad_args(self) :
        for C in classes :
            x, y = C.monomials(2)
            p = x**2 + y + 1
            for iv in [[1], [1,2,3]] :
                self.assertRaises(AssertionError, p.intd, *iv)

    def test_intd_1d(self) :
        for C in classes :
            x, = C.monomials(1)
            p = x
            exp = 0.5
            for interval in [ [0, 1], 
                              (0, 1), 
                              np.array([0, 1]),
                              range(2) ] :
                obt = p.intd(interval)
                self.assertTrue(exp == obt, 
                                "bad integral %s" % (repr(obt)))

    def test_intd_2d(self) :
        for C in classes :
            x, y = C.monomials(2)
            p = x**2 + 4*y
            exp = 1719
            obt = p.intd([11, 14], [7, 10])
            self.assertTrue(exp == obt, 
                            "bad integral %s" % (repr(obt)))

    def test_intd_3d(self) :
        for C in classes :
            x, y, z = C.monomials(3)
            p = x + y + z
            exp = 1.5
            obt = p.intd([0, 1], [0, 1], [0, 1])
            self.assertTrue(exp == obt, 
                            "bad integral %s" % (repr(obt)))
            p = 3*x**2 + y + z
            exp = 12
            obt = p.intd([0, 1], [2, 4], [-2, 0])
            self.assertTrue(exp == obt, 
                            "bad integral %s" % (repr(obt)))


class TestMVPolyMaxmodND(unittest.TestCase) :

    def test_maxmodnd_univariate(self) :
        eps = 1e-9 
        for C in classes :
            x, = C.monomials(1, dtype=complex)
            p = x**10 + 1
            exp = 2
            obt = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(exp - obt) < eps*exp, 
                            "bad 1d maxmodnd %s" % (repr(obt)))

    def test_maxmodnd_bivariate(self) :
        eps = 1e-9
        for C in classes :
            x, y = C.monomials(2, dtype=complex)
            p = (1 + x**9)*y**9 + 8
            exp = 10
            obt = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(exp - obt) < eps*exp,
                            "bad 2d maxmodnd %s" % (repr(obt)))

    def test_maxmodnd_kaijser_varopoulos(self) :
        # N. Varopoulos, On an inequality of von Neumann and an 
        # application of themetric theory of tensor products to 
        # operator theory, J. Funct. Anal., 16 (1974), 83--100.
        eps = 1e-5
        for C in classes :
            x, y, z = C.monomials(3, dtype=complex)
            p = x**2 + y**2 + z**2 - 2*x*y - 2*x*z - 2*y*z 
            exp = 5
            obt = p.maxmodnd(epsilon=eps)[0]
            self.assertTrue(np.abs(exp - obt) < eps*exp, 
                            "bad kaijser-varopoulos maxmodnd %s" % (repr(obt)))

