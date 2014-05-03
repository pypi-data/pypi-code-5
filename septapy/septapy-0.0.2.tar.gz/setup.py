from distutils.core import setup

setup(
    name = 'septapy',
    packages = ['septapy'],
    version = '0.0.2',
    description = 'Library for querying SEPTA public transit API',
    author = 'Conor Schaefer',
    author_email = 'conor.schaefer@gmail.com',
    url = 'https://github.com/ronocdh/septapy',
    download_url = 'https://github.com/ronocdh/septapy/tarball/0.0.1',
    install_requires=[
        'requests>=2.2.1',
        ],
    keywords = ['transit', 'API', 'Philadelphia', 'SEPTA'],
    classifiers = [],
)
