from setuptools import setup, find_packages
import geocode

setup(
    name='twentytab-geocode',
    version=geocode.__version__,
    description='It\'s a simple python client that uses google geocode api',
    author='20tab S.r.l.',
    author_email='info@20tab.com',
    url='https://github.com/20tab/twentytab-geocode',
    license='MIT License',
    install_requires=[
        'requests>=2',
    ],
    packages=find_packages(),
    include_package_data=True,
    package_data={
        '': ['*.html', '*.css', '*.js', '*.gif', '*.png', ],
}
)
