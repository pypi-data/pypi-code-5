"""
    Student Evaluator
    Copyright 2014, Jeroen Doggen, jeroendoggen@gmail.com
"""

from __future__ import print_function, division  # We require Python 2.6+

import sys
import libuser
import os


class Setup():
    """ Setup class: pre-configure the system """
    admin = libuser.admin()

    def __init__(self, logfile):
        self.create_users("testuser", 5)
#         self.delete_users("testuser", 5)

    def create_users(self, username_prefix, number):
        """Create user accounts on the system """
        os.system("addgroup students")
        for x in range(0, number):
            pass
#             username = username_prefix + str(x)
#             print(username)
#             os.system("useradd -p  SNSr7/A1BYa12 -g students " + username )
#             os.system("adduser --disabled-password " + username + " students")
#             os.system("echo " + username +":SNSr7/A1BYa12" + "| chpasswd -e")
#             os.system("mkdir /home/" + username)
#             os.system("passwd " + username + " " + username)
#             os.system("chown "+ username + ":students " + "/home/" + username )

    def delete_users(self, username_prefix, number):
        """Delete the user accounts (at the end) """
        for x in range(0, number):
            pass
#             username = username_prefix + str(x)
#             os.system("deluser --remove-home " + username )

    def info(self, message):
        self.logger.info(message)
