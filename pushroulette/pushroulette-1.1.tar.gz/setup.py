import ez_setup
ez_setup.use_setuptools()
from setuptools import setup
setup(name='pushroulette',
      version='1.1',
      description='Plays a random 5 second clip from soundcloud for every git push',
      author='Matt Carrier',
      author_email='mcarrieruri@gmail.com',
      url='https://github.com/Astonish-Results/push-roulette',
      py_modules=['ez_setup', 'pushroulette'],
      install_requires=['soundcloud==0.4.1', 'pydub==0.9.2']
      )
