from nose2.compat import unittest
from nose2.tests._common import run_nose2
from nose2.tools import params

from applitools.errors import EyesError
from applitools._webdriver import EyesScreenshot


class MockWebDriver(object):
    pass


class EyesScreenshotInit(unittest.TestCase):
    """
    Tests EyesScreenshot initialization.
    """
    def setUp(self):
        self.driver = MockWebDriver()

    def test_no_screenshot(self):
        self.assertRaises(ValueError, EyesScreenshot(self.driver))


if __name__ == "__main__":

