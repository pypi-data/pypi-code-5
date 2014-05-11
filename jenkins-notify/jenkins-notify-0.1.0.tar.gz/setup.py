import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform
import os


def read_file(fname):
    """Utility function to read the README file.
    """
    return open(os.path.join(os.path.dirname('../'), fname)).read()


def get_dependencies():
    """ Utility function to get the dependancies based on OS
    """
    package_dependencies = []
    if platform.system() == "Darwin":
        package_dependencies.append('pync>=1.4')
    elif platform.system() == "Linux" and "Ubuntu" in platform.platform():
        package_dependencies.append('notify2>=0.3')
    else:
        raise NotImplementedError("jenkins-notify has not been implemented"
                                  " on this platform.")

    return package_dependencies

setup(name='jenkins-notify',
      version='0.1.0',
      description='Jenkins build server desktop notification application',
      author='Samuel Jackson',
      author_email='samueljackson@outlook.com',
      url='http://github.com/samueljackson92/jenkins-notify',
      packages=find_packages(),
      install_requires=get_dependencies(),
      long_description=read_file('README.md'),
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Topic :: Software Development',
          ],
      entry_points={
          'console_scripts': ['jenkins-notify=jenkinsnotify.command_line:main']
          }
      )
