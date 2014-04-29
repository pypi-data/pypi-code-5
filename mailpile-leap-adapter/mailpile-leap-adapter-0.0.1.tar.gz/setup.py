from setuptools import setup

setup(name='mailpile-leap-adapter',
      version='0.0.1',
      description='Adapter to directly use LEAP mailboxes with Mailpile',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Programming Language :: Python :: 2.7',
          'Topic :: Communications :: Email :: Email Clients (MUA)'
      ],
      keywords = ['mailpile', 'leap', 'email'],
      url='http://github.com/pixelated-team/mailpile-leap-adapter',
      download_url = 'https://github.com/pixelated-team/mailpile-leap-adapter/tarball/0.0.1',
      author='Folker Bernitt',
      author_email='fbernitt@thoughtworks.com',
      license='ALv2',
      packages=['mailpile_leap_adapter'],
      install_requires=[
          'scrypt==0.6.1',
          'dirspec',
          'u1db',
          'leap.common==0.3.7',
          'leap.soledad.common==0.5.0',
          'leap.soledad.client==0.5.0',
          'leap.mail==0.3.8',
          'srp'
      ],
      test_suite='nose.collector',
      tests_require=[
          'nose',
          'mock',
          'httmock'
      ],
      zip_safe=False)

