import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages
import platform


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

    package_dependencies.append('jenkinsapi>=0.2.19')
    return package_dependencies

setup(name='jenkins-notify',
      version='0.1.4',
      description='Jenkins build server desktop notification application',
      author='Samuel Jackson',
      author_email='samueljackson@outlook.com',
      url='http://github.com/samueljackson92/jenkins-notify',
      packages=find_packages(),
      scripts=['ez_setup.py'],
      install_requires=get_dependencies(),
      long_description='Monitor Jenkins build servers for changes and show desktop notifications.',
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
