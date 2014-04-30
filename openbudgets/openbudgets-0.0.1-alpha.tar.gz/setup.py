from setuptools import setup, find_packages


##### DO NOT TRY TO USE THIS YET! #####


# with open('README.rst') as f:
#     long_description = f.read()

setup(name='openbudgets',
      version='0.0.1-alpha',
      description='(WIP - DO NOT USE) A web app and web API for storing, '
                  'accessing, visualizing and comparing budgetary data.',
      # long_description=long_description,
      url='https://github.com/openbudgets/openbudgets',
      author='Paul Walsh, Yehonatan Daniv',
      author_email='paulywalsh@gmail.com, maggotfish@gmail.com',
      license='BSD',
      packages=find_packages(),
      install_requires=["Django >= 1.6.3"],
      zip_safe=False)
