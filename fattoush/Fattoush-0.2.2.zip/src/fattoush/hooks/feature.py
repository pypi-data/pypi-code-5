# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
Hooks that run before and after features
"""

from lettuce import world, before


@before.each_feature
def hook_before_feature(feature):
    """
    Change the feature name to include information about where it is
    running - this will appear in the Saucelabs session and so
    having this information makes it easier to see where any
    unexpected behaviour may have occurred.
    """
    config = world.fattoush
    feature.name = "[{0}] {1}".format(config.name, feature.name)