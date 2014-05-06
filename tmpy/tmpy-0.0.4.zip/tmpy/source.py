#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function, unicode_literals)

"""This is all about Source"""

import os
import sys
import pandas as pd


# def get_sources():
#     return ["DirSource", "VectorSource"]


class Source(object):
    """the Soucre"""

    def _check_type(self, x):
        """
        Parameters
        ===========
        x: {list-like, directory_path, file_path}
            Firstly, the function would check whether it is a directory path
            or a file path, if True, create a Source with the pointer and
            names of them, and an attribute showing it is actually a list of
            "filename".
            Secondly, the function would try as x is a list-like, directly
            create the Source with an attribute showing the contents and
            another attributes showing it is actually a list of "string".

        Returns
        =======
        source_type: {"list", "directory", "file", "pure_string", "others"}
            Showing the type of the source.
        """
        source_type = "others"
        if isinstance(x, basestring):
            if os.path.isdir(os.path.expanduser(x)):
                source_type = "directory"
            elif os.path.isfile(os.path.expanduser(x)):
                source_type = "file"
            else:
                # check this almost at the very end
                source_type = "pure_string"
        elif isinstance(x, (list, tuple, set)):
            source_type = "list"
        else:
            # always put this in the end
            source_type = "others"
        return source_type

    def __init__(self, x='.', default_reader = None, encoding = "utf-8",
        names = None, recursive=False, *args, **kwargs):
        """
        Create a Source with an list-like, directory path, or file path,
        or maybe some mystery things.

        Parameters
        ===========
        x: {list-like, directory_path, file_path}, '.' as default
            Firstly, the function would check whether it is a directory path
            or a file path, if True, create a Source with the pointer and
            names of them, and an attribute showing it is actually a list of
            "filename".
            Secondly, the function would try as x is a list-like, directly
            create the Source with an attribute showing the contents and
            another attributes showing it is actually a list of "string".
        default_reader: a callable, None as default
            A callable.
        encoding: a string, "utf-8" as default
            Default encoding.
        names: list of strings, None as default
            The names of each resource.
        recursive: {True, False}, False as default
            If x is a directory, this paremeter would determine whether the
            resources contains the sub directories.

        Returns
        =======
        self: a new Source object
            self would have many attributes

        """
        source_type = self._check_type(x)
        self.source_type = source_type
        self.default_reader = default_reader
        self.encoding = encoding
        self.names = names
        self.recursive = recursive

        if source_type == "list":
            self.content = x
            self.length = len(x)

        elif source_type == "directory":
            self.directory = os.path.realpath(os.path.expanduser(x))
            self.FileList = []
            self.names = []
            for (dir_path, dir_names, file_names) in os.walk(self.directory):
                self.names.extend(file_names)
                self.FileList.extend([os.path.join(dir_path, file_name) for file_name in file_names])
                if not self.recursive:
                    break
            self.length = len(self.names)

        elif source_type == "file":
            self.directory = os.path.dirname(os.path.realpath(os.path.expanduser(x)))
            self.FileList = [os.path.realpath(os.path.expanduser(x))]
            self.names = [os.path.basename(os.path.realpath(os.path.expanduser(x)))]
            self.length = 1

        elif source_type == "pure_string":
            self.content = [x]
            self.length = 1

        elif source_type == "others":
            self.content = x
            self.length = len(x)


    def __len__(self):
        return self.length

    def get_info(self):
        if self.source_type == "list":
            return {"encoding": self.encoding,
             "names": self.names,
             "type": "string"}

        elif self.source_type == "directory":
            return {"encoding": self.encoding,
                "length": self.length,
                "names": self.names,
                "type": "filename"}

        elif self.source_type == "file":
            return {"encoding": self.encoding,
                "length": self.length,
                "names": self.names,
                "type": "filename"}

        elif self.source_type == "pure_string":
            return {"encoding": self.encoding,
                "names": self.names,
                "type": "string"}

        else:
            return {"encoding": self.encoding,
                "length": self.length,
                "names": self.names,
                "type": "string"}

    def get_resources(self):
        if self.source_type == "list":
            return self.content

        elif self.source_type == "directory":
            return self.FileList

        elif self.source_type == "file":
            return self.FileList

        elif self.source_type == "pure_string":
            return self.content

        else:
            return self.content


# class VectorSource(Source):
#     """A vector where each component is interpreted as document"""
#     def __init__(self,
#         x,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         default_reader,
#         encoding,
#         length,
#         names,
#         position,
#         vectorized)
#         self.length = len(x)
#         self.content = x

#     def get_info(self):
#         return {"encoding": self.encoding,
#             "names": self.names,
#             "vectorized": self.vectorized,
#             "type": "string"}

#     def get_resources(self):
#         return self.content

#     def __len__(self):
#         return self.length


# class DataframeSource(Source):
#     """A data frame where each row is interpreted as document"""
#     def __init__(self,
#         x = pd.DataFrame(),
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.content = x
#         self.length = len(self.content)
#     pass


# class DirSource(Source):
#     """A directory with files"""
#     def __init__(self,
#         directory = ".",
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True,
#         pattern = None,
#         recursive = False,
#         ignore_case = False):
#         Source.__init__(self,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         if not os.path.isdir(os.path.expanduser(directory)):
#             sys.exit('not a dir')
#         self.directory = directory
#         self.pattern = pattern
#         self.recursive = recursive
#         self.ignore_case = ignore_case
#         self.FileList = []
#         self.names = []
#         for (dir_path, dir_names, file_names) in os.walk(self.directory):
#             self.names.extend(file_names)
#             self.FileList.extend([os.path.join(dir_path, file_name) for file_name in file_names])
#             if not self.recursive:
#                 break
#         self.length = len(self.names)

#     def get_info(self):
#         return {"encoding": self.encoding,
#             "length": self.length,
#             "names": self.names,
#             "vectorized": self.vectorized,
#             "type": "filename"}

#     def get_resources(self):
#         return self.FileList

#     def __len__(self):
#         return self.length


# class URISource(Source):
#     """Documents identified by a Uniform Resource Identifier"""
#     def __init__(self,
#         x,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#     pass

# class ReutersSource(Source):
#     def __init__(self,
#         x,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#     pass


# class XMLSource(Source):
#     """XML"""
#     def __init__(self,
#         x,
#         parser,
#         reader,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True):
#         Source.__init__(self,
#         default_reader = None,
#         encoding = "utf-8",
#         length = None,
#         names = None,
#         position = 0,
#         vectorized = True)
#         self.x = x
#         self.parser = parser
#         self.reader = reader
#     pass

# def eoi(x):
#     pass

# def eoi_Source(x):
#     pass
