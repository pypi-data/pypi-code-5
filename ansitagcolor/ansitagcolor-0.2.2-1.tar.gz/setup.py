# !/usr/bin/python

from distutils.core import setup


# # Get long_description from index.txt:
f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

setup(
    name="ansitagcolor",
    version="0.2.2-1",
    url="http://github.com/areku/ansitagcolor",
    license="MIT",
    author="Alexander Weigl",
    author_email="alexweigl@gmail.com",
    py_modules=["ansitagcolor"],
    requires=['enum34'],
    test_requires=['nose'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        "Environment :: Console",
        "Intended Audience :: Developers"
    ],


    description="ansi color output defined by tags within the output",
    long_description=long_description
)
