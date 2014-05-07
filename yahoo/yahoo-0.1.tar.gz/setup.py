from setuptools import setup

setup(name = "yahoo",
      version = "0.1",
      description = "Yahoo search results with python",
      long_description=open('README.rst', 'r').read(),
      author = "Carlos Ganoza Plasencia",
      author_email = "cganozap@gmail.com",
      url = "https://github.com/drneox/yahoo",
      license = "GPL v3.0",
      packages=["yahoo"],
      keywords= "search engine scraping yahoo",
      install_requires = ["requests==1.1.0", "beautifulsoup4==4.3.2"],

)
