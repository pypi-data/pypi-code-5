from distutils.core import setup

setup(name="PyOracle",
      version="2",
      description="PyOracle - Audio Oracle and Factor Oracle Analysis in Python",
      author="Greg Surges and Cheng-i Wang",
      author_email='surgesg@gmail.com',
      url='http://www.gregsurges.com/',
      py_modules = ['pyoracle',
                    'factoracle',
                    'oracletest',
                    'extract_features',
                    'examples/bach_cello_demo',
                    'Resources.DrawOracle',
                    'Resources.generate',
                    'Resources.helpers',
                    'Resources.PyOracle.FactOracle',
                    'Resources.PyOracle.IR',
                    'Resources.PyOracle.PyOracle'],
      long_description = 'PyOracle is a project using Python to analyze aspects of musical structure. Audio Oracle, an algorithm based on the Factor Oracle string matching algorithm, is used to detect introductions and repetitions of musical materials. Through this analysis, aspects of musical structure can be understood, and new versions of the analyzed work can be created. You can download a beta version of PyOracle Improviser, a real-time implementation of PyOracle from the Downloads tab above.',
      )
