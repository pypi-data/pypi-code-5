"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""

from __future__ import print_function, division  # We require Python 2.6+

import os


class Reporter():
    """ Logging class """

    def __init__(self, settings):
        self.settings = settings

    def run(self):
        """ Write statistics to files """
        self.write_summary()

    def write_summary(self):
        """ Write a summary of the analysis process to a logfile """
        try:
            os.chdir(self.settings.output_path)
            outfile = open(self.settings.summary_file, 'w+')
            outfile.write("Build summary:\n")
            outfile.write("--------------\n")
            outfile.write(" Total students: ")
            outfile.write("\n Best grade: ")
            outfile.write("\n Worst grade: ")
            outfile.write("\n Errors: ")
            outfile.write("\n Comments: \n")
            outfile.close()
            with open(self.settings.summary_file) as f:
                content = f.read()
                print(content)
            outfile.close()
        except OSError:
            self.exit_program("writing the summary")

    def exit_program(self, message):
        """ Exit the program with an error message
           TODO: this should move somewhere else (needed in multiple places)
        """
        print("Error while " + message)
        print("Closing application")
        sys.exit()
