import os
from setuptools import setup

# cursed_lich
# The Undead Empire of the nCursed Lich wages war against Humans, Orcs, Elves, Drow, and Dwarves alike!

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "cursed_lich",
    version = "0.1.0",
    description = "NCurses MMO, one of its kind! The Undead Empire strikes.",
    author = "Johan Nestaas",
    author_email = "johannestaas@gmail.com",
    license = "GPLv3+",
    keywords = "cli war mmo console ncurses magic lich undead",
    url = "https://bitbucket.org/johannestaas/cursed_lich",
    packages=['cursed_lich'],
    package_dir={'cursed_lich': 'cursed_lich'},
    long_description=read('README.md'),
    classifiers=[
        #'Development Status :: 1 - Planning',
        'Development Status :: 2 - Pre-Alpha',
        #'Development Status :: 3 - Alpha',
        #'Development Status :: 4 - Beta',
        #'Development Status :: 5 - Production/Stable',
        #'Development Status :: 6 - Mature',
        #'Development Status :: 7 - Inactive',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Environment :: Console',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: POSIX',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
    ],
    install_requires=[
        'sqlalchemy',
        'protobuf>=2.5.0',
        'twisted',
        'service_identity',
    ],
    entry_points = {
        'console_scripts': [
            'cursed_lich_game = cursed_lich.bin:cursed_lich',
            'cursed_lich_server = cursed_lich.bin:cursed_lich_server',
        ],
    },
    #data_files = [
    #    (os.path.join(
    #        os.getenv('HOME'), '.cursed_lich'), 
    #    [
    #        '.cursed_lich/server_config.py'
    #    ]),
    #]
    #package_data = {
        #'cursed_lich': ['catalog/*.edb'],
    #},
    #include_package_data = True,
)
