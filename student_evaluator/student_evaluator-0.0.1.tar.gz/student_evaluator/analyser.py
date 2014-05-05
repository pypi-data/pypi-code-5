"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""


from __future__ import print_function, division  # We require Python 2.6+

import os

from logger import Logger


class Analyser():
    """ Timer to check the speed of the tool itself (benchmarking) """
    txt_files_list = []
    studentnames_list = []

    def __init__(self, settings, logger, reporter):
        self.settings = settings
        self.logger = logger
        self.reporter = reporter

    def run(self):
        """ Run all tests, staring narrowing down the scope step by step """
        self.check_folders()
        self.check_file("dummy filename")

    def check_folders(self):
        for folder in self.settings.folders_list:
            path = os.path.join(os.getcwd(), self.settings.folder_prefix, folder)
            if (os.path.isdir(path)):
                print("Found folder: " + folder)
                for subfolder in self.settings.subfolders_list:
                    subpath = os.path.join(path, subfolder)
                    if (os.path.isdir(subpath)):
                        print("Found subfolder: " + subfolder)

    def check_folder(self, filename):
        """ Check if a file exists """
        pass

    def check_file(self, filename):
        """ Check if a file exists """
        pass

    def check_access_rights(self, filename, rights):
        """ Check if a file/folder has the correct access rights """
