"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""


import os
import ConfigParser
import argparse

class Settings:
    """ Contains all the tools to analyse Blackboard assignments """
    logfile = "student_evaluator.log"
    summary_file = 'summary.log'
    script_path = os.getcwd()
    input_path = script_path
    output_path = script_path
    config_file = "settings.conf"
    Config = ConfigParser.ConfigParser()
    Log = ConfigParser.ConfigParser()
    working_dir = os.getcwd()
    folders_list = []
    subfolders_list = []
    students = 0

    parser = argparse.ArgumentParser(
        prog="student_evaluator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="student_evaluator commandline arguments:",
        epilog="Report bugs to jeroendoggen@gmail.com.")

    def __init__(self):
        self.read_config_file(self.config_file)
        self.cli_arguments()

    def config_section_map(self, section):
        """ Helper function to read config settings """
        dict1 = {}
        options = self.Config.options(section)
        for option in options:
            try:
                dict1[option] = self.Config.get(section, option)
                if dict1[option] == -1:
                    DebugPrint("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
                sys.exit(1)
        return dict1

    def read_config_file(self, filename):
        """ Read the config  """
        try:
            self.Config.read(filename)
            self.folder_prefix = self.config_section_map("Config")['prefix']
            for number, folder in enumerate(self.Config.items("Folders")):
                self.folders_list.append(folder[1])
            for number, subfolder in enumerate(self.Config.items("SubFolders")):
                self.subfolders_list.append(subfolder[1])
        except AttributeError:
            #TODO: this does not work!! (AttributeError or KeyError needed? both?)
            print("Error while processing config file")
            sys.exit(1)

    def cli_arguments(self):
        """Configure a read all the cli arguments."""
        self.configure_cli_arguments()
        self.get_cli_arguments()

    def configure_cli_arguments(self):
        """Configure all the cli arguments."""
        self.parser.add_argument("-s", metavar="students",
          help="Number of user accounts to create for the students")
        self.parser.add_argument('-l', metavar='logfile',
          help="Set the name the logfile to use")

    def get_cli_arguments(self):
        """Read all the cli arguments."""
        args = self.parser.parse_args()
        if (args.s is not None):
            self.students = args.s
        if (args.l is not None):
            self.logfile = args.l

