# (c) 2014 Mind Candy Ltd. All Rights Reserved.  
# Licensed under the MIT License; you may not use this file except in compliance with the License. 
# You may obtain a copy of the License at http://opensource.org/licenses/MIT.

from setuptools import setup, find_packages
from os import path
import sys


def read_lines(file_name):
    pth = path.join(path.dirname(__file__), file_name)
    with open(pth) as handle:
        return handle.readlines()

try:
    # If all the prerequisites are installed, we can get the
    # version and description from the package itself.

    # This is mainly intended for package creation and upload,
    # and prevents having to store this information in more than one
    # place.
    sys.path.insert(0, path.join(path.dirname(__file__), 'src'))
    import fattoush
    VERSION = fattoush.VERSION
    LONG_DESCRIPTION = fattoush.__doc__

except:

    # If these pre-requisites are not installed, the version module
    # can still be executed, and the long description is not required
    # for successful installation - mainly I just want to have the
    # correct information in pypi.

    VERSION = "UNKNOWN"
    execfile(path.join(path.dirname(__file__),
                       'src/fattoush/config/version.py'))

    LONG_DESCRIPTION = ""

setup(
    name='Fattoush',
    package_data={'': ['*.txt']},
    author='Alistair Broomhead',
    version=VERSION,
    author_email='alistair.broomhead@mindcandy.com',
    description="A delicious testing framework",
    license='MIT',
    #url='https://github.com/mindcandy/fattoush',
    #download_url='https://github.com/mindcandy/fattoush/zipball/master',
    long_description=LONG_DESCRIPTION,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=read_lines("requirements.txt"),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'fattoush = fattoush.runner.bin:console']
    }
)
