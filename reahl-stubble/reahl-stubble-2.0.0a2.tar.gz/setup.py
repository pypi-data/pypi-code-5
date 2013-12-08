from setuptools import setup
setup(
    name='reahl-stubble',
    version=u'2.0.0a2',
    description='Stub tools for use in unit testing',
    long_description=u'Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language. . Stubble (a part of the Reahl development tools) is a collection of tools for writing stubs in unit tests. . Using stubs allows one to decouple one unit test from real code unrelated to it - you write a fake class to take the place of a real one (which this test is not testing). . Stubble ensures, however, that the test will break should the interface of the stub differ from that of the real class it is a stub for. ',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['examples', 'reahl', 'reahl.stubble'],
    py_modules=['setup'],
    include_package_data=False,
    package_data={'': [u'*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=[],
    setup_requires=[],
    tests_require=[u'nose'],
    test_suite=u'reahl.stubble_dev',
    entry_points={
        'reahl.eggs': [
            u'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={}
)
