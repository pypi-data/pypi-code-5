# -*- coding: utf-8 -*-
from distutils.core import setup

import digg_paginator

setup(
    name = "django-digg-paginator",
    version = digg_paginator.__version__,
    packages = ["digg_paginator"],
    url = 'https://github.com/alrusdi/django_digg_paginator',
    author = ' Michael Elsdörfer',
    author_email = 'michael@elsdoerfer.com',
    maintainer = 'alrusdi',
    maintainer_email = 'alrusdi@gmail.com',
    license = 'GPL3',
    description = 'Digg-like Paginator from Django Snippets',
    long_description = open('README', 'r').read(),
    download_url = 'https://github.com/alrusdi/django_digg_paginator/archive/master.zip',
    classifiers = [
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
)
