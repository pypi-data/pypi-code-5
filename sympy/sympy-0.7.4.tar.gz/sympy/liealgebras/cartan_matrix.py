from .cartan_type import CartanType

def CartanMatrix(ct):
    """
    This is a method that allows a user to access
    the Cartan matrix of a specific Lie algebra.
    Example
    =======
    >>> from sympy.liealgebras.cartan_matrix import CartanMatrix
    >>> CartanMatrix("A2")
    Matrix([
    [ 2, -1],
    [-1,  2]])

    >>> CartanMatrix(['C', 3])
    Matrix([
    [ 2, -1,  0],
    [-1,  2, -1],
    [ 0, -2,  2]])

    This method works by returning the Cartan matrix
    which corresponds to Cartan type t.
    """

    return CartanType(ct).cartan_matrix()
