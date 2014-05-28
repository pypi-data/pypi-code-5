import sys

sys.modules[__name__] = lambda agent: "MicroMessenger" in agent
