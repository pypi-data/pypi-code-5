from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='wordcount_file',
      version='0.2',
      description='Counts the words in an ASCII file.',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Indexing',
      ],
      keywords='word count text file',
      url='http://github.com/esoupy/wordcount_file',
      author='Eric Sales',
      author_email='eric@soupynet.com',
      license='MIT',
      packages=['wordcount_file'],
      zip_safe=False)