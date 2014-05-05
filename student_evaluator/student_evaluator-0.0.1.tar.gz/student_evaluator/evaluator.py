"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""


from __future__ import print_function, division  # We require Python 2.6+

import os

from settings import Settings
from logger import Logger
from analyser import Analyser
from reporter import Reporter
from setup import Setup


class StudentEvaluator:
    """ Contains all the tools to analyse assignments """
    errors = 0

    def __init__(self):
        self.settings = Settings()
        self.mylogger = Logger(self.settings.logfile)
        self.reporter = Reporter(self.settings)
        self.analyser = Analyser(self.settings, self.reporter, self.mylogger)
        self.setup = Setup(self.settings)

    def run(self):
        #""" Run the program (call this from main) """
        self.analyser.run()
        self.reporter.run()

    def exit_value(self):
        #"""TODO: Generate the exit value for the application."""
        if (self.errors == 0):
            return 0
        else:
            return 42
