from setuptools import setup

setup(
    name			= "versioning",
    packages			= [
        "versioning",
    ],
    package_dir			= {
        "versioning":		".", 
    },
    version			= "0.2.1",
    description			= "Python version sorting tool and MySQL version manager",
    author			= "Matthew Brisebois",
    author_email		= "matthew@webheroes.ca",
    url				= "https://github.com/mjbrisebois/pyversioning",
    keywords			= ["pyversioning", "versioning", "version", "version sorting", "mysql version", "mysql"],
    classifiers			= [],
    install_requires		= [
        "mysql-python",
    ],
)
