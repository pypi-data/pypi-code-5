from __future__ import division, print_function, absolute_import

import warnings

import numpy as np
from numpy.testing import assert_almost_equal, assert_equal, run_module_suite

from scipy.signal.ltisys import ss2tf, lsim2, impulse2, step2, lti, bode, \
    freqresp, impulse, step
from scipy.signal.filter_design import BadCoefficients
import scipy.linalg as linalg


class TestSS2TF:
    def tst_matrix_shapes(self, p, q, r):
        ss2tf(np.zeros((p, p)),
              np.zeros((p, q)),
              np.zeros((r, p)),
              np.zeros((r, q)), 0)

    def test_basic(self):
        for p, q, r in [
            (3, 3, 3),
            (1, 3, 3),
            (1, 1, 1)]:
            yield self.tst_matrix_shapes, p, q, r


class Test_lsim2(object):

    def test_01(self):
        t = np.linspace(0,10,1001)
        u = np.zeros_like(t)
        # First order system: x'(t) + x(t) = u(t), x(0) = 1.
        # Exact solution is x(t) = exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y, x = lsim2(system, u, t, X0=[1.0])
        expected_x = np.exp(-tout)
        assert_almost_equal(x[:,0], expected_x)

    def test_02(self):
        t = np.array([0.0, 1.0, 1.0, 3.0])
        u = np.array([0.0, 0.0, 1.0, 1.0])
        # Simple integrator: x'(t) = u(t)
        system = ([1.0],[1.0,0.0])
        tout, y, x = lsim2(system, u, t, X0=[1.0])
        expected_x = np.maximum(1.0, tout)
        assert_almost_equal(x[:,0], expected_x)

    def test_03(self):
        t = np.array([0.0, 1.0, 1.0, 1.1, 1.1, 2.0])
        u = np.array([0.0, 0.0, 1.0, 1.0, 0.0, 0.0])
        # Simple integrator:  x'(t) = u(t)
        system = ([1.0],[1.0, 0.0])
        tout, y, x = lsim2(system, u, t, hmax=0.01)
        expected_x = np.array([0.0, 0.0, 0.0, 0.1, 0.1, 0.1])
        assert_almost_equal(x[:,0], expected_x)

    def test_04(self):
        t = np.linspace(0, 10, 1001)
        u = np.zeros_like(t)
        # Second order system with a repeated root: x''(t) + 2*x(t) + x(t) = 0.
        # With initial conditions x(0)=1.0 and x'(t)=0.0, the exact solution
        # is (1-t)*exp(-t).
        system = ([1.0], [1.0, 2.0, 1.0])
        tout, y, x = lsim2(system, u, t, X0=[1.0, 0.0])
        expected_x = (1.0 - tout) * np.exp(-tout)
        assert_almost_equal(x[:,0], expected_x)

    def test_05(self):
        # The call to lsim2 triggers a "BadCoefficients" warning from
        # scipy.signal.filter_design, but the test passes.  I think the warning
        # is related to the incomplete handling of multi-input systems in
        # scipy.signal.

        # A system with two state variables, two inputs, and one output.
        A = np.array([[-1.0, 0.0], [0.0, -2.0]])
        B = np.array([[1.0, 0.0], [0.0, 1.0]])
        C = np.array([1.0, 0.0])
        D = np.zeros((1,2))

        t = np.linspace(0, 10.0, 101)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BadCoefficients)
            tout, y, x = lsim2((A,B,C,D), T=t, X0=[1.0, 1.0])
        expected_y = np.exp(-tout)
        expected_x0 = np.exp(-tout)
        expected_x1 = np.exp(-2.0*tout)
        assert_almost_equal(y, expected_y)
        assert_almost_equal(x[:,0], expected_x0)
        assert_almost_equal(x[:,1], expected_x1)

    def test_06(self):
        """Test use of the default values of the arguments `T` and `U`."""
        # Second order system with a repeated root: x''(t) + 2*x(t) + x(t) = 0.
        # With initial conditions x(0)=1.0 and x'(t)=0.0, the exact solution
        # is (1-t)*exp(-t).
        system = ([1.0], [1.0, 2.0, 1.0])
        tout, y, x = lsim2(system, X0=[1.0, 0.0])
        expected_x = (1.0 - tout) * np.exp(-tout)
        assert_almost_equal(x[:,0], expected_x)


class _TestImpulseFuncs(object):
    # Common tests for impulse/impulse2 (= self.func)

    def test_01(self):
        # First order system: x'(t) + x(t) = u(t)
        # Exact impulse response is x(t) = exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system)
        expected_y = np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_02(self):
        # Specify the desired time values for the output.

        # First order system: x'(t) + x(t) = u(t)
        # Exact impulse response is x(t) = exp(-t).
        system = ([1.0],[1.0,1.0])
        n = 21
        t = np.linspace(0, 2.0, n)
        tout, y = self.func(system, T=t)
        assert_equal(tout.shape, (n,))
        assert_almost_equal(tout, t)
        expected_y = np.exp(-t)
        assert_almost_equal(y, expected_y)

    def test_03(self):
        # Specify an initial condition as a scalar.

        # First order system: x'(t) + x(t) = u(t), x(0)=3.0
        # Exact impulse response is x(t) = 4*exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system, X0=3.0)
        expected_y = 4.0*np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_04(self):
        # Specify an initial condition as a list.

        # First order system: x'(t) + x(t) = u(t), x(0)=3.0
        # Exact impulse response is x(t) = 4*exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system, X0=[3.0])
        expected_y = 4.0*np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_05(self):
        # Simple integrator: x'(t) = u(t)
        system = ([1.0],[1.0,0.0])
        tout, y = self.func(system)
        expected_y = np.ones_like(tout)
        assert_almost_equal(y, expected_y)

    def test_array_like(self):
        # Test that function can accept sequences, scalars.
        system = ([1.0], [1.0, 2.0, 1.0])
        # TODO: add meaningful test where X0 is a list
        tout, y = self.func(system, X0=[3], T=[5, 6])
        tout, y = self.func(system, X0=[3], T=[5])


class TestImpulse2(_TestImpulseFuncs):
    def setup(self):
        self.func = impulse2

    def test_array_like2(self):
        system = ([1.0], [1.0, 2.0, 1.0])
        tout, y = self.func(system, X0=3, T=5)

    def test_06(self):
        # Second order system with a repeated root:
        #     x''(t) + 2*x(t) + x(t) = u(t)
        # The exact impulse response is t*exp(-t).
        # Doesn't pass for `impulse` (on some systems, see gh-2654)
        system = ([1.0], [1.0, 2.0, 1.0])
        tout, y = self.func(system)
        expected_y = tout * np.exp(-tout)
        assert_almost_equal(y, expected_y)


class TestImpulse(_TestImpulseFuncs):
    def setup(self):
        self.func = impulse


class _TestStepFuncs(object):
    def test_01(self):
        # First order system: x'(t) + x(t) = u(t)
        # Exact step response is x(t) = 1 - exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system)
        expected_y = 1.0 - np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_02(self):
        # Specify the desired time values for the output.

        # First order system: x'(t) + x(t) = u(t)
        # Exact step response is x(t) = 1 - exp(-t).
        system = ([1.0],[1.0,1.0])
        n = 21
        t = np.linspace(0, 2.0, n)
        tout, y = self.func(system, T=t)
        assert_equal(tout.shape, (n,))
        assert_almost_equal(tout, t)
        expected_y = 1 - np.exp(-t)
        assert_almost_equal(y, expected_y)

    def test_03(self):
        # Specify an initial condition as a scalar.

        # First order system: x'(t) + x(t) = u(t), x(0)=3.0
        # Exact step response is x(t) = 1 + 2*exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system, X0=3.0)
        expected_y = 1 + 2.0*np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_04(self):
        # Specify an initial condition as a list.

        # First order system: x'(t) + x(t) = u(t), x(0)=3.0
        # Exact step response is x(t) = 1 + 2*exp(-t).
        system = ([1.0],[1.0,1.0])
        tout, y = self.func(system, X0=[3.0])
        expected_y = 1 + 2.0*np.exp(-tout)
        assert_almost_equal(y, expected_y)

    def test_array_like(self):
        # Test that function can accept sequences, scalars.
        system = ([1.0], [1.0, 2.0, 1.0])
        # TODO: add meaningful test where X0 is a list
        tout, y = self.func(system, T=[5, 6])


class TestStep2(_TestStepFuncs):
    def setup(self):
        self.func = step2

    def test_05(self):
        # Simple integrator: x'(t) = u(t)
        # Exact step response is x(t) = t.
        system = ([1.0],[1.0,0.0])
        tout, y = self.func(system, atol=1e-10, rtol=1e-8)
        expected_y = tout
        assert_almost_equal(y, expected_y)

    def test_06(self):
        # Second order system with a repeated root:
        #     x''(t) + 2*x(t) + x(t) = u(t)
        # The exact step response is 1 - (1 + t)*exp(-t).
        system = ([1.0], [1.0, 2.0, 1.0])
        tout, y = self.func(system, atol=1e-10, rtol=1e-8)
        expected_y = 1 - (1 + tout) * np.exp(-tout)
        assert_almost_equal(y, expected_y)


class TestStep(_TestStepFuncs):
    def setup(self):
        self.func = step

    def test_complex_input(self):
        # Test that complex input doesn't raise an error.
        # `step` doesn't seem to have been designed for complex input, but this
        # works and may be used, so add regression test.  See gh-2654.
        step(([], [-1], 1+0j))




def test_lti_instantiation():
    # Test that lti can be instantiated with sequences, scalars.  See PR-225.
    s = lti([1], [-1])
    s = lti(np.array([]), np.array([-1]), 1)
    s = lti([], [-1], 1)
    s = lti([1], [-1], 1, 3)


class Test_bode(object):

    def test_01(self):
        """Test bode() magnitude calculation (manual sanity check)."""
        # 1st order low-pass filter: H(s) = 1 / (s + 1),
        # cutoff: 1 rad/s, slope: -20 dB/decade
        #   H(s=0.1) ~= 0 dB
        #   H(s=1) ~= -3 dB
        #   H(s=10) ~= -20 dB
        #   H(s=100) ~= -40 dB
        system = lti([1], [1, 1])
        w = [0.1, 1, 10, 100]
        w, mag, phase = bode(system, w=w)
        expected_mag = [0, -3, -20, -40]
        assert_almost_equal(mag, expected_mag, decimal=1)

    def test_02(self):
        """Test bode() phase calculation (manual sanity check)."""
        # 1st order low-pass filter: H(s) = 1 / (s + 1),
        #   angle(H(s=0.1)) ~= -5.7 deg
        #   angle(H(s=1)) ~= -45 deg
        #   angle(H(s=10)) ~= -84.3 deg
        system = lti([1], [1, 1])
        w = [0.1, 1, 10]
        w, mag, phase = bode(system, w=w)
        expected_phase = [-5.7, -45, -84.3]
        assert_almost_equal(phase, expected_phase, decimal=1)

    def test_03(self):
        """Test bode() magnitude calculation."""
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        system = lti([1], [1, 1])
        w = [0.1, 1, 10, 100]
        w, mag, phase = bode(system, w=w)
        jw = w * 1j
        y = np.polyval(system.num, jw) / np.polyval(system.den, jw)
        expected_mag = 20.0 * np.log10(abs(y))
        assert_almost_equal(mag, expected_mag)

    def test_04(self):
        """Test bode() phase calculation."""
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        system = lti([1], [1, 1])
        w = [0.1, 1, 10, 100]
        w, mag, phase = bode(system, w=w)
        jw = w * 1j
        y = np.polyval(system.num, jw) / np.polyval(system.den, jw)
        expected_phase = np.arctan2(y.imag, y.real) * 180.0 / np.pi
        assert_almost_equal(phase, expected_phase)

    def test_05(self):
        """Test that bode() finds a reasonable frequency range."""
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        system = lti([1], [1, 1])
        n = 10
        # Expected range is from 0.01 to 10.
        expected_w = np.logspace(-2, 1, n)
        w, mag, phase = bode(system, n=n)
        assert_almost_equal(w, expected_w)

    def test_06(self):
        """Test that bode() doesn't fail on a system with a pole at 0."""
        # integrator, pole at zero: H(s) = 1 / s
        system = lti([1], [1, 0])
        w, mag, phase = bode(system, n=2)
        assert_equal(w[0], 0.01)  # a fail would give not-a-number

    def test_07(self):
        """bode() should not fail on a system with pure imaginary poles."""
        # The test passes if bode doesn't raise an exception.
        system = lti([1], [1, 0, 100])
        w, mag, phase = bode(system, n=2)

    def test_from_state_space(self):
        # Ensure that bode works with a system that was created from the
        # state space representation matrices A, B, C, D.  In this case,
        # system.num will be a 2-D array with shape (1, n+1), where (n,n)
        # is the shape of A.
        # A Butterworth lowpass filter is used, so we know the exact
        # frequency response.
        a = np.array([1.0, 2.0, 2.0, 1.0])
        A = linalg.companion(a).T
        B = np.array([[0.0],[0.0],[1.0]])
        C = np.array([[1.0, 0.0, 0.0]])
        D = np.array([[0.0]])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BadCoefficients)
            system = lti(A, B, C, D)
        w, mag, phase = bode(system, n=100)
        expected_magnitude = 20 * np.log10(np.sqrt(1.0 / (1.0 + w**6)))
        assert_almost_equal(mag, expected_magnitude)


class Test_freqresp(object):

    def test_real_part_manual(self):
        # Test freqresp() real part calculation (manual sanity check).
        # 1st order low-pass filter: H(s) = 1 / (s + 1),
        #   re(H(s=0.1)) ~= 0.99
        #   re(H(s=1)) ~= 0.5
        #   re(H(s=10)) ~= 0.0099
        system = lti([1], [1, 1])
        w = [0.1, 1, 10]
        w, H = freqresp(system, w=w)
        expected_re = [0.99, 0.5, 0.0099]
        assert_almost_equal(H.real, expected_re, decimal=1)

    def test_imag_part_manual(self):
        # Test freqresp() imaginary part calculation (manual sanity check).
        # 1st order low-pass filter: H(s) = 1 / (s + 1),
        #   im(H(s=0.1)) ~= -0.099
        #   im(H(s=1)) ~= -0.5
        #   im(H(s=10)) ~= -0.099
        system = lti([1], [1, 1])
        w = [0.1, 1, 10]
        w, H = freqresp(system, w=w)
        expected_im = [-0.099, -0.5, -0.099]
        assert_almost_equal(H.imag, expected_im, decimal=1)

    def test_real_part(self):
        # Test freqresp() real part calculation.
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        system = lti([1], [1, 1])
        w = [0.1, 1, 10, 100]
        w, H = freqresp(system, w=w)
        jw = w * 1j
        y = np.polyval(system.num, jw) / np.polyval(system.den, jw)
        expected_re = y.real
        assert_almost_equal(H.real, expected_re)

    def test_imag_part(self):
        # Test freqresp() imaginary part calculation.
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        system = lti([1], [1, 1])
        w = [0.1, 1, 10, 100]
        w, H = freqresp(system, w=w)
        jw = w * 1j
        y = np.polyval(system.num, jw) / np.polyval(system.den, jw)
        expected_im = y.imag
        assert_almost_equal(H.imag, expected_im)

    def test_freq_range(self):
        # Test that freqresp() finds a reasonable frequency range.
        # 1st order low-pass filter: H(s) = 1 / (s + 1)
        # Expected range is from 0.01 to 10.
        system = lti([1], [1, 1])
        n = 10
        expected_w = np.logspace(-2, 1, n)
        w, H = freqresp(system, n=n)
        assert_almost_equal(w, expected_w)

    def test_pole_zero(self):
        # Test that freqresp() doesn't fail on a system with a pole at 0.
        # integrator, pole at zero: H(s) = 1 / s
        system = lti([1], [1, 0])
        w, H = freqresp(system, n=2)
        assert_equal(w[0], 0.01)  # a fail would give not-a-number

    def test_from_state_space(self):
        # Ensure that freqresp works with a system that was created from the
        # state space representation matrices A, B, C, D.  In this case,
        # system.num will be a 2-D array with shape (1, n+1), where (n,n) is
        # the shape of A.
        # A Butterworth lowpass filter is used, so we know the exact
        # frequency response.
        a = np.array([1.0, 2.0, 2.0, 1.0])
        A = linalg.companion(a).T
        B = np.array([[0.0],[0.0],[1.0]])
        C = np.array([[1.0, 0.0, 0.0]])
        D = np.array([[0.0]])
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", BadCoefficients)
            system = lti(A, B, C, D)
        w, H = freqresp(system, n=100)
        expected_magnitude = np.sqrt(1.0 / (1.0 + w**6))
        assert_almost_equal(np.abs(H), expected_magnitude)


if __name__ == "__main__":
    run_module_suite()
