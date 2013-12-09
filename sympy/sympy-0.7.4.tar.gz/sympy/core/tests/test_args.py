"""Test whether all elements of cls.args are instances of Basic. """

# NOTE: keep tests sorted by (module, class name) key. If a class can't
# be instantiated, add it here anyway with @SKIP("abstract class) (see
# e.g. Function).

import os
import re
import warnings

from sympy import Basic, S, symbols, sqrt, sin, oo, Interval, exp
from sympy.utilities.pytest import XFAIL, SKIP
from sympy.utilities.exceptions import SymPyDeprecationWarning

x, y, z = symbols('x,y,z')


def test_all_classes_are_tested():
    this = os.path.split(__file__)[0]
    path = os.path.join(this, os.pardir, os.pardir)
    sympy_path = os.path.abspath(path)
    prefix = os.path.split(sympy_path)[0] + os.sep

    re_cls = re.compile("^class ([A-Za-z][A-Za-z0-9_]*)\s*\(", re.MULTILINE)

    modules = {}

    # Ignore sympy.statistics import warning
    warnings.filterwarnings("ignore", message="sympy.statistics has been deprecated since SymPy 0.7.2",
        category=SymPyDeprecationWarning)

    for root, dirs, files in os.walk(sympy_path):
        module = root.replace(prefix, "").replace(os.sep, ".")

        for file in files:
            if file.startswith(("_", "test_", "bench_")):
                continue
            if not file.endswith(".py"):
                continue

            with open(os.path.join(root, file), "r") as f:
                text = f.read()

            submodule = module + '.' + file[:-3]
            names = re_cls.findall(text)

            if not names:
                continue

            try:
                mod = __import__(submodule, fromlist=names)
            except ImportError:
                continue

            def is_Basic(name):
                cls = getattr(mod, name)
                return issubclass(cls, Basic)

            names = list(filter(is_Basic, names))

            if names:
                modules[submodule] = names

    ns = globals()
    failed = []

    for module, names in modules.items():
        mod = module.replace('.', '__')

        for name in names:
            test = 'test_' + mod + '__' + name

            if test not in ns:
                failed.append(module + '.' + name)

    # reset all SymPyDeprecationWarning into errors
    warnings.simplefilter("error", category=SymPyDeprecationWarning)

    assert not failed, "Missing classes: %s.  Please add tests for these to sympy/core/tests/test_args.py." % ", ".join(failed)


def _test_args(obj):
    return all(isinstance(arg, Basic) for arg in obj.args)


def test_sympy__assumptions__assume__AppliedPredicate():
    from sympy.assumptions.assume import AppliedPredicate, Predicate
    assert _test_args(AppliedPredicate(Predicate("test"), 2))


def test_sympy__assumptions__assume__Predicate():
    from sympy.assumptions.assume import Predicate
    assert _test_args(Predicate("test"))


@XFAIL
def test_sympy__combinatorics__graycode__GrayCode():
    from sympy.combinatorics.graycode import GrayCode
    # an integer is given and returned from GrayCode as the arg
    assert _test_args(GrayCode(3, start='100'))
    assert _test_args(GrayCode(3, rank=1))


def test_sympy__combinatorics__subsets__Subset():
    from sympy.combinatorics.subsets import Subset
    assert _test_args(Subset([0, 1], [0, 1, 2, 3]))
    assert _test_args(Subset(['c', 'd'], ['a', 'b', 'c', 'd']))


@XFAIL
def test_sympy__combinatorics__permutations__Permutation():
    from sympy.combinatorics.permutations import Permutation
    assert _test_args(Permutation([0, 1, 2, 3]))


@XFAIL
def test_sympy__combinatorics__perm_groups__PermutationGroup():
    from sympy.combinatorics.permutations import Permutation
    from sympy.combinatorics.perm_groups import PermutationGroup
    assert _test_args(PermutationGroup([Permutation([0, 1])]))


def test_sympy__combinatorics__polyhedron__Polyhedron():
    from sympy.combinatorics.permutations import Permutation
    from sympy.combinatorics.polyhedron import Polyhedron
    from sympy.abc import w, x, y, z
    pgroup = [Permutation([[0, 1, 2], [3]]),
              Permutation([[0, 1, 3], [2]]),
              Permutation([[0, 2, 3], [1]]),
              Permutation([[1, 2, 3], [0]]),
              Permutation([[0, 1], [2, 3]]),
              Permutation([[0, 2], [1, 3]]),
              Permutation([[0, 3], [1, 2]]),
              Permutation([[0, 1, 2, 3]])]
    corners = [w, x, y, z]
    faces = [(w, x, y), (w, y, z), (w, z, x), (x, y, z)]
    assert _test_args(Polyhedron(corners, faces, pgroup))


@XFAIL
def test_sympy__combinatorics__prufer__Prufer():
    from sympy.combinatorics.prufer import Prufer
    assert _test_args(Prufer([[0, 1], [0, 2], [0, 3]], 4))


def test_sympy__combinatorics__partitions__Partition():
    from sympy.combinatorics.partitions import Partition
    assert _test_args(Partition([[1]]))


@XFAIL
def test_sympy__combinatorics__partitions__IntegerPartition():
    from sympy.combinatorics.partitions import IntegerPartition
    assert _test_args(IntegerPartition([1]))


def test_sympy__concrete__products__Product():
    from sympy.concrete.products import Product
    assert _test_args(Product(x, (x, 0, 10)))
    assert _test_args(Product(x, (x, 0, y), (y, 0, 10)))


@SKIP("abstract Class")
def test_sympy__concrete__expr_with_limits__ExprWithLimits():
    from sympy.concrete.expr_with_limits import ExprWithLimits
    assert _test_args(ExprWithLimits(x, (x, 0, 10)))
    assert _test_args(ExprWithLimits(x*y, (x, 0, 10.),(y,1.,3)))


@SKIP("abstract Class")
def test_sympy__concrete__expr_with_limits__AddWithLimits():
    from sympy.concrete.expr_with_limits import AddWithLimits
    assert _test_args(AddWithLimits(x, (x, 0, 10)))
    assert _test_args(AddWithLimits(x*y, (x, 0, 10),(y,1,3)))


@SKIP("abstract Class")
def test_sympy__concrete__expr_with_intlimits__ExprWithIntLimits():
    from sympy.concrete.expr_with_intlimits import ExprWithIntLimits
    assert _test_args(ExprWithIntLimits(x, (x, 0, 10)))
    assert _test_args(ExprWithIntLimits(x*y, (x, 0, 10),(y,1,3)))


def test_sympy__concrete__summations__Sum():
    from sympy.concrete.summations import Sum
    assert _test_args(Sum(x, (x, 0, 10)))
    assert _test_args(Sum(x, (x, 0, y), (y, 0, 10)))


def test_sympy__core__add__Add():
    from sympy.core.add import Add
    assert _test_args(Add(x, y, z, 2))


def test_sympy__core__basic__Atom():
    from sympy.core.basic import Atom
    assert _test_args(Atom())


def test_sympy__core__basic__Basic():
    from sympy.core.basic import Basic
    assert _test_args(Basic())


def test_sympy__core__containers__Dict():
    from sympy.core.containers import Dict
    assert _test_args(Dict({x: y, y: z}))


def test_sympy__core__containers__Tuple():
    from sympy.core.containers import Tuple
    assert _test_args(Tuple(x, y, z, 2))


def test_sympy__core__expr__AtomicExpr():
    from sympy.core.expr import AtomicExpr
    assert _test_args(AtomicExpr())


def test_sympy__core__expr__Expr():
    from sympy.core.expr import Expr
    assert _test_args(Expr())


def test_sympy__core__function__Application():
    from sympy.core.function import Application
    assert _test_args(Application(1, 2, 3))


def test_sympy__core__function__AppliedUndef():
    from sympy.core.function import AppliedUndef
    assert _test_args(AppliedUndef(1, 2, 3))


def test_sympy__core__function__Derivative():
    from sympy.core.function import Derivative
    assert _test_args(Derivative(2, x, y, 3))


@SKIP("abstract class")
def test_sympy__core__function__Function():
    pass


def test_sympy__core__function__Lambda():
    from sympy.core.function import Lambda
    assert _test_args(Lambda((x, y), x + y + z))


def test_sympy__core__function__Subs():
    from sympy.core.function import Subs
    assert _test_args(Subs(x + y, x, 2))


def test_sympy__core__function__WildFunction():
    from sympy.core.function import WildFunction
    assert _test_args(WildFunction('f'))


def test_sympy__core__mod__Mod():
    from sympy.core.mod import Mod
    assert _test_args(Mod(x, 2))


def test_sympy__core__mul__Mul():
    from sympy.core.mul import Mul
    assert _test_args(Mul(2, x, y, z))


def test_sympy__core__numbers__Catalan():
    from sympy.core.numbers import Catalan
    assert _test_args(Catalan())


def test_sympy__core__numbers__ComplexInfinity():
    from sympy.core.numbers import ComplexInfinity
    assert _test_args(ComplexInfinity())


def test_sympy__core__numbers__EulerGamma():
    from sympy.core.numbers import EulerGamma
    assert _test_args(EulerGamma())


def test_sympy__core__numbers__Exp1():
    from sympy.core.numbers import Exp1
    assert _test_args(Exp1())


def test_sympy__core__numbers__Float():
    from sympy.core.numbers import Float
    assert _test_args(Float(1.23))


def test_sympy__core__numbers__GoldenRatio():
    from sympy.core.numbers import GoldenRatio
    assert _test_args(GoldenRatio())


def test_sympy__core__numbers__Half():
    from sympy.core.numbers import Half
    assert _test_args(Half())


def test_sympy__core__numbers__ImaginaryUnit():
    from sympy.core.numbers import ImaginaryUnit
    assert _test_args(ImaginaryUnit())


def test_sympy__core__numbers__Infinity():
    from sympy.core.numbers import Infinity
    assert _test_args(Infinity())


def test_sympy__core__numbers__Integer():
    from sympy.core.numbers import Integer
    assert _test_args(Integer(7))


@SKIP("abstract class")
def test_sympy__core__numbers__IntegerConstant():
    pass


def test_sympy__core__numbers__NaN():
    from sympy.core.numbers import NaN
    assert _test_args(NaN())


def test_sympy__core__numbers__NegativeInfinity():
    from sympy.core.numbers import NegativeInfinity
    assert _test_args(NegativeInfinity())


def test_sympy__core__numbers__NegativeOne():
    from sympy.core.numbers import NegativeOne
    assert _test_args(NegativeOne())


def test_sympy__core__numbers__Number():
    from sympy.core.numbers import Number
    assert _test_args(Number(1, 7))


def test_sympy__core__numbers__NumberSymbol():
    from sympy.core.numbers import NumberSymbol
    assert _test_args(NumberSymbol())


def test_sympy__core__numbers__One():
    from sympy.core.numbers import One
    assert _test_args(One())


def test_sympy__core__numbers__Pi():
    from sympy.core.numbers import Pi
    assert _test_args(Pi())


def test_sympy__core__numbers__Rational():
    from sympy.core.numbers import Rational
    assert _test_args(Rational(1, 7))


def test_sympy__core__numbers__RationalConstant():
    from sympy.core.numbers import RationalConstant
    assert _test_args(RationalConstant())


def test_sympy__core__numbers__Zero():
    from sympy.core.numbers import Zero
    assert _test_args(Zero())


@SKIP("abstract class")
def test_sympy__core__operations__AssocOp():
    pass


@SKIP("abstract class")
def test_sympy__core__operations__LatticeOp():
    pass


def test_sympy__core__power__Pow():
    from sympy.core.power import Pow
    assert _test_args(Pow(x, 2))


def test_sympy__core__relational__Equality():
    from sympy.core.relational import Equality
    assert _test_args(Equality(x, 2))


def test_sympy__core__relational__GreaterThan():
    from sympy.core.relational import GreaterThan
    assert _test_args(GreaterThan(x, 2))


def test_sympy__core__relational__LessThan():
    from sympy.core.relational import LessThan
    assert _test_args(LessThan(x, 2))


@SKIP("abstract class")
def test_sympy__core__relational__Relational():
    pass


def test_sympy__core__relational__StrictGreaterThan():
    from sympy.core.relational import StrictGreaterThan
    assert _test_args(StrictGreaterThan(x, 2))


def test_sympy__core__relational__StrictLessThan():
    from sympy.core.relational import StrictLessThan
    assert _test_args(StrictLessThan(x, 2))


def test_sympy__core__relational__Unequality():
    from sympy.core.relational import Unequality
    assert _test_args(Unequality(x, 2))


def test_sympy__core__sets__EmptySet():
    from sympy.core.sets import EmptySet
    assert _test_args(EmptySet())


def test_sympy__core__sets__UniversalSet():
    from sympy.core.sets import UniversalSet
    assert _test_args(UniversalSet())


def test_sympy__core__sets__FiniteSet():
    from sympy.core.sets import FiniteSet
    assert _test_args(FiniteSet(x, y, z))


@XFAIL
def test_sympy__core__sets__Interval():
    from sympy.core.sets import Interval
    assert _test_args(Interval(0, 1))


def test_sympy__core__sets__ProductSet():
    from sympy.core.sets import ProductSet, Interval
    assert _test_args(ProductSet(Interval(0, 1), Interval(0, 1)))


@SKIP("does it make sense to test this?")
def test_sympy__core__sets__Set():
    from sympy.core.sets import Set
    assert _test_args(Set())


def test_sympy__core__sets__Intersection():
    from sympy.core.sets import Intersection, Interval
    assert _test_args(Intersection(Interval(0, 3), Interval(2, 4),
        evaluate=False))


def test_sympy__core__sets__Union():
    from sympy.core.sets import Union, Interval
    assert _test_args(Union(Interval(0, 1), Interval(2, 3)))


def test_sympy__core__trace__Tr():
    from sympy.core.trace import Tr
    a, b = symbols('a b')
    assert _test_args(Tr(a + b))


def test_sympy__sets__fancysets__Naturals():
    from sympy.sets.fancysets import Naturals
    assert _test_args(Naturals())

def test_sympy__sets__fancysets__Naturals0():
    from sympy.sets.fancysets import Naturals0
    assert _test_args(Naturals0())

def test_sympy__sets__fancysets__Integers():
    from sympy.sets.fancysets import Integers
    assert _test_args(Integers())


@XFAIL  # This fails for the same reason Interval fails. Not all args are Basic
def test_sympy__sets__fancysets__Reals():
    from sympy.sets.fancysets import Reals
    assert _test_args(Reals())


def test_sympy__sets__fancysets__ImageSet():
    from sympy.sets.fancysets import ImageSet
    from sympy import S, Lambda, Symbol
    x = Symbol('x')
    assert _test_args(ImageSet(Lambda(x, x**2), S.Naturals))


def test_sympy__sets__fancysets__Range():
    from sympy.sets.fancysets import Range
    assert _test_args(Range(1, 5, 1))

# STATS


from sympy.stats.crv_types import NormalDistribution
nd = NormalDistribution(0, 1)
from sympy.stats.frv_types import DieDistribution
die = DieDistribution(6)


def test_sympy__stats__crv__ContinuousDomain():
    from sympy.stats.crv import ContinuousDomain
    assert _test_args(ContinuousDomain(set([x]), Interval(-oo, oo)))


def test_sympy__stats__crv__SingleContinuousDomain():
    from sympy.stats.crv import SingleContinuousDomain
    assert _test_args(SingleContinuousDomain(x, Interval(-oo, oo)))


def test_sympy__stats__crv__ProductContinuousDomain():
    from sympy.stats.crv import SingleContinuousDomain, ProductContinuousDomain
    D = SingleContinuousDomain(x, Interval(-oo, oo))
    E = SingleContinuousDomain(y, Interval(0, oo))
    assert _test_args(ProductContinuousDomain(D, E))


def test_sympy__stats__crv__ConditionalContinuousDomain():
    from sympy.stats.crv import (SingleContinuousDomain,
            ConditionalContinuousDomain)
    D = SingleContinuousDomain(x, Interval(-oo, oo))
    assert _test_args(ConditionalContinuousDomain(D, x > 0))


def test_sympy__stats__crv__ContinuousPSpace():
    from sympy.stats.crv import ContinuousPSpace, SingleContinuousDomain
    D = SingleContinuousDomain(x, Interval(-oo, oo))
    assert _test_args(ContinuousPSpace(D, nd))


def test_sympy__stats__crv__SingleContinuousPSpace():
    from sympy.stats.crv import SingleContinuousPSpace
    assert _test_args(SingleContinuousPSpace(x, nd))


def test_sympy__stats__crv__ProductContinuousPSpace():
    from sympy.stats.crv import ProductContinuousPSpace, SingleContinuousPSpace
    A = SingleContinuousPSpace(x, nd)
    B = SingleContinuousPSpace(y, nd)
    assert _test_args(ProductContinuousPSpace(A, B))

@SKIP("abstract class")
def test_sympy__stats__crv__SingleContinuousDistribution():
    pass

def test_sympy__stats__drv__SingleDiscreteDomain():
    from sympy.stats.drv import SingleDiscreteDomain
    assert _test_args(SingleDiscreteDomain(x, S.Naturals))

def test_sympy__stats__drv__SingleDiscretePSpace():
    from sympy.stats.drv import SingleDiscretePSpace
    from sympy.stats.drv_types import PoissonDistribution
    assert _test_args(SingleDiscretePSpace(x, PoissonDistribution(1)))

@SKIP("abstract class")
def test_sympy__stats__drv__SingleDiscreteDistribution():
    pass

def test_sympy__stats__rv__RandomDomain():
    from sympy.stats.rv import RandomDomain
    from sympy.core.sets import FiniteSet
    assert _test_args(RandomDomain(FiniteSet(x), FiniteSet(1, 2, 3)))


def test_sympy__stats__rv__SingleDomain():
    from sympy.stats.rv import SingleDomain
    from sympy.core.sets import FiniteSet
    assert _test_args(SingleDomain(x, FiniteSet(1, 2, 3)))


def test_sympy__stats__rv__ConditionalDomain():
    from sympy.stats.rv import ConditionalDomain, RandomDomain
    from sympy.core.sets import FiniteSet
    D = RandomDomain(FiniteSet(x), FiniteSet(1, 2))
    assert _test_args(ConditionalDomain(D, x > 1))


def test_sympy__stats__rv__PSpace():
    from sympy.stats.rv import PSpace, RandomDomain
    from sympy import Dict, FiniteSet
    D = RandomDomain(FiniteSet(x), FiniteSet(1, 2, 3, 4, 5, 6))
    assert _test_args(PSpace(D, die))


@SKIP("abstract Class")
def test_sympy__stats__rv__SinglePSpace():
    pass


def test_sympy__stats__rv__RandomSymbol():
    from sympy.stats.rv import RandomSymbol
    from sympy.stats.crv import SingleContinuousPSpace
    A = SingleContinuousPSpace(x, nd)
    assert _test_args(RandomSymbol(A, x))


def test_sympy__stats__rv__ProductPSpace():
    from sympy.stats.rv import ProductPSpace
    from sympy.stats.crv import SingleContinuousPSpace
    A = SingleContinuousPSpace(x, nd)
    B = SingleContinuousPSpace(y, nd)
    assert _test_args(ProductPSpace(A, B))


def test_sympy__stats__rv__ProductDomain():
    from sympy.stats.rv import ProductDomain, SingleDomain
    D = SingleDomain(x, Interval(-oo, oo))
    E = SingleDomain(y, Interval(0, oo))
    assert _test_args(ProductDomain(D, E))


def test_sympy__stats__frv_types__DiscreteUniformDistribution():
    from sympy.stats.frv_types import DiscreteUniformDistribution
    from sympy.core.containers import Tuple
    assert _test_args(DiscreteUniformDistribution(Tuple(*list(range(6)))))


def test_sympy__stats__frv_types__DieDistribution():
    from sympy.stats.frv_types import DieDistribution
    assert _test_args(DieDistribution(6))


def test_sympy__stats__frv_types__BernoulliDistribution():
    from sympy.stats.frv_types import BernoulliDistribution
    assert _test_args(BernoulliDistribution(S.Half, 0, 1))


def test_sympy__stats__frv_types__BinomialDistribution():
    from sympy.stats.frv_types import BinomialDistribution
    assert _test_args(BinomialDistribution(5, S.Half, 1, 0))


def test_sympy__stats__frv_types__HypergeometricDistribution():
    from sympy.stats.frv_types import HypergeometricDistribution
    assert _test_args(HypergeometricDistribution(10, 5, 3))


def test_sympy__stats__frv__FiniteDomain():
    from sympy.stats.frv import FiniteDomain
    assert _test_args(FiniteDomain(set([(x, 1), (x, 2)])))  # x can be 1 or 2


def test_sympy__stats__frv__SingleFiniteDomain():
    from sympy.stats.frv import SingleFiniteDomain
    assert _test_args(SingleFiniteDomain(x, set([1, 2])))  # x can be 1 or 2


def test_sympy__stats__frv__ProductFiniteDomain():
    from sympy.stats.frv import SingleFiniteDomain, ProductFiniteDomain
    xd = SingleFiniteDomain(x, set([1, 2]))
    yd = SingleFiniteDomain(y, set([1, 2]))
    assert _test_args(ProductFiniteDomain(xd, yd))


def test_sympy__stats__frv__ConditionalFiniteDomain():
    from sympy.stats.frv import SingleFiniteDomain, ConditionalFiniteDomain
    xd = SingleFiniteDomain(x, set([1, 2]))
    assert _test_args(ConditionalFiniteDomain(xd, x > 1))


def test_sympy__stats__frv__FinitePSpace():
    from sympy.stats.frv import FinitePSpace, SingleFiniteDomain
    xd = SingleFiniteDomain(x, set([1, 2, 3, 4, 5, 6]))
    p = 1.0/6
    xd = SingleFiniteDomain(x, set([1, 2]))
    assert _test_args(FinitePSpace(xd, {(x, 1): S.Half, (x, 2): S.Half}))


def test_sympy__stats__frv__SingleFinitePSpace():
    from sympy.stats.frv import SingleFinitePSpace, SingleFiniteDomain
    from sympy import Symbol

    assert _test_args(SingleFinitePSpace(Symbol('x'), die))


def test_sympy__stats__frv__ProductFinitePSpace():
    from sympy.stats.frv import (SingleFiniteDomain, SingleFinitePSpace,
        ProductFinitePSpace)
    from sympy import Symbol
    xp = SingleFinitePSpace(Symbol('x'), die)
    yp = SingleFinitePSpace(Symbol('y'), die)
    assert _test_args(ProductFinitePSpace(xp, yp))

@SKIP("abstract class")
def test_sympy__stats__frv__SingleFiniteDistribution():
    pass

@SKIP("abstract class")
def test_sympy__stats__crv__ContinuousDistribution():
    pass


def test_sympy__stats__frv_types__FiniteDistributionHandmade():
    from sympy.stats.frv_types import FiniteDistributionHandmade
    assert _test_args(FiniteDistributionHandmade({1: 1}))


def test_sympy__stats__crv__ContinuousDistributionHandmade():
    from sympy.stats.crv import ContinuousDistributionHandmade
    from sympy import Symbol, Interval
    assert _test_args(ContinuousDistributionHandmade(Symbol('x'),
                                                     Interval(0, 2)))

def test_sympy__stats__rv__Density():
    from sympy.stats.rv import Density
    from sympy.stats.crv_types import Normal
    assert _test_args(Density(Normal('x', 0, 1)))


def test_sympy__stats__crv_types__ArcsinDistribution():
    from sympy.stats.crv_types import ArcsinDistribution
    assert _test_args(ArcsinDistribution(0, 1))


def test_sympy__stats__crv_types__BeniniDistribution():
    from sympy.stats.crv_types import BeniniDistribution
    assert _test_args(BeniniDistribution(1, 1, 1))


def test_sympy__stats__crv_types__BetaDistribution():
    from sympy.stats.crv_types import BetaDistribution
    assert _test_args(BetaDistribution(1, 1))


def test_sympy__stats__crv_types__BetaPrimeDistribution():
    from sympy.stats.crv_types import BetaPrimeDistribution
    assert _test_args(BetaPrimeDistribution(1, 1))


def test_sympy__stats__crv_types__CauchyDistribution():
    from sympy.stats.crv_types import CauchyDistribution
    assert _test_args(CauchyDistribution(0, 1))


def test_sympy__stats__crv_types__ChiDistribution():
    from sympy.stats.crv_types import ChiDistribution
    assert _test_args(ChiDistribution(1))


def test_sympy__stats__crv_types__ChiNoncentralDistribution():
    from sympy.stats.crv_types import ChiNoncentralDistribution
    assert _test_args(ChiNoncentralDistribution(1,1))


def test_sympy__stats__crv_types__ChiSquaredDistribution():
    from sympy.stats.crv_types import ChiSquaredDistribution
    assert _test_args(ChiSquaredDistribution(1))


def test_sympy__stats__crv_types__DagumDistribution():
    from sympy.stats.crv_types import DagumDistribution
    assert _test_args(DagumDistribution(1, 1, 1))


def test_sympy__stats__crv_types__ExponentialDistribution():
    from sympy.stats.crv_types import ExponentialDistribution
    assert _test_args(ExponentialDistribution(1))


def test_sympy__stats__crv_types__FDistributionDistribution():
    from sympy.stats.crv_types import FDistributionDistribution
    assert _test_args(FDistributionDistribution(1, 1))


def test_sympy__stats__crv_types__FisherZDistribution():
    from sympy.stats.crv_types import FisherZDistribution
    assert _test_args(FisherZDistribution(1, 1))


def test_sympy__stats__crv_types__FrechetDistribution():
    from sympy.stats.crv_types import FrechetDistribution
    assert _test_args(FrechetDistribution(1, 1, 1))


def test_sympy__stats__crv_types__GammaInverseDistribution():
    from sympy.stats.crv_types import GammaInverseDistribution
    assert _test_args(GammaInverseDistribution(1, 1))


def test_sympy__stats__crv_types__GammaDistribution():
    from sympy.stats.crv_types import GammaDistribution
    assert _test_args(GammaDistribution(1, 1))


def test_sympy__stats__crv_types__KumaraswamyDistribution():
    from sympy.stats.crv_types import KumaraswamyDistribution
    assert _test_args(KumaraswamyDistribution(1, 1))

def test_sympy__stats__crv_types__LaplaceDistribution():
    from sympy.stats.crv_types import LaplaceDistribution
    assert _test_args(LaplaceDistribution(0, 1))


def test_sympy__stats__crv_types__LogisticDistribution():
    from sympy.stats.crv_types import LogisticDistribution
    assert _test_args(LogisticDistribution(0, 1))


def test_sympy__stats__crv_types__LogNormalDistribution():
    from sympy.stats.crv_types import LogNormalDistribution
    assert _test_args(LogNormalDistribution(0, 1))


def test_sympy__stats__crv_types__MaxwellDistribution():
    from sympy.stats.crv_types import MaxwellDistribution
    assert _test_args(MaxwellDistribution(1))


def test_sympy__stats__crv_types__NakagamiDistribution():
    from sympy.stats.crv_types import NakagamiDistribution
    assert _test_args(NakagamiDistribution(1, 1))


def test_sympy__stats__crv_types__NormalDistribution():
    from sympy.stats.crv_types import NormalDistribution
    assert _test_args(NormalDistribution(0, 1))


def test_sympy__stats__crv_types__ParetoDistribution():
    from sympy.stats.crv_types import ParetoDistribution
    assert _test_args(ParetoDistribution(1, 1))


def test_sympy__stats__crv_types__QuadraticUDistribution():
    from sympy.stats.crv_types import QuadraticUDistribution
    assert _test_args(QuadraticUDistribution(1, 2))

def test_sympy__stats__crv_types__RaisedCosineDistribution():
    from sympy.stats.crv_types import RaisedCosineDistribution
    assert _test_args(RaisedCosineDistribution(1, 1))

def test_sympy__stats__crv_types__RayleighDistribution():
    from sympy.stats.crv_types import RayleighDistribution
    assert _test_args(RayleighDistribution(1))


def test_sympy__stats__crv_types__StudentTDistribution():
    from sympy.stats.crv_types import StudentTDistribution
    assert _test_args(StudentTDistribution(1))


def test_sympy__stats__crv_types__TriangularDistribution():
    from sympy.stats.crv_types import TriangularDistribution
    assert _test_args(TriangularDistribution(-1, 0, 1))


def test_sympy__stats__crv_types__UniformDistribution():
    from sympy.stats.crv_types import UniformDistribution
    assert _test_args(UniformDistribution(0, 1))


def test_sympy__stats__crv_types__UniformSumDistribution():
    from sympy.stats.crv_types import UniformSumDistribution
    assert _test_args(UniformSumDistribution(1))


def test_sympy__stats__crv_types__VonMisesDistribution():
    from sympy.stats.crv_types import VonMisesDistribution
    assert _test_args(VonMisesDistribution(1, 1))


def test_sympy__stats__crv_types__WeibullDistribution():
    from sympy.stats.crv_types import WeibullDistribution
    assert _test_args(WeibullDistribution(1, 1))


def test_sympy__stats__crv_types__WignerSemicircleDistribution():
    from sympy.stats.crv_types import WignerSemicircleDistribution
    assert _test_args(WignerSemicircleDistribution(1))

def test_sympy__stats__drv_types__PoissonDistribution():
    from sympy.stats.drv_types import PoissonDistribution
    assert _test_args(PoissonDistribution(1))

def test_sympy__stats__drv_types__GeometricDistribution():
    from sympy.stats.drv_types import GeometricDistribution
    assert _test_args(GeometricDistribution(.5))

def test_sympy__core__symbol__Dummy():
    from sympy.core.symbol import Dummy
    assert _test_args(Dummy('t'))


def test_sympy__core__symbol__Symbol():
    from sympy.core.symbol import Symbol
    assert _test_args(Symbol('t'))


def test_sympy__core__symbol__Wild():
    from sympy.core.symbol import Wild
    assert _test_args(Wild('x', exclude=[x]))


@SKIP("abstract class")
def test_sympy__functions__combinatorial__factorials__CombinatorialFunction():
    pass


def test_sympy__functions__combinatorial__factorials__FallingFactorial():
    from sympy.functions.combinatorial.factorials import FallingFactorial
    assert _test_args(FallingFactorial(2, x))


def test_sympy__functions__combinatorial__factorials__MultiFactorial():
    from sympy.functions.combinatorial.factorials import MultiFactorial
    assert _test_args(MultiFactorial(x))


def test_sympy__functions__combinatorial__factorials__RisingFactorial():
    from sympy.functions.combinatorial.factorials import RisingFactorial
    assert _test_args(RisingFactorial(2, x))


def test_sympy__functions__combinatorial__factorials__binomial():
    from sympy.functions.combinatorial.factorials import binomial
    assert _test_args(binomial(2, x))


def test_sympy__functions__combinatorial__factorials__subfactorial():
    from sympy.functions.combinatorial.factorials import subfactorial
    assert _test_args(subfactorial(1))


def test_sympy__functions__combinatorial__factorials__factorial():
    from sympy.functions.combinatorial.factorials import factorial
    assert _test_args(factorial(x))


def test_sympy__functions__combinatorial__factorials__factorial2():
    from sympy.functions.combinatorial.factorials import factorial2
    assert _test_args(factorial2(x))


def test_sympy__functions__combinatorial__numbers__bell():
    from sympy.functions.combinatorial.numbers import bell
    assert _test_args(bell(x, y))


def test_sympy__functions__combinatorial__numbers__bernoulli():
    from sympy.functions.combinatorial.numbers import bernoulli
    assert _test_args(bernoulli(x))


def test_sympy__functions__combinatorial__numbers__catalan():
    from sympy.functions.combinatorial.numbers import catalan
    assert _test_args(catalan(x))


def test_sympy__functions__combinatorial__numbers__euler():
    from sympy.functions.combinatorial.numbers import euler
    assert _test_args(euler(x))


def test_sympy__functions__combinatorial__numbers__fibonacci():
    from sympy.functions.combinatorial.numbers import fibonacci
    assert _test_args(fibonacci(x))


def test_sympy__functions__combinatorial__numbers__harmonic():
    from sympy.functions.combinatorial.numbers import harmonic
    assert _test_args(harmonic(x, 2))


def test_sympy__functions__combinatorial__numbers__lucas():
    from sympy.functions.combinatorial.numbers import lucas
    assert _test_args(lucas(x))


def test_sympy__functions__elementary__complexes__Abs():
    from sympy.functions.elementary.complexes import Abs
    assert _test_args(Abs(x))


def test_sympy__functions__elementary__complexes__adjoint():
    from sympy.functions.elementary.complexes import adjoint
    assert _test_args(adjoint(x))


def test_sympy__functions__elementary__complexes__arg():
    from sympy.functions.elementary.complexes import arg
    assert _test_args(arg(x))


def test_sympy__functions__elementary__complexes__conjugate():
    from sympy.functions.elementary.complexes import conjugate
    assert _test_args(conjugate(x))


def test_sympy__functions__elementary__complexes__im():
    from sympy.functions.elementary.complexes import im
    assert _test_args(im(x))


def test_sympy__functions__elementary__complexes__re():
    from sympy.functions.elementary.complexes import re
    assert _test_args(re(x))


def test_sympy__functions__elementary__complexes__sign():
    from sympy.functions.elementary.complexes import sign
    assert _test_args(sign(x))


def test_sympy__functions__elementary__complexes__polar_lift():
    from sympy.functions.elementary.complexes import polar_lift
    assert _test_args(polar_lift(x))


def test_sympy__functions__elementary__complexes__periodic_argument():
    from sympy.functions.elementary.complexes import periodic_argument
    assert _test_args(periodic_argument(x, y))


def test_sympy__functions__elementary__complexes__principal_branch():
    from sympy.functions.elementary.complexes import principal_branch
    assert _test_args(principal_branch(x, y))


def test_sympy__functions__elementary__complexes__transpose():
    from sympy.functions.elementary.complexes import transpose
    assert _test_args(transpose(x))


def test_sympy__functions__elementary__exponential__LambertW():
    from sympy.functions.elementary.exponential import LambertW
    assert _test_args(LambertW(2))


@SKIP("abstract class")
def test_sympy__functions__elementary__exponential__ExpBase():
    pass


def test_sympy__functions__elementary__exponential__exp():
    from sympy.functions.elementary.exponential import exp
    assert _test_args(exp(2))


def test_sympy__functions__elementary__exponential__exp_polar():
    from sympy.functions.elementary.exponential import exp_polar
    assert _test_args(exp_polar(2))


def test_sympy__functions__elementary__exponential__log():
    from sympy.functions.elementary.exponential import log
    assert _test_args(log(2))


@SKIP("abstract class")
def test_sympy__functions__elementary__hyperbolic__HyperbolicFunction():
    pass


def test_sympy__functions__elementary__hyperbolic__acosh():
    from sympy.functions.elementary.hyperbolic import acosh
    assert _test_args(acosh(2))


def test_sympy__functions__elementary__hyperbolic__acoth():
    from sympy.functions.elementary.hyperbolic import acoth
    assert _test_args(acoth(2))


def test_sympy__functions__elementary__hyperbolic__asinh():
    from sympy.functions.elementary.hyperbolic import asinh
    assert _test_args(asinh(2))


def test_sympy__functions__elementary__hyperbolic__atanh():
    from sympy.functions.elementary.hyperbolic import atanh
    assert _test_args(atanh(2))


def test_sympy__functions__elementary__hyperbolic__cosh():
    from sympy.functions.elementary.hyperbolic import cosh
    assert _test_args(cosh(2))


def test_sympy__functions__elementary__hyperbolic__coth():
    from sympy.functions.elementary.hyperbolic import coth
    assert _test_args(coth(2))


def test_sympy__functions__elementary__hyperbolic__sinh():
    from sympy.functions.elementary.hyperbolic import sinh
    assert _test_args(sinh(2))


def test_sympy__functions__elementary__hyperbolic__tanh():
    from sympy.functions.elementary.hyperbolic import tanh
    assert _test_args(tanh(2))


@SKIP("does this work at all?")
def test_sympy__functions__elementary__integers__RoundFunction():
    from sympy.functions.elementary.integers import RoundFunction
    assert _test_args(RoundFunction())


def test_sympy__functions__elementary__integers__ceiling():
    from sympy.functions.elementary.integers import ceiling
    assert _test_args(ceiling(x))


def test_sympy__functions__elementary__integers__floor():
    from sympy.functions.elementary.integers import floor
    assert _test_args(floor(x))


def test_sympy__functions__elementary__miscellaneous__IdentityFunction():
    from sympy.functions.elementary.miscellaneous import IdentityFunction
    assert _test_args(IdentityFunction())


def test_sympy__functions__elementary__miscellaneous__Max():
    from sympy.functions.elementary.miscellaneous import Max
    assert _test_args(Max(x, 2))


def test_sympy__functions__elementary__miscellaneous__Min():
    from sympy.functions.elementary.miscellaneous import Min
    assert _test_args(Min(x, 2))


@SKIP("abstract class")
def test_sympy__functions__elementary__miscellaneous__MinMaxBase():
    pass


def test_sympy__functions__elementary__piecewise__ExprCondPair():
    from sympy.functions.elementary.piecewise import ExprCondPair
    assert _test_args(ExprCondPair(1, True))


def test_sympy__functions__elementary__piecewise__Piecewise():
    from sympy.functions.elementary.piecewise import Piecewise
    assert _test_args(Piecewise((1, x >= 0), (0, True)))


@SKIP("abstract class")
def test_sympy__functions__elementary__trigonometric__TrigonometricFunction():
    pass

@SKIP("abstract class")
def test_sympy__functions__elementary__trigonometric__ReciprocalTrigonometricFunction():
    pass

def test_sympy__functions__elementary__trigonometric__acos():
    from sympy.functions.elementary.trigonometric import acos
    assert _test_args(acos(2))


def test_sympy__functions__elementary__trigonometric__acot():
    from sympy.functions.elementary.trigonometric import acot
    assert _test_args(acot(2))


def test_sympy__functions__elementary__trigonometric__asin():
    from sympy.functions.elementary.trigonometric import asin
    assert _test_args(asin(2))


def test_sympy__functions__elementary__trigonometric__atan():
    from sympy.functions.elementary.trigonometric import atan
    assert _test_args(atan(2))


def test_sympy__functions__elementary__trigonometric__atan2():
    from sympy.functions.elementary.trigonometric import atan2
    assert _test_args(atan2(2, 3))


def test_sympy__functions__elementary__trigonometric__cos():
    from sympy.functions.elementary.trigonometric import cos
    assert _test_args(cos(2))


def test_sympy__functions__elementary__trigonometric__csc():
    from sympy.functions.elementary.trigonometric import csc
    assert _test_args(csc(2))


def test_sympy__functions__elementary__trigonometric__cot():
    from sympy.functions.elementary.trigonometric import cot
    assert _test_args(cot(2))


def test_sympy__functions__elementary__trigonometric__sin():
    assert _test_args(sin(2))


def test_sympy__functions__elementary__trigonometric__sec():
    from sympy.functions.elementary.trigonometric import sec
    assert _test_args(sec(2))


def test_sympy__functions__elementary__trigonometric__tan():
    from sympy.functions.elementary.trigonometric import tan
    assert _test_args(tan(2))


@SKIP("abstract class")
def test_sympy__functions__special__bessel__BesselBase():
    pass


@SKIP("abstract class")
def test_sympy__functions__special__bessel__SphericalBesselBase():
    pass


def test_sympy__functions__special__bessel__besseli():
    from sympy.functions.special.bessel import besseli
    assert _test_args(besseli(x, 1))


def test_sympy__functions__special__bessel__besselj():
    from sympy.functions.special.bessel import besselj
    assert _test_args(besselj(x, 1))


def test_sympy__functions__special__bessel__besselk():
    from sympy.functions.special.bessel import besselk
    assert _test_args(besselk(x, 1))


def test_sympy__functions__special__bessel__bessely():
    from sympy.functions.special.bessel import bessely
    assert _test_args(bessely(x, 1))


def test_sympy__functions__special__bessel__hankel1():
    from sympy.functions.special.bessel import hankel1
    assert _test_args(hankel1(x, 1))


def test_sympy__functions__special__bessel__hankel2():
    from sympy.functions.special.bessel import hankel2
    assert _test_args(hankel2(x, 1))


def test_sympy__functions__special__bessel__jn():
    from sympy.functions.special.bessel import jn
    assert _test_args(jn(0, x))


def test_sympy__functions__special__bessel__yn():
    from sympy.functions.special.bessel import yn
    assert _test_args(yn(0, x))


def test_sympy__functions__special__elliptic_integrals__elliptic_k():
    from sympy.functions.special.elliptic_integrals import elliptic_k as K
    assert _test_args(K(x))


def test_sympy__functions__special__elliptic_integrals__elliptic_f():
    from sympy.functions.special.elliptic_integrals import elliptic_f as F
    assert _test_args(F(x, y))


def test_sympy__functions__special__elliptic_integrals__elliptic_e():
    from sympy.functions.special.elliptic_integrals import elliptic_e as E
    assert _test_args(E(x))
    assert _test_args(E(x, y))


def test_sympy__functions__special__elliptic_integrals__elliptic_pi():
    from sympy.functions.special.elliptic_integrals import elliptic_pi as P
    assert _test_args(P(x, y))
    assert _test_args(P(x, y, z))


def test_sympy__functions__special__delta_functions__DiracDelta():
    from sympy.functions.special.delta_functions import DiracDelta
    assert _test_args(DiracDelta(x, 1))


def test_sympy__functions__special__delta_functions__Heaviside():
    from sympy.functions.special.delta_functions import Heaviside
    assert _test_args(Heaviside(x))


def test_sympy__functions__special__error_functions__erf():
    from sympy.functions.special.error_functions import erf
    assert _test_args(erf(2))

def test_sympy__functions__special__error_functions__erfc():
    from sympy.functions.special.error_functions import erfc
    assert _test_args(erfc(2))

def test_sympy__functions__special__error_functions__erfi():
    from sympy.functions.special.error_functions import erfi
    assert _test_args(erfi(2))

def test_sympy__functions__special__error_functions__erf2():
    from sympy.functions.special.error_functions import erf2
    assert _test_args(erf2(2, 3))

def test_sympy__functions__special__error_functions__erfinv():
    from sympy.functions.special.error_functions import erfinv
    assert _test_args(erfinv(2))

def test_sympy__functions__special__error_functions__erfcinv():
    from sympy.functions.special.error_functions import erfcinv
    assert _test_args(erfcinv(2))

def test_sympy__functions__special__error_functions__erf2inv():
    from sympy.functions.special.error_functions import erf2inv
    assert _test_args(erf2inv(2, 3))

@SKIP("abstract class")
def test_sympy__functions__special__error_functions__FresnelIntegral():
    pass


def test_sympy__functions__special__error_functions__fresnels():
    from sympy.functions.special.error_functions import fresnels
    assert _test_args(fresnels(2))


def test_sympy__functions__special__error_functions__fresnelc():
    from sympy.functions.special.error_functions import fresnelc
    assert _test_args(fresnelc(2))


def test_sympy__functions__special__error_functions__erfs():
    from sympy.functions.special.error_functions import _erfs
    assert _test_args(_erfs(2))


def test_sympy__functions__special__error_functions__Ei():
    from sympy.functions.special.error_functions import Ei
    assert _test_args(Ei(2))


def test_sympy__functions__special__error_functions__li():
    from sympy.functions.special.error_functions import li
    assert _test_args(li(2))


def test_sympy__functions__special__error_functions__Li():
    from sympy.functions.special.error_functions import Li
    assert _test_args(Li(2))


@SKIP("abstract class")
def test_sympy__functions__special__error_functions__TrigonometricIntegral():
    pass


def test_sympy__functions__special__error_functions__Si():
    from sympy.functions.special.error_functions import Si
    assert _test_args(Si(2))


def test_sympy__functions__special__error_functions__Ci():
    from sympy.functions.special.error_functions import Ci
    assert _test_args(Ci(2))


def test_sympy__functions__special__error_functions__Shi():
    from sympy.functions.special.error_functions import Shi
    assert _test_args(Shi(2))


def test_sympy__functions__special__error_functions__Chi():
    from sympy.functions.special.error_functions import Chi
    assert _test_args(Chi(2))


def test_sympy__functions__special__error_functions__expint():
    from sympy.functions.special.error_functions import expint
    assert _test_args(expint(y, x))


def test_sympy__functions__special__gamma_functions__gamma():
    from sympy.functions.special.gamma_functions import gamma
    assert _test_args(gamma(x))


def test_sympy__functions__special__gamma_functions__loggamma():
    from sympy.functions.special.gamma_functions import loggamma
    assert _test_args(loggamma(2))


def test_sympy__functions__special__gamma_functions__lowergamma():
    from sympy.functions.special.gamma_functions import lowergamma
    assert _test_args(lowergamma(x, 2))


def test_sympy__functions__special__gamma_functions__polygamma():
    from sympy.functions.special.gamma_functions import polygamma
    assert _test_args(polygamma(x, 2))


def test_sympy__functions__special__gamma_functions__uppergamma():
    from sympy.functions.special.gamma_functions import uppergamma
    assert _test_args(uppergamma(x, 2))


@SKIP("abstract class")
def test_sympy__functions__special__hyper__TupleParametersBase():
    pass


@SKIP("abstract class")
def test_sympy__functions__special__hyper__TupleArg():
    pass


def test_sympy__functions__special__hyper__hyper():
    from sympy.functions.special.hyper import hyper
    assert _test_args(hyper([1, 2, 3], [4, 5], x))


def test_sympy__functions__special__hyper__meijerg():
    from sympy.functions.special.hyper import meijerg
    assert _test_args(meijerg([1, 2, 3], [4, 5], [6], [], x))


@SKIP("abstract class")
def test_sympy__functions__special__hyper__HyperRep():
    pass


def test_sympy__functions__special__hyper__HyperRep_power1():
    from sympy.functions.special.hyper import HyperRep_power1
    assert _test_args(HyperRep_power1(x, y))


def test_sympy__functions__special__hyper__HyperRep_power2():
    from sympy.functions.special.hyper import HyperRep_power2
    assert _test_args(HyperRep_power2(x, y))


def test_sympy__functions__special__hyper__HyperRep_log1():
    from sympy.functions.special.hyper import HyperRep_log1
    assert _test_args(HyperRep_log1(x))


def test_sympy__functions__special__hyper__HyperRep_atanh():
    from sympy.functions.special.hyper import HyperRep_atanh
    assert _test_args(HyperRep_atanh(x))


def test_sympy__functions__special__hyper__HyperRep_asin1():
    from sympy.functions.special.hyper import HyperRep_asin1
    assert _test_args(HyperRep_asin1(x))


def test_sympy__functions__special__hyper__HyperRep_asin2():
    from sympy.functions.special.hyper import HyperRep_asin2
    assert _test_args(HyperRep_asin2(x))


def test_sympy__functions__special__hyper__HyperRep_sqrts1():
    from sympy.functions.special.hyper import HyperRep_sqrts1
    assert _test_args(HyperRep_sqrts1(x, y))


def test_sympy__functions__special__hyper__HyperRep_sqrts2():
    from sympy.functions.special.hyper import HyperRep_sqrts2
    assert _test_args(HyperRep_sqrts2(x, y))


def test_sympy__functions__special__hyper__HyperRep_log2():
    from sympy.functions.special.hyper import HyperRep_log2
    assert _test_args(HyperRep_log2(x))


def test_sympy__functions__special__hyper__HyperRep_cosasin():
    from sympy.functions.special.hyper import HyperRep_cosasin
    assert _test_args(HyperRep_cosasin(x, y))


def test_sympy__functions__special__hyper__HyperRep_sinasin():
    from sympy.functions.special.hyper import HyperRep_sinasin
    assert _test_args(HyperRep_sinasin(x, y))


@SKIP("abstract class")
def test_sympy__functions__special__polynomials__OrthogonalPolynomial():
    pass


def test_sympy__functions__special__polynomials__jacobi():
    from sympy.functions.special.polynomials import jacobi
    assert _test_args(jacobi(x, 2, 2, 2))


def test_sympy__functions__special__polynomials__gegenbauer():
    from sympy.functions.special.polynomials import gegenbauer
    assert _test_args(gegenbauer(x, 2, 2))


def test_sympy__functions__special__polynomials__chebyshevt():
    from sympy.functions.special.polynomials import chebyshevt
    assert _test_args(chebyshevt(x, 2))


def test_sympy__functions__special__polynomials__chebyshevt_root():
    from sympy.functions.special.polynomials import chebyshevt_root
    assert _test_args(chebyshevt_root(3, 2))


def test_sympy__functions__special__polynomials__chebyshevu():
    from sympy.functions.special.polynomials import chebyshevu
    assert _test_args(chebyshevu(x, 2))


def test_sympy__functions__special__polynomials__chebyshevu_root():
    from sympy.functions.special.polynomials import chebyshevu_root
    assert _test_args(chebyshevu_root(3, 2))


def test_sympy__functions__special__polynomials__hermite():
    from sympy.functions.special.polynomials import hermite
    assert _test_args(hermite(x, 2))


def test_sympy__functions__special__polynomials__legendre():
    from sympy.functions.special.polynomials import legendre
    assert _test_args(legendre(x, 2))


def test_sympy__functions__special__polynomials__assoc_legendre():
    from sympy.functions.special.polynomials import assoc_legendre
    assert _test_args(assoc_legendre(x, 0, y))


def test_sympy__functions__special__polynomials__laguerre():
    from sympy.functions.special.polynomials import laguerre
    assert _test_args(laguerre(x, 2))


def test_sympy__functions__special__polynomials__assoc_laguerre():
    from sympy.functions.special.polynomials import assoc_laguerre
    assert _test_args(assoc_laguerre(x, 0, y))


def test_sympy__functions__special__spherical_harmonics__Ynm():
    from sympy.functions.special.spherical_harmonics import Ynm
    assert _test_args(Ynm(1, 1, x, y))


def test_sympy__functions__special__spherical_harmonics__Znm():
    from sympy.functions.special.spherical_harmonics import Znm
    assert _test_args(Znm(1, 1, x, y))


def test_sympy__functions__special__tensor_functions__LeviCivita():
    from sympy.functions.special.tensor_functions import LeviCivita
    assert _test_args(LeviCivita(x, y, 2))


def test_sympy__functions__special__tensor_functions__KroneckerDelta():
    from sympy.functions.special.tensor_functions import KroneckerDelta
    assert _test_args(KroneckerDelta(x, y))


def test_sympy__functions__special__zeta_functions__dirichlet_eta():
    from sympy.functions.special.zeta_functions import dirichlet_eta
    assert _test_args(dirichlet_eta(x))


def test_sympy__functions__special__zeta_functions__zeta():
    from sympy.functions.special.zeta_functions import zeta
    assert _test_args(zeta(101))


def test_sympy__functions__special__zeta_functions__lerchphi():
    from sympy.functions.special.zeta_functions import lerchphi
    assert _test_args(lerchphi(x, y, z))


def test_sympy__functions__special__zeta_functions__polylog():
    from sympy.functions.special.zeta_functions import polylog
    assert _test_args(polylog(x, y))


def test_sympy__integrals__integrals__Integral():
    from sympy.integrals.integrals import Integral
    assert _test_args(Integral(2, (x, 0, 1)))


def test_sympy__integrals__risch__NonElementaryIntegral():
    from sympy.integrals.risch import NonElementaryIntegral
    assert _test_args(NonElementaryIntegral(exp(-x**2), x))


@SKIP("abstract class")
def test_sympy__integrals__transforms__IntegralTransform():
    pass


def test_sympy__integrals__transforms__MellinTransform():
    from sympy.integrals.transforms import MellinTransform
    assert _test_args(MellinTransform(2, x, y))


def test_sympy__integrals__transforms__InverseMellinTransform():
    from sympy.integrals.transforms import InverseMellinTransform
    assert _test_args(InverseMellinTransform(2, x, y, 0, 1))


def test_sympy__integrals__transforms__LaplaceTransform():
    from sympy.integrals.transforms import LaplaceTransform
    assert _test_args(LaplaceTransform(2, x, y))


def test_sympy__integrals__transforms__InverseLaplaceTransform():
    from sympy.integrals.transforms import InverseLaplaceTransform
    assert _test_args(InverseLaplaceTransform(2, x, y, 0))


@SKIP("abstract class")
def test_sympy__integrals__transforms__FourierTypeTransform():
    pass


def test_sympy__integrals__transforms__InverseFourierTransform():
    from sympy.integrals.transforms import InverseFourierTransform
    assert _test_args(InverseFourierTransform(2, x, y))


def test_sympy__integrals__transforms__FourierTransform():
    from sympy.integrals.transforms import FourierTransform
    assert _test_args(FourierTransform(2, x, y))


@SKIP("abstract class")
def test_sympy__integrals__transforms__SineCosineTypeTransform():
    pass


def test_sympy__integrals__transforms__InverseSineTransform():
    from sympy.integrals.transforms import InverseSineTransform
    assert _test_args(InverseSineTransform(2, x, y))


def test_sympy__integrals__transforms__SineTransform():
    from sympy.integrals.transforms import SineTransform
    assert _test_args(SineTransform(2, x, y))


def test_sympy__integrals__transforms__InverseCosineTransform():
    from sympy.integrals.transforms import InverseCosineTransform
    assert _test_args(InverseCosineTransform(2, x, y))


def test_sympy__integrals__transforms__CosineTransform():
    from sympy.integrals.transforms import CosineTransform
    assert _test_args(CosineTransform(2, x, y))


@SKIP("abstract class")
def test_sympy__integrals__transforms__HankelTypeTransform():
    pass


def test_sympy__integrals__transforms__InverseHankelTransform():
    from sympy.integrals.transforms import InverseHankelTransform
    assert _test_args(InverseHankelTransform(2, x, y, 0))


def test_sympy__integrals__transforms__HankelTransform():
    from sympy.integrals.transforms import HankelTransform
    assert _test_args(HankelTransform(2, x, y, 0))

@XFAIL
def test_sympy__liealgebras__cartan_type__CartanType_generator():
    from sympy.liealgebras.cartan_type import CartanType_generator
    assert _test_args(CartanType_generator("A2"))

@XFAIL
def test_sympy__liealgebras__cartan_type__Standard_Cartan():
    from sympy.liealgebras.cartan_type import Standard_Cartan
    assert _test_args(Standard_Cartan("A", 2))

@XFAIL
def test_sympy__liealgebras__weyl_group__WeylGroup():
    from sympy.liealgebras.weyl_group import WeylGroup
    assert _test_args(WeylGroup("B4"))

@XFAIL
def test_sympy__liealgebras__root_system__RootSystem():
    from sympy.liealgebras.root_system import RootSyStem
    assert _test_args(RootSystem("A2"))

@XFAIL
def test_sympy__liealgebras__type_a__TypeA():
    from sympy.liealgebras.type_a import TypeA
    assert _test_args(TypeA(2))

@XFAIL
def test_sympy__liealgebras__type_b__TypeB():
    from sympy.liealgebras.type_b import TypeB
    assert _test_args(TypeB(4))

@XFAIL
def test_sympy__liealgebras__type_c__TypeC():
    from sympy.liealgebras.type_c import TypeC
    assert _test_args(TypeC(4))

@XFAIL
def test_sympy__liealgebras__type_d__TypeD():
    from sympy.liealgebras.type_d import TypeD
    assert _test_args(TypeD(4))

@XFAIL
def test_sympy__liealgebras__type_e__TypeE():
    from sympy.liealgebras.type_e import TypeE
    assert _test_args(TypeE(6))

@XFAIL
def test_sympy__liealgebras__type_f__TypeF():
    from sympy.liealgebras.type_f import TypeF
    assert _test_args(TypeF(4))

@XFAIL
def test_sympy__liealgebras__type_g__TypeG():
    from sympy.liealgebras.type_g import TypeG
    assert _test_args(TypeG(2))


def test_sympy__logic__boolalg__And():
    from sympy.logic.boolalg import And
    assert _test_args(And(x, y, 2))


@SKIP("abstract class")
def test_sympy__logic__boolalg__Boolean():
    pass


def test_sympy__logic__boolalg__BooleanFunction():
    from sympy.logic.boolalg import BooleanFunction
    assert _test_args(BooleanFunction(1, 2, 3))

@SKIP("abstract class")
def test_sympy__logic__boolalg__BooleanAtom():
    pass

def test_sympy__logic__boolalg__BooleanTrue():
    from sympy.logic.boolalg import true
    assert _test_args(true)

def test_sympy__logic__boolalg__BooleanFalse():
    from sympy.logic.boolalg import false
    assert _test_args(false)

def test_sympy__logic__boolalg__Equivalent():
    from sympy.logic.boolalg import Equivalent
    assert _test_args(Equivalent(x, 2))


def test_sympy__logic__boolalg__ITE():
    from sympy.logic.boolalg import ITE
    assert _test_args(ITE(x, y, 2))


def test_sympy__logic__boolalg__Implies():
    from sympy.logic.boolalg import Implies
    assert _test_args(Implies(x, y))


def test_sympy__logic__boolalg__Nand():
    from sympy.logic.boolalg import Nand
    assert _test_args(Nand(x, y, 2))


def test_sympy__logic__boolalg__Nor():
    from sympy.logic.boolalg import Nor
    assert _test_args(Nor(x, y))


def test_sympy__logic__boolalg__Not():
    from sympy.logic.boolalg import Not
    assert _test_args(Not(x))


def test_sympy__logic__boolalg__Or():
    from sympy.logic.boolalg import Or
    assert _test_args(Or(x, y))


def test_sympy__logic__boolalg__Xor():
    from sympy.logic.boolalg import Xor
    assert _test_args(Xor(x, y, 2))


def test_sympy__matrices__matrices__DeferredVector():
    from sympy.matrices.matrices import DeferredVector
    assert _test_args(DeferredVector("X"))


@SKIP("abstract class")
def test_sympy__matrices__expressions__matexpr__MatrixBase():
    pass


def test_sympy__matrices__immutable__ImmutableMatrix():
    from sympy.matrices.immutable import ImmutableMatrix
    assert _test_args(ImmutableMatrix([[1, 2], [3, 4]]))


def test_sympy__matrices__immutable__ImmutableSparseMatrix():
    from sympy.matrices.immutable import ImmutableSparseMatrix
    assert _test_args(ImmutableSparseMatrix([[1, 2], [3, 4]]))


def test_sympy__matrices__expressions__slice__MatrixSlice():
    from sympy.matrices.expressions.slice import MatrixSlice
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', 4, 4)
    assert _test_args(MatrixSlice(X, (0, 2), (0, 2)))


def test_sympy__matrices__expressions__blockmatrix__BlockDiagMatrix():
    from sympy.matrices.expressions.blockmatrix import BlockDiagMatrix
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', x, x)
    Y = MatrixSymbol('Y', y, y)
    assert _test_args(BlockDiagMatrix(X, Y))


def test_sympy__matrices__expressions__blockmatrix__BlockMatrix():
    from sympy.matrices.expressions.blockmatrix import BlockMatrix
    from sympy.matrices.expressions import MatrixSymbol, ZeroMatrix
    X = MatrixSymbol('X', x, x)
    Y = MatrixSymbol('Y', y, y)
    Z = MatrixSymbol('Z', x, y)
    O = ZeroMatrix(y, x)
    assert _test_args(BlockMatrix([[X, Z], [O, Y]]))


def test_sympy__matrices__expressions__inverse__Inverse():
    from sympy.matrices.expressions.inverse import Inverse
    from sympy.matrices.expressions import MatrixSymbol
    assert _test_args(Inverse(MatrixSymbol('A', 3, 3)))


def test_sympy__matrices__expressions__matadd__MatAdd():
    from sympy.matrices.expressions.matadd import MatAdd
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', x, y)
    Y = MatrixSymbol('Y', x, y)
    assert _test_args(MatAdd(X, Y))


@XFAIL
def test_sympy__matrices__expressions__matexpr__Identity():
    from sympy.matrices.expressions.matexpr import Identity
    assert _test_args(Identity(3))


@SKIP("abstract class")
def test_sympy__matrices__expressions__matexpr__MatrixExpr():
    pass

def test_sympy__matrices__expressions__matexpr__MatrixElement():
    from sympy.matrices.expressions.matexpr import MatrixSymbol, MatrixElement
    from sympy import S
    assert _test_args(MatrixElement(MatrixSymbol('A', 3, 5), S(2), S(3)))

@XFAIL
def test_sympy__matrices__expressions__matexpr__MatrixSymbol():
    from sympy.matrices.expressions.matexpr import MatrixSymbol
    assert _test_args(MatrixSymbol('A', 3, 5))


@XFAIL
def test_sympy__matrices__expressions__matexpr__ZeroMatrix():
    from sympy.matrices.expressions.matexpr import ZeroMatrix
    assert _test_args(ZeroMatrix(3, 5))


def test_sympy__matrices__expressions__matmul__MatMul():
    from sympy.matrices.expressions.matmul import MatMul
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', x, y)
    Y = MatrixSymbol('Y', y, x)
    assert _test_args(MatMul(X, Y))

def test_sympy__matrices__expressions__diagonal__DiagonalMatrix():
    from sympy.matrices.expressions.diagonal import DiagonalMatrix
    from sympy.matrices.expressions import MatrixSymbol
    x = MatrixSymbol('x', 10, 1)
    assert _test_args(DiagonalMatrix(x))

def test_sympy__matrices__expressions__diagonal__DiagonalOf():
    from sympy.matrices.expressions.diagonal import DiagonalOf
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('x', 10, 10)
    assert _test_args(DiagonalOf(X))

def test_sympy__matrices__expressions__hadamard__HadamardProduct():
    from sympy.matrices.expressions.hadamard import HadamardProduct
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', x, y)
    Y = MatrixSymbol('Y', x, y)
    assert _test_args(HadamardProduct(X, Y))


def test_sympy__matrices__expressions__matpow__MatPow():
    from sympy.matrices.expressions.matpow import MatPow
    from sympy.matrices.expressions import MatrixSymbol
    X = MatrixSymbol('X', x, x)
    assert _test_args(MatPow(X, 2))


def test_sympy__matrices__expressions__transpose__Transpose():
    from sympy.matrices.expressions.transpose import Transpose
    from sympy.matrices.expressions import MatrixSymbol
    assert _test_args(Transpose(MatrixSymbol('A', 3, 5)))


def test_sympy__matrices__expressions__adjoint__Adjoint():
    from sympy.matrices.expressions.adjoint import Adjoint
    from sympy.matrices.expressions import MatrixSymbol
    assert _test_args(Adjoint(MatrixSymbol('A', 3, 5)))


def test_sympy__matrices__expressions__trace__Trace():
    from sympy.matrices.expressions.trace import Trace
    from sympy.matrices.expressions import MatrixSymbol
    assert _test_args(Trace(MatrixSymbol('A', 3, 3)))

def test_sympy__matrices__expressions__determinant__Determinant():
    from sympy.matrices.expressions.determinant import Determinant
    from sympy.matrices.expressions import MatrixSymbol
    assert _test_args(Determinant(MatrixSymbol('A', 3, 3)))


def test_sympy__matrices__expressions__funcmatrix__FunctionMatrix():
    from sympy.matrices.expressions.funcmatrix import FunctionMatrix
    from sympy import Lambda, symbols
    i, j = symbols('i,j')
    assert _test_args(FunctionMatrix(3, 3, Lambda((i, j), i - j) ))

def test_sympy__matrices__expressions__fourier__DFT():
    from sympy.matrices.expressions.fourier import DFT
    from sympy import S
    assert _test_args(DFT(S(2)))

def test_sympy__matrices__expressions__fourier__IDFT():
    from sympy.matrices.expressions.fourier import IDFT
    from sympy import S
    assert _test_args(IDFT(S(2)))

from sympy.matrices.expressions import MatrixSymbol
X = MatrixSymbol('X', 10, 10)

def test_sympy__matrices__expressions__factorizations__LofLU():
    from sympy.matrices.expressions.factorizations import LofLU
    assert _test_args(LofLU(X))

def test_sympy__matrices__expressions__factorizations__UofLU():
    from sympy.matrices.expressions.factorizations import UofLU
    assert _test_args(UofLU(X))

def test_sympy__matrices__expressions__factorizations__QofQR():
    from sympy.matrices.expressions.factorizations import QofQR
    assert _test_args(QofQR(X))

def test_sympy__matrices__expressions__factorizations__RofQR():
    from sympy.matrices.expressions.factorizations import RofQR
    assert _test_args(RofQR(X))

def test_sympy__matrices__expressions__factorizations__LofCholesky():
    from sympy.matrices.expressions.factorizations import LofCholesky
    assert _test_args(LofCholesky(X))

def test_sympy__matrices__expressions__factorizations__UofCholesky():
    from sympy.matrices.expressions.factorizations import UofCholesky
    assert _test_args(UofCholesky(X))

def test_sympy__matrices__expressions__factorizations__EigenVectors():
    from sympy.matrices.expressions.factorizations import EigenVectors
    assert _test_args(EigenVectors(X))

def test_sympy__matrices__expressions__factorizations__EigenValues():
    from sympy.matrices.expressions.factorizations import EigenValues
    assert _test_args(EigenValues(X))

def test_sympy__matrices__expressions__factorizations__UofSVD():
    from sympy.matrices.expressions.factorizations import UofSVD
    assert _test_args(UofSVD(X))

def test_sympy__matrices__expressions__factorizations__VofSVD():
    from sympy.matrices.expressions.factorizations import VofSVD
    assert _test_args(VofSVD(X))

def test_sympy__matrices__expressions__factorizations__SofSVD():
    from sympy.matrices.expressions.factorizations import SofSVD
    assert _test_args(SofSVD(X))

@SKIP("abstract class")
def test_sympy__matrices__expressions__factorizations__Factorization():
    pass

def test_sympy__physics__mechanics__essential__CoordinateSym():
    from sympy.physics.mechanics import CoordinateSym
    from sympy.physics.mechanics import ReferenceFrame
    assert _test_args(CoordinateSym('R_x', ReferenceFrame('R'), 0))

def test_sympy__physics__gaussopt__BeamParameter():
    from sympy.physics.gaussopt import BeamParameter
    assert _test_args(BeamParameter(530e-9, 1, w=1e-3))


def test_sympy__physics__paulialgebra__Pauli():
    from sympy.physics.paulialgebra import Pauli
    assert _test_args(Pauli(1))


def test_sympy__physics__quantum__anticommutator__AntiCommutator():
    from sympy.physics.quantum.anticommutator import AntiCommutator
    assert _test_args(AntiCommutator(x, y))


def test_sympy__physics__quantum__cartesian__PositionBra3D():
    from sympy.physics.quantum.cartesian import PositionBra3D
    assert _test_args(PositionBra3D(x, y, z))


def test_sympy__physics__quantum__cartesian__PositionKet3D():
    from sympy.physics.quantum.cartesian import PositionKet3D
    assert _test_args(PositionKet3D(x, y, z))


def test_sympy__physics__quantum__cartesian__PositionState3D():
    from sympy.physics.quantum.cartesian import PositionState3D
    assert _test_args(PositionState3D(x, y, z))


def test_sympy__physics__quantum__cartesian__PxBra():
    from sympy.physics.quantum.cartesian import PxBra
    assert _test_args(PxBra(x, y, z))


def test_sympy__physics__quantum__cartesian__PxKet():
    from sympy.physics.quantum.cartesian import PxKet
    assert _test_args(PxKet(x, y, z))


def test_sympy__physics__quantum__cartesian__PxOp():
    from sympy.physics.quantum.cartesian import PxOp
    assert _test_args(PxOp(x, y, z))


def test_sympy__physics__quantum__cartesian__XBra():
    from sympy.physics.quantum.cartesian import XBra
    assert _test_args(XBra(x))


def test_sympy__physics__quantum__cartesian__XKet():
    from sympy.physics.quantum.cartesian import XKet
    assert _test_args(XKet(x))


def test_sympy__physics__quantum__cartesian__XOp():
    from sympy.physics.quantum.cartesian import XOp
    assert _test_args(XOp(x))


def test_sympy__physics__quantum__cartesian__YOp():
    from sympy.physics.quantum.cartesian import YOp
    assert _test_args(YOp(x))


def test_sympy__physics__quantum__cartesian__ZOp():
    from sympy.physics.quantum.cartesian import ZOp
    assert _test_args(ZOp(x))


def test_sympy__physics__quantum__cg__CG():
    from sympy.physics.quantum.cg import CG
    from sympy import S
    assert _test_args(CG(S(3)/2, S(3)/2, S(1)/2, -S(1)/2, 1, 1))


def test_sympy__physics__quantum__cg__Wigner3j():
    from sympy.physics.quantum.cg import Wigner3j
    assert _test_args(Wigner3j(6, 0, 4, 0, 2, 0))


def test_sympy__physics__quantum__cg__Wigner6j():
    from sympy.physics.quantum.cg import Wigner6j
    assert _test_args(Wigner6j(1, 2, 3, 2, 1, 2))


def test_sympy__physics__quantum__cg__Wigner9j():
    from sympy.physics.quantum.cg import Wigner9j
    assert _test_args(Wigner9j(2, 1, 1, S(3)/2, S(1)/2, 1, S(1)/2, S(1)/2, 0))

def test_sympy__physics__quantum__circuitplot__Mz():
    from sympy.physics.quantum.circuitplot import Mz
    assert _test_args(Mz(0))

def test_sympy__physics__quantum__circuitplot__Mx():
    from sympy.physics.quantum.circuitplot import Mx
    assert _test_args(Mx(0))

def test_sympy__physics__quantum__commutator__Commutator():
    from sympy.physics.quantum.commutator import Commutator
    A, B = symbols('A,B', commutative=False)
    assert _test_args(Commutator(A, B))


def test_sympy__physics__quantum__constants__HBar():
    from sympy.physics.quantum.constants import HBar
    assert _test_args(HBar())


def test_sympy__physics__quantum__dagger__Dagger():
    from sympy.physics.quantum.dagger import Dagger
    from sympy.physics.quantum.state import Ket
    assert _test_args(Dagger(Dagger(Ket('psi'))))


def test_sympy__physics__quantum__gate__CGate():
    from sympy.physics.quantum.gate import CGate, Gate
    assert _test_args(CGate((0, 1), Gate(2)))


def test_sympy__physics__quantum__gate__CGateS():
    from sympy.physics.quantum.gate import CGateS, Gate
    assert _test_args(CGateS((0, 1), Gate(2)))


def test_sympy__physics__quantum__gate__CNotGate():
    from sympy.physics.quantum.gate import CNotGate
    assert _test_args(CNotGate(0, 1))


def test_sympy__physics__quantum__gate__Gate():
    from sympy.physics.quantum.gate import Gate
    assert _test_args(Gate(0))


def test_sympy__physics__quantum__gate__HadamardGate():
    from sympy.physics.quantum.gate import HadamardGate
    assert _test_args(HadamardGate(0))


def test_sympy__physics__quantum__gate__IdentityGate():
    from sympy.physics.quantum.gate import IdentityGate
    assert _test_args(IdentityGate(0))


def test_sympy__physics__quantum__gate__OneQubitGate():
    from sympy.physics.quantum.gate import OneQubitGate
    assert _test_args(OneQubitGate(0))


def test_sympy__physics__quantum__gate__PhaseGate():
    from sympy.physics.quantum.gate import PhaseGate
    assert _test_args(PhaseGate(0))


def test_sympy__physics__quantum__gate__SwapGate():
    from sympy.physics.quantum.gate import SwapGate
    assert _test_args(SwapGate(0, 1))


def test_sympy__physics__quantum__gate__TGate():
    from sympy.physics.quantum.gate import TGate
    assert _test_args(TGate(0))


def test_sympy__physics__quantum__gate__TwoQubitGate():
    from sympy.physics.quantum.gate import TwoQubitGate
    assert _test_args(TwoQubitGate(0))


def test_sympy__physics__quantum__gate__UGate():
    from sympy.physics.quantum.gate import UGate
    from sympy.matrices.immutable import ImmutableMatrix
    from sympy import Integer, Tuple
    assert _test_args(
        UGate(Tuple(Integer(1)), ImmutableMatrix([[1, 0], [0, 2]])))


def test_sympy__physics__quantum__gate__XGate():
    from sympy.physics.quantum.gate import XGate
    assert _test_args(XGate(0))


def test_sympy__physics__quantum__gate__YGate():
    from sympy.physics.quantum.gate import YGate
    assert _test_args(YGate(0))


def test_sympy__physics__quantum__gate__ZGate():
    from sympy.physics.quantum.gate import ZGate
    assert _test_args(ZGate(0))


@SKIP("TODO: sympy.physics")
def test_sympy__physics__quantum__grover__OracleGate():
    from sympy.physics.quantum.grover import OracleGate
    assert _test_args(OracleGate())


def test_sympy__physics__quantum__grover__WGate():
    from sympy.physics.quantum.grover import WGate
    assert _test_args(WGate(1))


def test_sympy__physics__quantum__hilbert__ComplexSpace():
    from sympy.physics.quantum.hilbert import ComplexSpace
    assert _test_args(ComplexSpace(x))


def test_sympy__physics__quantum__hilbert__DirectSumHilbertSpace():
    from sympy.physics.quantum.hilbert import DirectSumHilbertSpace, ComplexSpace, FockSpace
    c = ComplexSpace(2)
    f = FockSpace()
    assert _test_args(DirectSumHilbertSpace(c, f))


def test_sympy__physics__quantum__hilbert__FockSpace():
    from sympy.physics.quantum.hilbert import FockSpace
    assert _test_args(FockSpace())


def test_sympy__physics__quantum__hilbert__HilbertSpace():
    from sympy.physics.quantum.hilbert import HilbertSpace
    assert _test_args(HilbertSpace())


def test_sympy__physics__quantum__hilbert__L2():
    from sympy.physics.quantum.hilbert import L2
    from sympy import oo, Interval
    assert _test_args(L2(Interval(0, oo)))


def test_sympy__physics__quantum__hilbert__TensorPowerHilbertSpace():
    from sympy.physics.quantum.hilbert import TensorPowerHilbertSpace, FockSpace
    f = FockSpace()
    assert _test_args(TensorPowerHilbertSpace(f, 2))


def test_sympy__physics__quantum__hilbert__TensorProductHilbertSpace():
    from sympy.physics.quantum.hilbert import TensorProductHilbertSpace, FockSpace, ComplexSpace
    c = ComplexSpace(2)
    f = FockSpace()
    assert _test_args(TensorProductHilbertSpace(f, c))


def test_sympy__physics__quantum__innerproduct__InnerProduct():
    from sympy.physics.quantum import Bra, Ket, InnerProduct
    b = Bra('b')
    k = Ket('k')
    assert _test_args(InnerProduct(b, k))


def test_sympy__physics__quantum__operator__DifferentialOperator():
    from sympy.physics.quantum.operator import DifferentialOperator
    from sympy import Derivative, Function
    f = Function('f')
    assert _test_args(DifferentialOperator(1/x*Derivative(f(x), x), f(x)))


def test_sympy__physics__quantum__operator__HermitianOperator():
    from sympy.physics.quantum.operator import HermitianOperator
    assert _test_args(HermitianOperator('H'))


def test_sympy__physics__quantum__operator__Operator():
    from sympy.physics.quantum.operator import Operator
    assert _test_args(Operator('A'))


def test_sympy__physics__quantum__operator__OuterProduct():
    from sympy.physics.quantum.operator import OuterProduct
    from sympy.physics.quantum import Ket, Bra
    b = Bra('b')
    k = Ket('k')
    assert _test_args(OuterProduct(k, b))


def test_sympy__physics__quantum__operator__UnitaryOperator():
    from sympy.physics.quantum.operator import UnitaryOperator
    assert _test_args(UnitaryOperator('U'))


def test_sympy__physics__quantum__piab__PIABBra():
    from sympy.physics.quantum.piab import PIABBra
    assert _test_args(PIABBra('B'))


def test_sympy__physics__quantum__piab__PIABHamiltonian():
    from sympy.physics.quantum.piab import PIABHamiltonian
    assert _test_args(PIABHamiltonian('P'))


def test_sympy__physics__quantum__piab__PIABKet():
    from sympy.physics.quantum.piab import PIABKet
    assert _test_args(PIABKet('K'))


def test_sympy__physics__quantum__qexpr__QExpr():
    from sympy.physics.quantum.qexpr import QExpr
    assert _test_args(QExpr(0))


def test_sympy__physics__quantum__qft__Fourier():
    from sympy.physics.quantum.qft import Fourier
    assert _test_args(Fourier(0, 1))


def test_sympy__physics__quantum__qft__IQFT():
    from sympy.physics.quantum.qft import IQFT
    assert _test_args(IQFT(0, 1))


def test_sympy__physics__quantum__qft__QFT():
    from sympy.physics.quantum.qft import QFT
    assert _test_args(QFT(0, 1))


def test_sympy__physics__quantum__qft__RkGate():
    from sympy.physics.quantum.qft import RkGate
    assert _test_args(RkGate(0, 1))


def test_sympy__physics__quantum__qubit__IntQubit():
    from sympy.physics.quantum.qubit import IntQubit
    assert _test_args(IntQubit(0))


def test_sympy__physics__quantum__qubit__IntQubitBra():
    from sympy.physics.quantum.qubit import IntQubitBra
    assert _test_args(IntQubitBra(0))


def test_sympy__physics__quantum__qubit__IntQubitState():
    from sympy.physics.quantum.qubit import IntQubitState, QubitState
    assert _test_args(IntQubitState(QubitState(0, 1)))


def test_sympy__physics__quantum__qubit__Qubit():
    from sympy.physics.quantum.qubit import Qubit
    assert _test_args(Qubit(0, 0, 0))


def test_sympy__physics__quantum__qubit__QubitBra():
    from sympy.physics.quantum.qubit import QubitBra
    assert _test_args(QubitBra('1', 0))


def test_sympy__physics__quantum__qubit__QubitState():
    from sympy.physics.quantum.qubit import QubitState
    assert _test_args(QubitState(0, 1))


def test_sympy__physics__quantum__density__Density():
    from sympy.physics.quantum.density import Density
    from sympy.physics.quantum.state import Ket
    assert _test_args(Density([Ket(0), 0.5], [Ket(1), 0.5]))


@SKIP("TODO: sympy.physics.quantum.shor: Cmod Not Implemented")
def test_sympy__physics__quantum__shor__CMod():
    from sympy.physics.quantum.shor import CMod
    assert _test_args(CMod())


def test_sympy__physics__quantum__spin__CoupledSpinState():
    from sympy.physics.quantum.spin import CoupledSpinState
    assert _test_args(CoupledSpinState(1, 0, (1, 1)))
    assert _test_args(CoupledSpinState(1, 0, (1, S(1)/2, S(1)/2)))
    assert _test_args(CoupledSpinState(
        1, 0, (1, S(1)/2, S(1)/2), ((2, 3, S(1)/2), (1, 2, 1)) ))
    j, m, j1, j2, j3, j12, x = symbols('j m j1:4 j12 x')
    assert CoupledSpinState(
        j, m, (j1, j2, j3)).subs(j2, x) == CoupledSpinState(j, m, (j1, x, j3))
    assert CoupledSpinState(j, m, (j1, j2, j3), ((1, 3, j12), (1, 2, j)) ).subs(j12, x) == \
        CoupledSpinState(j, m, (j1, j2, j3), ((1, 3, x), (1, 2, j)) )


def test_sympy__physics__quantum__spin__J2Op():
    from sympy.physics.quantum.spin import J2Op
    assert _test_args(J2Op('J'))


def test_sympy__physics__quantum__spin__JminusOp():
    from sympy.physics.quantum.spin import JminusOp
    assert _test_args(JminusOp('J'))


def test_sympy__physics__quantum__spin__JplusOp():
    from sympy.physics.quantum.spin import JplusOp
    assert _test_args(JplusOp('J'))


def test_sympy__physics__quantum__spin__JxBra():
    from sympy.physics.quantum.spin import JxBra
    assert _test_args(JxBra(1, 0))


def test_sympy__physics__quantum__spin__JxBraCoupled():
    from sympy.physics.quantum.spin import JxBraCoupled
    assert _test_args(JxBraCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JxKet():
    from sympy.physics.quantum.spin import JxKet
    assert _test_args(JxKet(1, 0))


def test_sympy__physics__quantum__spin__JxKetCoupled():
    from sympy.physics.quantum.spin import JxKetCoupled
    assert _test_args(JxKetCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JxOp():
    from sympy.physics.quantum.spin import JxOp
    assert _test_args(JxOp('J'))


def test_sympy__physics__quantum__spin__JyBra():
    from sympy.physics.quantum.spin import JyBra
    assert _test_args(JyBra(1, 0))


def test_sympy__physics__quantum__spin__JyBraCoupled():
    from sympy.physics.quantum.spin import JyBraCoupled
    assert _test_args(JyBraCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JyKet():
    from sympy.physics.quantum.spin import JyKet
    assert _test_args(JyKet(1, 0))


def test_sympy__physics__quantum__spin__JyKetCoupled():
    from sympy.physics.quantum.spin import JyKetCoupled
    assert _test_args(JyKetCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JyOp():
    from sympy.physics.quantum.spin import JyOp
    assert _test_args(JyOp('J'))


def test_sympy__physics__quantum__spin__JzBra():
    from sympy.physics.quantum.spin import JzBra
    assert _test_args(JzBra(1, 0))


def test_sympy__physics__quantum__spin__JzBraCoupled():
    from sympy.physics.quantum.spin import JzBraCoupled
    assert _test_args(JzBraCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JzKet():
    from sympy.physics.quantum.spin import JzKet
    assert _test_args(JzKet(1, 0))


def test_sympy__physics__quantum__spin__JzKetCoupled():
    from sympy.physics.quantum.spin import JzKetCoupled
    assert _test_args(JzKetCoupled(1, 0, (1, 1)))


def test_sympy__physics__quantum__spin__JzOp():
    from sympy.physics.quantum.spin import JzOp
    assert _test_args(JzOp('J'))


def test_sympy__physics__quantum__spin__Rotation():
    from sympy.physics.quantum.spin import Rotation
    from sympy import pi
    assert _test_args(Rotation(pi, 0, pi/2))


def test_sympy__physics__quantum__spin__SpinState():
    from sympy.physics.quantum.spin import SpinState
    assert _test_args(SpinState(1, 0))


def test_sympy__physics__quantum__spin__WignerD():
    from sympy.physics.quantum.spin import WignerD
    assert _test_args(WignerD(0, 1, 2, 3, 4, 5))


def test_sympy__physics__quantum__state__Bra():
    from sympy.physics.quantum.state import Bra
    assert _test_args(Bra(0))


def test_sympy__physics__quantum__state__BraBase():
    from sympy.physics.quantum.state import BraBase
    assert _test_args(BraBase(0))


def test_sympy__physics__quantum__state__Ket():
    from sympy.physics.quantum.state import Ket
    assert _test_args(Ket(0))


def test_sympy__physics__quantum__state__KetBase():
    from sympy.physics.quantum.state import KetBase
    assert _test_args(KetBase(0))


def test_sympy__physics__quantum__state__State():
    from sympy.physics.quantum.state import State
    assert _test_args(State(0))


def test_sympy__physics__quantum__state__StateBase():
    from sympy.physics.quantum.state import StateBase
    assert _test_args(StateBase(0))


def test_sympy__physics__quantum__state__TimeDepBra():
    from sympy.physics.quantum.state import TimeDepBra
    assert _test_args(TimeDepBra('psi', 't'))


def test_sympy__physics__quantum__state__TimeDepKet():
    from sympy.physics.quantum.state import TimeDepKet
    assert _test_args(TimeDepKet('psi', 't'))


def test_sympy__physics__quantum__state__TimeDepState():
    from sympy.physics.quantum.state import TimeDepState
    assert _test_args(TimeDepState('psi', 't'))


def test_sympy__physics__quantum__state__Wavefunction():
    from sympy.physics.quantum.state import Wavefunction
    from sympy.functions import sin
    from sympy import Piecewise, pi
    n = 1
    L = 1
    g = Piecewise((0, x < 0), (0, x > L), (sqrt(2//L)*sin(n*pi*x/L), True))
    assert _test_args(Wavefunction(g, x))


def test_sympy__physics__quantum__tensorproduct__TensorProduct():
    from sympy.physics.quantum.tensorproduct import TensorProduct
    assert _test_args(TensorProduct(x, y))


def test_sympy__physics__quantum__identitysearch__GateIdentity():
    from sympy.physics.quantum.gate import X
    from sympy.physics.quantum.identitysearch import GateIdentity
    assert _test_args(GateIdentity(X(0), X(0)))


def test_sympy__physics__quantum__sho1d__SHOOp():
    from sympy.physics.quantum.sho1d import SHOOp
    assert _test_args(SHOOp('a'))


def test_sympy__physics__quantum__sho1d__RaisingOp():
    from sympy.physics.quantum.sho1d import RaisingOp
    assert _test_args(RaisingOp('a'))


def test_sympy__physics__quantum__sho1d__LoweringOp():
    from sympy.physics.quantum.sho1d import LoweringOp
    assert _test_args(LoweringOp('a'))


def test_sympy__physics__quantum__sho1d__NumberOp():
    from sympy.physics.quantum.sho1d import NumberOp
    assert _test_args(NumberOp('N'))


def test_sympy__physics__quantum__sho1d__Hamiltonian():
    from sympy.physics.quantum.sho1d import Hamiltonian
    assert _test_args(Hamiltonian('H'))


def test_sympy__physics__quantum__sho1d__SHOState():
    from sympy.physics.quantum.sho1d import SHOState
    assert _test_args(SHOState(0))


def test_sympy__physics__quantum__sho1d__SHOKet():
    from sympy.physics.quantum.sho1d import SHOKet
    assert _test_args(SHOKet(0))


def test_sympy__physics__quantum__sho1d__SHOBra():
    from sympy.physics.quantum.sho1d import SHOBra
    assert _test_args(SHOBra(0))


def test_sympy__physics__secondquant__AnnihilateBoson():
    from sympy.physics.secondquant import AnnihilateBoson
    assert _test_args(AnnihilateBoson(0))


def test_sympy__physics__secondquant__AnnihilateFermion():
    from sympy.physics.secondquant import AnnihilateFermion
    assert _test_args(AnnihilateFermion(0))


@SKIP("abstract class")
def test_sympy__physics__secondquant__Annihilator():
    pass


def test_sympy__physics__secondquant__AntiSymmetricTensor():
    from sympy.physics.secondquant import AntiSymmetricTensor
    i, j = symbols('i j', below_fermi=True)
    a, b = symbols('a b', above_fermi=True)
    assert _test_args(AntiSymmetricTensor('v', (a, i), (b, j)))


def test_sympy__physics__secondquant__BosonState():
    from sympy.physics.secondquant import BosonState
    assert _test_args(BosonState((0, 1)))


@SKIP("abstract class")
def test_sympy__physics__secondquant__BosonicOperator():
    pass


def test_sympy__physics__secondquant__Commutator():
    from sympy.physics.secondquant import Commutator
    assert _test_args(Commutator(x, y))


def test_sympy__physics__secondquant__CreateBoson():
    from sympy.physics.secondquant import CreateBoson
    assert _test_args(CreateBoson(0))


def test_sympy__physics__secondquant__CreateFermion():
    from sympy.physics.secondquant import CreateFermion
    assert _test_args(CreateFermion(0))


@SKIP("abstract class")
def test_sympy__physics__secondquant__Creator():
    pass


def test_sympy__physics__secondquant__Dagger():
    from sympy.physics.secondquant import Dagger
    from sympy import I
    assert _test_args(Dagger(2*I))


def test_sympy__physics__secondquant__FermionState():
    from sympy.physics.secondquant import FermionState
    assert _test_args(FermionState((0, 1)))


def test_sympy__physics__secondquant__FermionicOperator():
    from sympy.physics.secondquant import FermionicOperator
    assert _test_args(FermionicOperator(0))


def test_sympy__physics__secondquant__FockState():
    from sympy.physics.secondquant import FockState
    assert _test_args(FockState((0, 1)))


def test_sympy__physics__secondquant__FockStateBosonBra():
    from sympy.physics.secondquant import FockStateBosonBra
    assert _test_args(FockStateBosonBra((0, 1)))


def test_sympy__physics__secondquant__FockStateBosonKet():
    from sympy.physics.secondquant import FockStateBosonKet
    assert _test_args(FockStateBosonKet((0, 1)))


def test_sympy__physics__secondquant__FockStateBra():
    from sympy.physics.secondquant import FockStateBra
    assert _test_args(FockStateBra((0, 1)))


def test_sympy__physics__secondquant__FockStateFermionBra():
    from sympy.physics.secondquant import FockStateFermionBra
    assert _test_args(FockStateFermionBra((0, 1)))


def test_sympy__physics__secondquant__FockStateFermionKet():
    from sympy.physics.secondquant import FockStateFermionKet
    assert _test_args(FockStateFermionKet((0, 1)))


def test_sympy__physics__secondquant__FockStateKet():
    from sympy.physics.secondquant import FockStateKet
    assert _test_args(FockStateKet((0, 1)))


def test_sympy__physics__secondquant__InnerProduct():
    from sympy.physics.secondquant import InnerProduct
    from sympy.physics.secondquant import FockStateKet, FockStateBra
    assert _test_args(InnerProduct(FockStateBra((0, 1)), FockStateKet((0, 1))))


def test_sympy__physics__secondquant__NO():
    from sympy.physics.secondquant import NO, F, Fd
    assert _test_args(NO(Fd(x)*F(y)))


def test_sympy__physics__secondquant__PermutationOperator():
    from sympy.physics.secondquant import PermutationOperator
    assert _test_args(PermutationOperator(0, 1))


def test_sympy__physics__secondquant__SqOperator():
    from sympy.physics.secondquant import SqOperator
    assert _test_args(SqOperator(0))


def test_sympy__physics__secondquant__TensorSymbol():
    from sympy.physics.secondquant import TensorSymbol
    assert _test_args(TensorSymbol(x))


def test_sympy__physics__units__Unit():
    from sympy.physics.units import Unit
    assert _test_args(Unit("meter", "m"))


def test_sympy__polys__numberfields__AlgebraicNumber():
    from sympy.polys.numberfields import AlgebraicNumber
    assert _test_args(AlgebraicNumber(sqrt(2), [1, 2, 3]))


def test_sympy__polys__polytools__GroebnerBasis():
    from sympy.polys.polytools import GroebnerBasis
    assert _test_args(GroebnerBasis([x, y, z], x, y, z))


def test_sympy__polys__polytools__Poly():
    from sympy.polys.polytools import Poly
    assert _test_args(Poly(2, x, y))


def test_sympy__polys__polytools__PurePoly():
    from sympy.polys.polytools import PurePoly
    assert _test_args(PurePoly(2, x, y))


def test_sympy__polys__rootoftools__RootOf():
    from sympy.polys.rootoftools import RootOf
    assert _test_args(RootOf(x**3 + x + 1, 0))


def test_sympy__polys__rootoftools__RootSum():
    from sympy.polys.rootoftools import RootSum
    assert _test_args(RootSum(x**3 + x + 1, sin))


def test_sympy__series__limits__Limit():
    from sympy.series.limits import Limit
    assert _test_args(Limit(x, x, 0, dir='-'))


def test_sympy__series__order__Order():
    from sympy.series.order import Order
    assert _test_args(Order(1, x, y))


def test_sympy__simplify__hyperexpand__Hyper_Function():
    from sympy.simplify.hyperexpand import Hyper_Function
    assert _test_args(Hyper_Function([2], [1]))


def test_sympy__simplify__hyperexpand__G_Function():
    from sympy.simplify.hyperexpand import G_Function
    assert _test_args(G_Function([2], [1], [], []))


def test_sympy__tensor__indexed__Idx():
    from sympy.tensor.indexed import Idx
    assert _test_args(Idx('test'))
    assert _test_args(Idx(1, (0, 10)))


def test_sympy__tensor__indexed__Indexed():
    from sympy.tensor.indexed import Indexed, Idx
    assert _test_args(Indexed('A', Idx('i'), Idx('j')))


def test_sympy__tensor__indexed__IndexedBase():
    from sympy.tensor.indexed import IndexedBase
    assert _test_args(IndexedBase('A', shape=(x, y)))
    assert _test_args(IndexedBase('A', 1))
    assert _test_args(IndexedBase('A')[0, 1])


@XFAIL
def test_sympy__physics__hep__gamma_matrices__GammaMatrixHead():
    # This test fails, this class can be reconstructed from the *args
    # of an instance using `TensorHead(*args)`
    from sympy.physics.hep.gamma_matrices import GammaMatrixHead, Lorentz
    from sympy.tensor.tensor import tensor_indices
    i = tensor_indices('i', Lorentz)
    assert _test_args(GammaMatrixHead())

def test_sympy__tensor__tensor__TensorIndexType():
    from sympy.tensor.tensor import TensorIndexType
    from sympy import Symbol
    assert _test_args(TensorIndexType('Lorentz', metric=False))


def test_sympy__tensor__tensor__TensorSymmetry():
    from sympy.tensor.tensor import TensorIndexType, tensor_indices, TensorSymmetry, TensorType, get_symmetric_group_sgs
    assert _test_args(TensorSymmetry(get_symmetric_group_sgs(2)))


def test_sympy__tensor__tensor__TensorType():
    from sympy.tensor.tensor import TensorIndexType, TensorSymmetry, get_symmetric_group_sgs, TensorType
    Lorentz = TensorIndexType('Lorentz', dummy_fmt='L')
    sym = TensorSymmetry(get_symmetric_group_sgs(1))
    assert _test_args(TensorType([Lorentz], sym))


def test_sympy__tensor__tensor__TensorHead():
    from sympy.tensor.tensor import TensorIndexType, TensorSymmetry, TensorType, get_symmetric_group_sgs, TensorHead
    Lorentz = TensorIndexType('Lorentz', dummy_fmt='L')
    sym = TensorSymmetry(get_symmetric_group_sgs(1))
    S1 = TensorType([Lorentz], sym)
    assert _test_args(TensorHead('p', S1, 0))


def test_sympy__tensor__tensor__TensorIndex():
    from sympy.tensor.tensor import TensorIndexType, TensorIndex, TensorSymmetry, TensorType, get_symmetric_group_sgs
    Lorentz = TensorIndexType('Lorentz', dummy_fmt='L')
    assert _test_args(TensorIndex('i', Lorentz))

@SKIP("abstract class")
def test_sympy__tensor__tensor__TensExpr():
    pass

def test_sympy__tensor__tensor__TensAdd():
    from sympy.tensor.tensor import TensorIndexType, TensorSymmetry, TensorType, get_symmetric_group_sgs, tensor_indices, TensAdd
    Lorentz = TensorIndexType('Lorentz', dummy_fmt='L')
    a, b = tensor_indices('a,b', Lorentz)
    sym = TensorSymmetry(get_symmetric_group_sgs(1))
    S1 = TensorType([Lorentz], sym)
    p, q = S1('p,q')
    t1 = p(a)
    t2 = q(a)
    assert _test_args(TensAdd(t1, t2))


def test_sympy__tensor__tensor__TensMul():
    from sympy.core import S
    from sympy.tensor.tensor import TensorIndexType, TensorSymmetry, TensorType, get_symmetric_group_sgs, tensor_indices, TensMul, TIDS
    Lorentz = TensorIndexType('Lorentz', dummy_fmt='L')
    a, b = tensor_indices('a,b', Lorentz)
    sym = TensorSymmetry(get_symmetric_group_sgs(1))
    S1 = TensorType([Lorentz], sym)
    p = S1('p')
    free, dum = TIDS.free_dum_from_indices(a)
    assert _test_args(TensMul.from_data(S.One, [p], free, dum))



@XFAIL
def test_as_coeff_add():
    # the ordering of terms in (3*x, 4*x**2) is system-dependent
    assert (7, (3*x, 4*x**2)) == (7 + 3*x + 4*x**2).as_coeff_add()


def test_sympy__geometry__curve__Curve():
    from sympy.geometry.curve import Curve
    assert _test_args(Curve((x, 1), (x, 0, 1)))


def test_sympy__geometry__point__Point():
    from sympy.geometry.point import Point
    assert _test_args(Point(0, 1))


def test_sympy__geometry__ellipse__Ellipse():
    from sympy.geometry.ellipse import Ellipse
    assert _test_args(Ellipse((0, 1), 2, 3))


def test_sympy__geometry__ellipse__Circle():
    from sympy.geometry.ellipse import Circle
    assert _test_args(Circle((0, 1), 2))


def test_sympy__geometry__line__LinearEntity():
    from sympy.geometry.line import LinearEntity
    assert _test_args(LinearEntity((0, 1), (2, 3)))


def test_sympy__geometry__line__Line():
    from sympy.geometry.line import Line
    assert _test_args(Line((0, 1), (2, 3)))


def test_sympy__geometry__line__Ray():
    from sympy.geometry.line import Ray
    assert _test_args(Ray((0, 1), (2, 3)))


def test_sympy__geometry__line__Segment():
    from sympy.geometry.line import Segment
    assert _test_args(Segment((0, 1), (2, 3)))


def test_sympy__geometry__polygon__Polygon():
    from sympy.geometry.polygon import Polygon
    assert _test_args(Polygon((0, 1), (2, 3), (4, 5), (6, 7)))


def test_sympy__geometry__polygon__RegularPolygon():
    from sympy.geometry.polygon import RegularPolygon
    assert _test_args(RegularPolygon((0, 1), 2, 3, 4))


def test_sympy__geometry__polygon__Triangle():
    from sympy.geometry.polygon import Triangle
    assert _test_args(Triangle((0, 1), (2, 3), (4, 5)))


def test_sympy__geometry__entity__GeometryEntity():
    from sympy.geometry.entity import GeometryEntity
    from sympy.geometry.point import Point
    assert _test_args(GeometryEntity(Point(1, 0), 1))


@XFAIL
def test_sympy__diffgeom__diffgeom__Manifold():
    from sympy.diffgeom import Manifold
    assert _test_args(Manifold('name', 3))


@XFAIL
def test_sympy__diffgeom__diffgeom__Patch():
    from sympy.diffgeom import Manifold, Patch
    assert _test_args(Patch('name', Manifold('name', 3)))


@XFAIL
def test_sympy__diffgeom__diffgeom__CoordSystem():
    from sympy.diffgeom import Manifold, Patch, CoordSystem
    assert _test_args(CoordSystem('name', Patch('name', Manifold('name', 3))))


@XFAIL
def test_sympy__diffgeom__diffgeom__Point():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, Point
    assert _test_args(Point(
        CoordSystem('name', Patch('name', Manifold('name', 3))), [x, y]))


@XFAIL
def test_sympy__diffgeom__diffgeom__BaseScalarField():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    assert _test_args(BaseScalarField(cs, 0))


@XFAIL
def test_sympy__diffgeom__diffgeom__BaseVectorField():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseVectorField
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    assert _test_args(BaseVectorField(cs, 0))


def test_sympy__diffgeom__diffgeom__Differential():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField, Differential
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    assert _test_args(Differential(BaseScalarField(cs, 0)))


def test_sympy__diffgeom__diffgeom__Commutator():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField, BaseVectorField, Commutator
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    cs1 = CoordSystem('name1', Patch('name', Manifold('name', 3)))
    v = BaseVectorField(cs, 0)
    v1 = BaseVectorField(cs1, 0)
    assert _test_args(Commutator(v, v1))


def test_sympy__diffgeom__diffgeom__TensorProduct():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField, Differential, TensorProduct
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    d = Differential(BaseScalarField(cs, 0))
    assert _test_args(TensorProduct(d, d))


def test_sympy__diffgeom__diffgeom__WedgeProduct():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField, Differential, WedgeProduct
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    d = Differential(BaseScalarField(cs, 0))
    d1 = Differential(BaseScalarField(cs, 1))
    assert _test_args(WedgeProduct(d, d1))


def test_sympy__diffgeom__diffgeom__LieDerivative():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseScalarField, Differential, BaseVectorField, LieDerivative
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    d = Differential(BaseScalarField(cs, 0))
    v = BaseVectorField(cs, 0)
    assert _test_args(LieDerivative(v, d))


@XFAIL
def test_sympy__diffgeom__diffgeom__BaseCovarDerivativeOp():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseCovarDerivativeOp
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    assert _test_args(BaseCovarDerivativeOp(cs, 0, [[[0, ]*3, ]*3, ]*3))


def test_sympy__diffgeom__diffgeom__CovarDerivativeOp():
    from sympy.diffgeom import Manifold, Patch, CoordSystem, BaseVectorField, CovarDerivativeOp
    cs = CoordSystem('name', Patch('name', Manifold('name', 3)))
    v = BaseVectorField(cs, 0)
    _test_args(CovarDerivativeOp(v, [[[0, ]*3, ]*3, ]*3))


def test_sympy__categories__baseclasses__Class():
    from sympy.categories.baseclasses import Class
    assert _test_args(Class())


def test_sympy__categories__baseclasses__Object():
    from sympy.categories import Object
    assert _test_args(Object("A"))


@XFAIL
def test_sympy__categories__baseclasses__Morphism():
    from sympy.categories import Object, Morphism
    assert _test_args(Morphism(Object("A"), Object("B")))


def test_sympy__categories__baseclasses__IdentityMorphism():
    from sympy.categories import Object, IdentityMorphism
    assert _test_args(IdentityMorphism(Object("A")))


def test_sympy__categories__baseclasses__NamedMorphism():
    from sympy.categories import Object, NamedMorphism
    assert _test_args(NamedMorphism(Object("A"), Object("B"), "f"))


def test_sympy__categories__baseclasses__CompositeMorphism():
    from sympy.categories import Object, NamedMorphism, CompositeMorphism
    A = Object("A")
    B = Object("B")
    C = Object("C")
    f = NamedMorphism(A, B, "f")
    g = NamedMorphism(B, C, "g")
    assert _test_args(CompositeMorphism(f, g))


def test_sympy__categories__baseclasses__Diagram():
    from sympy.categories import Object, NamedMorphism, Diagram, Category
    A = Object("A")
    B = Object("B")
    C = Object("C")
    f = NamedMorphism(A, B, "f")
    d = Diagram([f])
    assert _test_args(d)


def test_sympy__categories__baseclasses__Category():
    from sympy.categories import Object, NamedMorphism, Diagram, Category
    A = Object("A")
    B = Object("B")
    C = Object("C")
    f = NamedMorphism(A, B, "f")
    g = NamedMorphism(B, C, "g")
    d1 = Diagram([f, g])
    d2 = Diagram([f])
    K = Category("K", commutative_diagrams=[d1, d2])
    assert _test_args(K)

def test_sympy__ntheory__factor___totient():
    from sympy.ntheory.factor_ import totient
    k = symbols('k', integer=True)
    t = totient(k)
    assert _test_args(t)
