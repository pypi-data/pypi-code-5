#
# Execute this script to copy the coopr/core/*.py files
# and run 2to3 to convert them to Python 3.
#

import glob
import subprocess
import os
import shutil

os.chdir('python2/coopr/core')
for file in glob.glob('*.py'):
    shutil.copyfile(file, '../../../python3/coopr/core/'+file)
for file in glob.glob('*/*.py'):
    shutil.copyfile(file, '../../../python3/coopr/core/'+file)
#
os.chdir('../../../python3/coopr/core')
#
for file in glob.glob('*.py'):
    subprocess.call('2to3 -w '+file, shell=True)
for file in glob.glob('*/*.py'):
    subprocess.call('2to3 -w '+file, shell=True)
