import setuptools

setuptools.setup(
    name='cell_acceptance',
    version="0.1.0",
    description='LibreOffice Calc Calculation Engine',
    long_description=open('README.md').read().strip(),
    author='James Rakich',
    author_email='james@fullandbydesign.com.au',
    url='http://path-to-my-packagename',
    py_modules=['cell_acceptance'],
    install_requires=['flask', 'requests'],
    tests_require=['nose'],
    license='MIT License',
    zip_safe=False,
    keywords='testing'
)
