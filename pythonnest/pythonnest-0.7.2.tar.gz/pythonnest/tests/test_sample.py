# -*- coding: utf-8 -*-
"""
Sample test module corresponding to the :mod:`pythonnest.sample` module.

A complete documentation can be found at :mod:`unittest`.

"""
import unittest
from pythonnest.sample import sample_function
__author__ = "flanker"
# __copyright__ = "Copyright 2013, 19pouces.net"
# __credits__ = "flanker"
# __maintainer__ = "flanker"
# __email__ = "flanker@19pouces.net"
__all__ = ['SampleTest']


class SampleTest(unittest.TestCase):
    """Base test cases for the sample function provided in
    :func:`pythonnest.sample.sample_function`."""
    # pylint: disable=R0904

    def test_1(self):
        """Test the sample_function with two arguments."""
        self.assertEqual(sample_function(4, 4), 8)

    def test_2(self):
        """Test the sample_function with a single argument."""
        self.assertEqual(sample_function(4), 8)

if __name__ == '__main__':
    unittest.main()