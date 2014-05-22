from distutils.core import setup

setup(
    name='SecureSubmit',
    version='1.5.1',
    author='Heartland Payment Systems',
    author_email='EntApp_DevPortal@e-hps.com',
    packages=[
        'securesubmit',
        'securesubmit.entities',
        'securesubmit.entities',
        'securesubmit.infrastructure',
        'securesubmit.services',
        'securesubmit.tests'],
    scripts=['bin/run_tests.py'],
    url='http://developer.heartlandpaymentsystems.com/SecureSubmit',
    license='LICENSE.txt',
    description='SDK for integrating with the Heartland Portico Gateway',
    long_description=open('README.txt').read(),
    install_requires=['xmltodict >= 0.9.0']
)
