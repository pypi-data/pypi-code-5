from setuptools import setup, find_packages
from dad import __version__


README = open('README.rst').read()


setup(name="DAD",
      author="Globo.com",
      author_email="semantica@corp.globo.com",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
      download_url = 'https://pypi.python.org/pypi/DAD',
      description=u"Deliver Asynchronous Data",
      include_package_data=True,
      install_requires=["stomp.py==3.1.3", "ujson==1.30"],
      license="GNU GPLv2",
      long_description=README,
      packages=find_packages(),
      tests_require=["coverage==3.6", "nose==1.2.1", "pep8==1.4.1"],
      url = "http://github.com/globocom/dad",
      version=__version__
)
