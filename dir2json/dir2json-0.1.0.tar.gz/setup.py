from setuptools import setup

setup(
    name='dir2json',
    py_modules=['dir2json'],
    version='0.1.0',
    author='David Keijser',
    author_email='keijser@gmail.com',
    description='creates a json tree from a directory structure',
    license='MIT',
    extras_require={'tests': ['PyHamcrest']},
    entry_points={
        'console_scripts': [
            'dir2json = dir2json:main'
        ]
    }
)

