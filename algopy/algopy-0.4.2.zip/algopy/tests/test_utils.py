from numpy.testing import *
import numpy
import numpy.random

from algopy.utpm import UTPM
from algopy.utils import *

class TestUtils ( TestCase ):

    def test_utpm2base_and_dirs(self):
        D,P,N,M,K = 2,3,4,5,6
        u = UTPM( numpy.arange(D*P*N*M*K).reshape((D,P,N,M,K)))
        x,V = utpm2base_and_dirs(u)
        assert_array_almost_equal(x, numpy.arange(N*M*K).reshape((N,M,K)))
        assert_array_almost_equal(V, numpy.arange(P*N*M*K,D*P*N*M*K).reshape((D-1,P,N,M,K)).transpose((2,3,4,1,0)))

    def test_utpm2dirs(self):
        D,P,N,M,K = 2,3,4,5,6
        u = UTPM( numpy.arange(D*P*N*M*K).reshape((D,P,N,M,K)))
        Vbar = utpm2dirs(u)
        assert_array_almost_equal(Vbar, numpy.arange(D*P*N*M*K).reshape((D,P,N,M,K)).transpose((2,3,4,1,0)) )

if __name__ == "__main__":
    run_module_suite()
