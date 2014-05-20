# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

"""
The driver class shall be a subclass of WebDriver with a classmethod
`instance()` which takes the current step or feature and returns
the active WebDriver instance.
"""

from selenium.webdriver import Remote
from lettuce.core import Step, Scenario
from .. import world
from .sauce import Sauce, Local


class Driver(Remote):

    _registry = {}

    @classmethod
    def _from(cls, scenario):
        if scenario.name not in cls._registry:
            cfg = world.fattoush
            cls._registry[scenario.name] = cls(cfg, scenario)
        return cls._registry[scenario.name]

    @classmethod
    def _scenario(cls, step_or_scenario):
        if isinstance(step_or_scenario, Step):
            return step_or_scenario.scenario
        if isinstance(step_or_scenario, Scenario):
            return step_or_scenario
        raise TypeError("{0} is not an instance of {1} or {2}"
                        .format(step_or_scenario, Step, Scenario))

    @classmethod
    def instance(cls, step_or_scenario):
        """
        :rtype : Driver
        """
        scenario = cls._scenario(step_or_scenario)
        return cls._from(scenario)

    @classmethod
    def has_instance(cls, step_or_scenario):
        try:
            scenario = cls._scenario(step_or_scenario)
        except TypeError:
            return False
        else:
            return scenario.name in cls._registry

    @classmethod
    def kill_instance(cls, scenario):
        if scenario.name not in cls._registry:
            return
        instance = cls._registry.pop(scenario.name)
        instance.quit()

    def __init__(self, config, scenario):
        """
        :param config: fattoush.config.FattoushConfig
        :param scenario: Scenario
        """
        self.fattoush_config = config

        super(Driver, self).__init__(config.command_executor,
                                     config.desired_capabilities(
                                         scenario))

        #self.start_session(config.desired_capabilities)

        kwargs = dict(config=config,
                      browser=self)

        # For saucelabs you need a user name and an auth key
        if "user" in config.server:
            self.sauce = Sauce(**kwargs)
        else:
            self.sauce = Local(**kwargs)