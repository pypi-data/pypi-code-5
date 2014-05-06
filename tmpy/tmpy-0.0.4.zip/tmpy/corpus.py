#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""This is the definition of Corpus"""

import os
import sys
import copy
#import pandas as pd
from .doc import Document, PlainTextDocument, RCV1Document, Reuters21578Document
from .source import Source
from .helper import read_file, write_file
from .reader import read_plain


class Corpus(object):
    def __init__(self, x=None, meta = None, reader=read_plain, *args, **kwargs):
        """Construct a Corpus instance.

        Parameters
        ===========
        x: Source like object.
            x should have get_info() and get_resources() methods.
        meta: a dict like object.
            It will be recorded as the meta of the Corpus instance.
        reader: a callable.
            Defaultly read_plain from reader module

        Returns
        =======
        result: a Corpus instance
            result would have get_meta(), set_meta(), inspect(),
            map(), map_return_corpus(), map_return_contents_list(),
            filter(), __getitem__(), __setitem__() methods.

        """
        if meta is None:
            meta = {}
        self.meta = meta

        self.docs = []

        if x is None:
            pass #construct an empty Corpus

        elif x.get_info()["type"] == "string":
            if x.get_info()["names"] is None:
                file_names = range(0, len(x))
                file_names = [str(item) for item in file_names]
            else:
                file_names = x.get_info()["names"]
            for i in range(0, len(x)):
                #print(x.get_resources()[i])
                #print(reader)
                doc = reader(x.get_resources()[i], name=file_names[i])
                self.docs = self.docs + [doc]

        elif x.get_info()["type"] == "filename":
            file_names = x.get_info()["names"]
            #files_content = []
            #print(files_content)
            for i in range(0, len(x)):
                pre_file_content = read_file(x.get_resources()[i], x.get_info()["encoding"])
                doc = reader(pre_file_content, name=file_names[i])
                self.docs = self.docs + [doc]

        else:
            pass #construct an empty Corpus

    def __getitem__(self, index):
        """
        reload the index,
        return a sub-Corpus.
        """
        if isinstance(index, basestring):
            for k in range(0, len(self.docs)):
                if self.docs[k].predefinedmetadata["Name"] == index:
                    return self.docs[k]
        elif isinstance(index, slice):
            y = copy.deepcopy(self)
            y.docs = self.docs[index]
            return y
        else:
            return self.docs[index]

    def __setitem__(self, key, item):
        """corpus_instance[i] = another_doc"""
        self.docs[key] = item

    def __iter__(self):
        for x in range(0, len(self)):
            yield self.docs[x]

    def __len__(self):
        """return how many docs in the corpus instance"""
        return len(self.docs)

    def get_meta(self, key=None):
        if key is None:
            return self.meta
        else:
            return self.meta[key]

    def set_meta(self, key, value):
        self.meta[key] = value
        return True

    def inspect(self):
        print("the meta of this corpus:")
        print(self.get_meta())
        print("\npre document in the corpus:\n")
        for doc in self:
            doc.inspect()
        return True

    def map(self, func, *args, **kwargs):
        """map the function inplace"""
        try:
            self.docs = [func(doc, *args, **kwargs) for doc in self.docs]
        except:
            for doc in self.docs:
                doc.set_content(func(doc.get_content(), *args, **kwargs))
        return True

    def map_return_corpus(self, func, *args, **kwargs):
        """map the function on copied corpus and return it"""
        new_corpus = copy.deepcopy(self)
        new_corpus.map(func, *args, **kwargs)
        return new_corpus

    def map_return_contents_list(self, func, *args, **kwargs):
        """map the function on copied corpus and return the contents list"""
        new_corpus = self.map_return_corpus(func, *args, **kwargs)
        return [item.get_content() for item in new_corpus]

    def filter(self, func, *args, **kwargs):
        """
        Filter the documents based on the filter func with parameters.

        Parameters
        ===========
        func: a function or callable.
            For example, s_filter that comes with this package.
        *args: arguments.
            *args would be passed to func.
        **kwargs: key words arguments
            **kwargs would be passed to func.

        Returns
        ========
        result: a new Corpus.
            A new Corpus, all documents of which satisfies the filter function.
        """
        result = Corpus()
        result.meta = self.get_meta()
        for doc in self:
            if func(doc, *args, **kwargs):
                #TODO do not use hack here in the future
                result.docs = result.docs + [doc]
        return result

    def write(self, path = ".", filenames = None):
        if not os.path.exists(path):
            try:
                os.makedirs(path)
            except Exception, e:
                raise e
        for item in self:
            #print(item.content)
            full_path = os.path.join(path, item.get_predefinedmetadata()['Name']+'.txt')
            write_file(item.get_content(), full_path)


def inspect(x):
    return x.inspect()
