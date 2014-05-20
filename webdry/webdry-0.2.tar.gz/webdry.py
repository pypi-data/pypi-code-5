# -*- coding: UTF-8 -*-
import os
import contextlib
import operator
import threading

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import logging
logging.getLogger('selenium.webdriver').setLevel('WARNING')


__all__ = ('Keys', 'patch_webdriver', 'env',
        'start_browser', 'stop_browser', 'delete_all_cookies', 'get', 'back',
        'save_screenshot', 'waits', 'find', 'find_all')


def _find(component, *args, **kws):
    """
    Find one element by css selector or webdriver keyword, or return None.
    """
    symbol, value = _selector(args, kws)
    try:
        return getattr(component, "find_element_by_" + symbol)(value)
    except NoSuchElementException:
        return None

def _find_all(component, *args, **kws):
    """
    Find all elements by css selector or webdriver keyword.
    """
    symbol, value = _selector(args, kws)
    return getattr(component, "find_elements_by_" + symbol)(value)

def _selector(args, kws):
    return ('css_selector', args[0]) if args else kws.items()[0]

def patch_webdriver():
    if not hasattr(WebDriver, 'find'):
        WebDriver.find = _find
    if not hasattr(WebDriver, 'find_all'):
        WebDriver.find_all = _find_all
    if not hasattr(WebElement, 'find'):
        WebElement.find = _find
    if not hasattr(WebElement, 'find_all'):
        WebElement.find_all = _find_all

patch_webdriver()


WAIT_SECS = 7

env = threading.local()

env.wait_secs = WAIT_SECS


def start_browser(driver):
    env.driver = driver
    env.driver.implicitly_wait(env.wait_secs)

def stop_browser():
    env.driver.quit()


@contextlib.contextmanager
def waits(seconds):
    """
    Use in a ``with`` block to set the seconds to wait for finding elements
    within that block.
    """
    env.driver.implicitly_wait(seconds)
    yield
    env.driver.implicitly_wait(env.wait_secs)


def _export_driver_func(fname, fdoc=None):
    get_f = operator.attrgetter(fname)
    f = lambda *args, **kws: get_f(env.driver)(*args, **kws)
    f.__name__ = fname
    f.__doc__ = fdoc
    return f

back = _export_driver_func('back', WebDriver.back.__doc__)

get = _export_driver_func('get', WebDriver.get.__doc__)

delete_all_cookies = _export_driver_func('delete_all_cookies',
        WebDriver.delete_all_cookies.__doc__)

save_screenshot = _export_driver_func('save_screenshot',
        WebDriver.save_screenshot.__doc__)

find = _export_driver_func('find', _find.__doc__)

find_all = _export_driver_func('find_all', _find_all.__doc__)

