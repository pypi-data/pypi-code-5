from setuptools import setup, find_packages
setup(
    name = "Zen",
    version = "0.1",

    install_requires = ['requests','django',],
    py_modules=['zen'],
    author = "Binal Patel",
    author_email = "binalkp91@gmail.com",
    description = "A simple way to access the ZenDesk v2 API via Python.",
    keywords = "zendesk api ticketing helpdesk",
    url = "https://github.com/caesarnine/zen_python"
)
