from distutils.core import setup

setup(name='cache_flusher',
      version='1.0',
      author='Roberto Agostino Vitillo',
      author_email='ra.vitillo@gmail.com',
      description='Disk cache flusher',
      url='https://github.com/vitillo/python_cache_flusher',
      py_modules=['cache_flusher'],
      data_files=[('data', ['data/Flush.exe'])])
