# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
Hooks that run before and after scenarios
"""

from lettuce import before, after


@before.each_scenario
def hook_rename_scenario(scenario):
    feature = scenario.feature
    scenario.name = "{0}.{1}".format(feature.name, scenario.name)

@after.each_scenario
def hook_destroy_sauce_connection(scenario):
    """
    Quits any sauce session in progress and removes the connection
    manager object from the world object namespace.
    """
    from .. import Driver
    Driver.kill_instance(scenario)