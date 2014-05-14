import setuptools

setuptools.setup(
    name='cell_acceptance',
    version="0.2.6",
    description='LibreOffice Calc Calculation Engine',
    long_description='LibreOffice Calc Calculation Engine',
    author='James Rakich',
    author_email='james@fullandbydesign.com.au',
    url='https://bitbucket.org/MalucoMarinero/cellacceptance',
    packages=['cell_acceptance', 'cell_acceptance.oosheet'],
    install_requires=['flask', 'requests'],
    scripts=['bin/cell-acceptance-load-calc'],
    entry_points = {
        'console_scripts': ['cell-acceptance=cell_acceptance.server:run_server']
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    license='MIT License',
    zip_safe=False,
    keywords='testing'
)
