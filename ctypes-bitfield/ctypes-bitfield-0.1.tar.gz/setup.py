from distutils.core import setup

setup(
	name='ctypes-bitfield',
	description='Ctypes Register Bitfields',
	version='0.1',
	py_modules=['bitfield'],
	license='MIT',
	long_description=open('README.txt').read(),

	data_files = [
		('', ['LICENSE.txt'])
	],

	author='Rob Gaddi',
	author_email='rgaddi@highlandtechnology.com'
)
