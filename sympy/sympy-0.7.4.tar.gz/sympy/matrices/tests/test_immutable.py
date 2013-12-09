from sympy import ImmutableMatrix, Matrix, eye, zeros
from sympy.abc import x, y
from sympy.utilities.pytest import raises

IM = ImmutableMatrix([[1, 2, 3], [4, 5, 6], [7, 8, 9]])
ieye = ImmutableMatrix(eye(3))


def test_immutable_creation():
    assert IM.shape == (3, 3)
    assert IM[1, 2] == 6
    assert IM[2, 2] == 9


def test_immutability():
    with raises(TypeError):
        IM[2, 2] = 5


def test_slicing():
    assert IM[1, :] == ImmutableMatrix([[4, 5, 6]])
    assert IM[:2, :2] == ImmutableMatrix([[1, 2], [4, 5]])


def test_subs():
    A = ImmutableMatrix([[1, 2], [3, 4]])
    B = ImmutableMatrix([[1, 2], [x, 4]])
    C = ImmutableMatrix([[-x, x*y], [-(x + y), y**2]])
    assert B.subs(x, 3) == A
    assert (x*B).subs(x, 3) == 3*A
    assert (x*eye(2) + B).subs(x, 3) == 3*eye(2) + A
    assert C.subs([[x, -1], [y, -2]]) == A
    assert C.subs([(x, -1), (y, -2)]) == A
    assert C.subs({x: -1, y: -2}) == A
    assert C.subs({x: y - 1, y: x - 1}, simultaneous=True) == \
        ImmutableMatrix([[1 - y, (x - 1)*(y - 1)], [2 - x - y, (x - 1)**2]])


def test_as_immutable():
    X = Matrix([[1, 2], [3, 4]])
    assert X.as_immutable() == ImmutableMatrix([[1, 2], [3, 4]])


def test_function_return_types():
    # Lets ensure that decompositions of immutable matrices remain immutable
    # I.e. do MatrixBase methods return the correct class?
    X = ImmutableMatrix([[1, 2], [3, 4]])
    Y = ImmutableMatrix([[1], [0]])
    q, r = X.QRdecomposition()
    assert (type(q), type(r)) == (ImmutableMatrix, ImmutableMatrix)

    assert type(X.LUsolve(Y)) == ImmutableMatrix
    assert type(X.QRsolve(Y)) == ImmutableMatrix

    X = ImmutableMatrix([[1, 2], [2, 1]])
    assert X.T == X
    assert X.is_symmetric
    assert type(X.cholesky()) == ImmutableMatrix
    L, D = X.LDLdecomposition()
    assert (type(L), type(D)) == (ImmutableMatrix, ImmutableMatrix)

    assert X.is_diagonalizable()
    assert X.berkowitz_det() == -3
    assert X.norm(2) == 3

    assert type(X.eigenvects()[0][2][0]) == ImmutableMatrix

    assert type(zeros(3, 3).as_immutable().nullspace()[0]) == ImmutableMatrix

    X = ImmutableMatrix([[1, 0], [2, 1]])
    assert type(X.lower_triangular_solve(Y)) == ImmutableMatrix
    assert type(X.T.upper_triangular_solve(Y)) == ImmutableMatrix

    assert type(X.minorMatrix(0, 0)) == ImmutableMatrix

# Issue 3180
# http://code.google.com/p/sympy/issues/detail?id=3180
# Test that Immutable _op_ Immutable => Immutable and not MatExpr


def test_immutable_evaluation():
    X = ImmutableMatrix(eye(3))
    A = ImmutableMatrix(3, 3, range(9))
    assert isinstance(X + A, ImmutableMatrix)
    assert isinstance(X * A, ImmutableMatrix)
    assert isinstance(X * 2, ImmutableMatrix)
    assert isinstance(2 * X, ImmutableMatrix)
    assert isinstance(A**2, ImmutableMatrix)
