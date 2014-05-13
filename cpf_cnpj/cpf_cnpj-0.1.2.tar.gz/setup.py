# -*- coding:utf-8 -*-

import os
from setuptools import setup, find_packages

def parse_requirements(requirements):
    with open(requirements) as f:
        return [l.strip('\n') for l in f if l.strip('\n') and not l.startswith('#')]

required = parse_requirements('requirements.txt')

setup(
    install_requires=required,
    name = "cpf_cnpj",
    version = '0.1.2',
    description = "Validador de CPF e CNPJ para Python",
    license = "MIT",
    author = "Adriano Margarin",
    author_email = "adriano.margarin@gmail.com",
    url = "https://github.com/amargarin/cpf_cnpj",
    packages = find_packages(exclude = ['tests']),
    keywords = "python cpf cnpj validador",
    zip_safe = True
)
