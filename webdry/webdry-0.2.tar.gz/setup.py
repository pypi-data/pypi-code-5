# -*- coding: UTF-8 -*-
from setuptools import setup
# Nasty hack to make e.g. setup.py register read PKG-INFO as utf-8.. {{{
import sys
reload(sys) # setdefaultencoding is deleted in site.py..
sys.setdefaultencoding('utf-8')
# }}}

setup(
    name='webdry',
    version='0.2',
    description = """A set of functions for minimalistic interaction with Selenium WebDriver.""",
    keywords = "web browser test tool",
    platforms = ["any"],
    author = "Niklas Lindström",
    author_email = "lindstream@gmail.com",
    license = "BSD",
    url = "https://bitbucket.org/niklasl/webdry",
    py_modules=['webdry'],
    install_requires = [
        'selenium>=2.19.1',
    ],
)
