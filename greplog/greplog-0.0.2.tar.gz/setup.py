import os
from setuptools import setup

# greplog
# Grep through log files from a set of servers, and sort by time

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "greplog",
    version = "0.0.2",
    description = "Grep through log files from a set of servers, and sort by time",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    license = "GPLv3+",
    keywords = "",
    url = "https://bitbucket.org/johannestaas/greplog",
    packages=['greplog'],
    package_dir={'greplog': 'greplog'},
    long_description=read('README.md'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        #'Development Status :: 2 - Pre-Alpha',
        'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: Console',
        'Environment :: X11 Applications :: Qt',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        'fabric',
    ],
    entry_points = {
        'console_scripts': [
            'greplog = greplog.bin:greplog',
        ],
    },
    data_files = [
        (os.path.join(os.getenv('HOME'), '.greplog'), [
            '.greplog/default.py',
            '.greplog/servers.py',
            ]
        )
    ],
    #package_data = {
        #'greplog': ['catalog/*.edb'],
    #},
    #include_package_data = True,
)
