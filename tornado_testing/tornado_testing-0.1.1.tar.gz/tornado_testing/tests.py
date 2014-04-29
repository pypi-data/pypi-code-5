#!/usr/bin/env python

import unittest
import doctest


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('layer.rst'))
    return suite
