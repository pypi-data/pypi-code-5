#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""about how to produce a stopwords list"""

from os import path
from nltk.corpus import stopwords as nltk_corpus_stopwords
from .helper import read_file

def words(language):
    """input a language name, like "english", and returns the stopwords list"""
    return nltk_corpus_stopwords.words(language)
