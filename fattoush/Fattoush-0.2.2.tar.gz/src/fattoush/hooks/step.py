# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
Hooks that run before and after steps
"""

from lettuce import world, before, after
import time
from selenium.common.exceptions import WebDriverException


@before.each_step
def hook_store_augmented_step_name(step):
    """
    Get a more meaningful step name that can be used in reporting
    while this step runs.
    """
    config = world.fattoush
    world.absorb("[{0}] {1}".format(config.name, step.sentence),
                 "step_name")


def on_fail(wd):
    time.sleep(1)
    filename = "logs/{0}_{1}.png".format(world.step_name,
                                         time.time())
    try:
        wd.get_screenshot_as_file(filename)
    except BaseException as ex:
        print "could not capture screen shot to {0}:\n{1}".format(
            filename, ex)
    finally:
        wd.sauce.fail_session()


def on_pass(wd):
    """"
    Make sure there's a screen shot in the saucelabs log. This gets a
    hunk of binary data but doesn't do anything with it, as we can
    retrieve it from saucelabs.
    """
    try:
        wd.get_screenshot_as_png()
    except WebDriverException:
        pass


@after.each_step
def hook_ensure_screenshot_after_step(step):
    """
    Makes sure a screen shot is taken in Saucelabs after each test
    step. If the step passed leave it on the sever, if it failed we
    want a copy.
    """
    from .. import Driver
    try:
        wd = Driver.instance(step)
        if step.failed:
            on_fail(wd)
        else:
            on_pass(wd)
    finally:
        world.spew('step_name')