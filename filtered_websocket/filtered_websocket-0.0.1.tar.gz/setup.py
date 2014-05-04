import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "filtered_websocket",
    version = "0.0.1",
    author = "Morgan Reece Phillips",
    author_email = "winter2718@gmail.com",
    description = ("A simple framework for constructing websocket servers"
                                   " from filter chains."),
    install_requires=[
        "twisted",
        "redis",
        "redis_collections",
        "TwistedWebsocket",
    ],
    license = "BSD",
    keywords = "websocket TwistedWebsocket",
    url = "https://github.com/mrrrgn/filtered_websocket/tarball/0.0.1",
    packages=[
        "filtered_websocket",
        "filtered_websocket.filters",
        "filtered_websocket.storage_objects",
    ],
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
