from setuptools import setup, find_packages


README = open('README.rst').read()


setup(name="semantic_web_pygments",
      author="Philip Cooper",
      author_email="philip.cooper@openvest.com",
      classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python'],
      download_url = 'https://pypi.python.org/pypi/semantic_web_pygments',
      description=u"Pygments lexer for semantic web languages",
      entry_points = {
        "pygments.lexers" : [
          "n3 = semantic_web_pygments:Notation3Lexer",
          "sparql = semantic_web_pygments:SparqlLexer"
        ]
      },
      include_package_data=True,
      install_requires=["pygments"],
      license="BSD",
      long_description=README,
      packages=find_packages(),
      url = "http://github.com/globocom/semantic-web-pygments",
      version="0.1.0"
)
