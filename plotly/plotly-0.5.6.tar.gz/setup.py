from setuptools import setup
exec(open('plotly/version.py').read())
def readme():
	with open('README.txt') as f:
		return f.read()

setup(name='plotly',
      version=__version__,
      description='',
      url='https://plot.ly/api/python',
      author='Chris P',
      author_email='chris@plot.ly',
      classifiers=['Development Status :: 3 - Alpha',
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: 3.3',      
      'Topic :: Scientific/Engineering :: Visualization',
	  ],
      license='MIT',
      packages=['plotly'],
      install_requires=[
      	'requests'
      ],
      zip_safe=False)
