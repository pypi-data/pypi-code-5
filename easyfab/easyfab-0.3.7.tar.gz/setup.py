try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open('LICENSE') as f:
    license = f.read()

requires = [
        'jinja2',
        'fabric',
        'unipath',
]

setup(
    name='easyfab',
    version='0.3.7',
    description='Simple deployments with fabric',
    url='https://github.com/phonkee/easyfab/',
    author='phonkee',
    author_email='phonkee@phonkee.eu',
    license=license,
    packages=[
        'easyfab',
    ],
    scripts=[
        'bin/easyfab'
    ],
    install_requires=requires,
    package_data={
        'easyfab': [
            '*.conf',
            'templates/*.*',
            'templates/deployment/*.*',
            'templates/deployment/conf/*.*',
        ]
    },
    zip_safe=False,
    classifiers=(
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ),
)
