from setuptools import setup

setup(
    name='KatoAdhocExpress',
    version='0.9',
    license='BSD',
    author='Elvis',
    author_email='elvis@maestraslolutions.com',
    url='https://kato.im/',
    long_description="README.txt",
    packages=['katoAdhocExpress'],
    include_package_data=True,
    package_data={},
    description="Kato Adhoc Express",
	install_requires=[
    'PyJWT>=0.2.1'
	]
)