from distutils.core import setup
setup(
    name='leiden',
    version='1.0.2',
    packages=['leiden', 'leiden.broad_cluster', 'leiden.input_output',
              'leiden.lovd', 'leiden.remapping', 'leiden.validation'],
    url='https://github.com/andrewhill157/leiden',
    license='MIT',
    author='Andrew Hill',
    author_email='andrewhill157@gmail.com',
    description='A set of tools for extracting, remapping, and validating variants from the Leiden Open Variation Databases (LOVD)',
    install_requires=['nose', 'hgvs', 'pygr', 'beautifulsoup4']
)
