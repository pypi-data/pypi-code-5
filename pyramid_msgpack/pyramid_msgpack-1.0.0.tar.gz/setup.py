
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': "Pyramid view renderer to output in msgpack (as opposed to JSON).",
    'author': 'Parnell Springmeyer',
    'url': 'https://github.com/ixmatus/pyramid_msgpack',
    'download_url': 'https://github.com/ixmatus/pyramid_msgpack',
    'author_email': 'parnell@ixmat.us',
    'version': '1.0.0',
    'install_requires': [
        'nose',
        'u-msgpack-python'
    ],
    'packages': ['pyramid_msgpack'],
    'scripts': [],
    'name': 'pyramid_msgpack'
}

setup(**config)
