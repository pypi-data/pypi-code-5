import distutils.core

distutils.core.setup(
        name='KeepMePosted',
        version='0.2',
        author='Kale Kundert',
        author_email='kale@thekunderts.net',
        py_modules=['kemepo'],
        url='https://github.com/kalekundert/KeepMePosted',
        download_url='https://github.com/kalekundert/KeepMePosted/tarball/0.2',
        license='LICENSE.txt',
        description="""\
An object-oriented event handling framework where events are registered by 
classes and then broadcasted by individual objects.  Listening for events from 
specific objects is made easy.""",
        long_description=open('README.txt').read(),
        keywords=['event handling'])
