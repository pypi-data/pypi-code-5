from setuptools import setup

setup(name='roboant_server_desert',
      version='0.4',
      description='Server for the RoboAnt project',
      url='http://github.com/d3kod/roboant',
      author='Aleksandar Kodzhabashev',
      author_email='akodzhabashev@gmail.com',
      license='MIT',
      packages=['roboant_server_desert'],
      scripts=['bin/roboant_server_desert'],
      install_requires=[
          'pygame',
          'twisted',
          'pygame'
          'qrcode'
          'Image'],
      zip_safe=False)
