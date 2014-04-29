from distutils.core import setup

setup(
    name='pyhi',
    version='0.2',
    author='LTF sp. z o.o.',
    author_email='mkebaypl2@gmail.com',
    packages=['pyhi'],
    package_data={'pyhi': ['doc/example.py']},
    url='http://historicalinvestor.com',
    license='LICENSE.txt',
    description='HistoricalInvestor trading API',
    long_description=open('README.txt').read(),
    install_requires=[
        "requests>=2.2.1"
    ],
)
