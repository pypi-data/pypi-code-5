from distutils.core import setup

setup(
    name='TemplateRender',
    version='0.1.0',
    author='Lethe',
    author_email='lethe30003000@gmail.com',
    packages=['templaterender', 'templaterender.test'],
    # scripts=['bin/stowe-towels.py','bin/wash-towels.py'],
    scripts=[''],
    # url='http://pypi.python.org/pypi/TowelStuff/',
    url='http://pypi.python.org/pypi/TowelStuff/',
    license='LICENSE.txt',
    description='template render based on django',
    long_description=open('README.txt').read(),
    install_requires=[
        # "Django >= 1.1.1",
        # "caldav == 0.1.4",
        ],
)