"""
Fattoush
========

Fattoush is a package that combines lettuce, webdriver and sauce to make
a tasty UI testing salad.


Running
-------

Fattoush provides its own test runner which invokes lettuce such that it
runs in saucelabs, with support of parallel test runs.

    $ fattoush --parallel=webdriver


Usage
-----

Just write your lettuce tests as normal,
but in your terrain file add

    from fattoush import hooks

You will now find that in each step you are able to add

    from fattoush import Driver

This returns a subclass of WebDriver with a class method `instance()`
which takes the current step or feature and returns the active WebDriver
instance.

License
-------
(c) 2014 Mind Candy Ltd. All Rights Reserved.  
Licensed under the MIT License; you may not use this file except in compliance with the License. 
You may obtain a copy of the License at http://opensource.org/licenses/MIT.
"""

# Bringing the step and world names into this namespace makes it
# easier to replace them at some future point.
#noinspection PyUnresolvedReferences
from lettuce import step, world
from .driver import Driver
from .config import VERSION