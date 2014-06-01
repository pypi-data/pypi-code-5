#
# Execute this script to copy the pyutilib/component/core/*.py files
# and run 2to3 to convert them to Python 3.
#

import glob
import subprocess
import os
import shutil

os.chdir('python2/pyutilib/component/core')
for file in glob.glob('*.py'):
    shutil.copyfile(file, '../../../../python3/pyutilib/component/core/'+file)
#
os.chdir('../../../../python3/pyutilib/component/core')
#
for file in glob.glob('*.py'):
    subprocess.call('2to3 -w '+file, shell=True)
