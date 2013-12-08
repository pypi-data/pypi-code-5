# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import codecs

from ..utils.tnt import TnT

data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                         'tag.marshal')
tagger = TnT()
tagger.load(data_path)


def train(file_name):
    fr = codecs.open(file_name, 'r', 'utf-8')
    data = []
    for i in fr:
        line = i.strip()
        if not line:
            continue
        tmp = map(lambda x: x.split('/'), line.split())
        data.append(tmp)
    fr.close()
    tagger.train(data)


def tag_all(words):
    return tagger.tag(words)


def tag(words):
    return map(lambda x: x[1], tag_all(words))
