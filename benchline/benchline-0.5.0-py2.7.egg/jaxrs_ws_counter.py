#!/usr/bin/env python
#
# Author: Paul D. Eden <paul@benchline.org>
# Created: 2014-05-13
"""
Script to count the number of JAX-RS web services
defined in .java files in a directory.
"""
import re
import os
import fnmatch

import six

import benchline.args


def read_in_file(file_name):
    """Return the contents of file_name

    >>> import tempfile
    >>> contents = u"This is a test\\nThis is only a test.\\n"
    >>> fo = tempfile.NamedTemporaryFile()
    >>> throw_away = fo.write(contents.encode("UTF-8"))
    >>> fo.flush()
    >>> read_in_file(fo.name) == contents
    True

    :param file_name: string
    :return: string contents of file_name
    """
    with open(file_name) as fo:
        content_str = fo.read()
    return content_str


def count_in_str(pattern, source):
    """Count number of matches of pattern in source

    >>> count_in_str("@GET", "This is a test")
    0
    >>> count_in_str("@GET", "  @GET this")
    1
    >>> count_in_str("@POST", "  @POST this\\n@GET 2\\n@POST 3")
    2

    :param pattern: string
    :param source: string
    :return: int number of matches
    """
    matches = re.findall(pattern, source, re.MULTILINE)
    return len(matches)


def validate_args(parser, options, args):
    if len(args) < 1:
        parser.error("The first positional argument is the directory to search for .java files.")
    if not os.path.isdir(args[0]):
        parser.error("%s is not a directory." % args[0])


def count_operations(dir_name):
    """Count all operations (GETs, PUTs, etc) in .java files in dir_name
    :param dir_name:
    :return: int
    """
    count = 0
    for root, dir_names, file_names in os.walk(dir_name):
        for file_name in fnmatch.filter(file_names, '*.java'):
            contents = read_in_file(os.path.join(root, file_name))
            count += count_in_str("^[\t ]*@GET", contents)
            count += count_in_str("^[\t ]*@PUT", contents)
            count += count_in_str("^[\t ]*@POST", contents)
            count += count_in_str("^[\t ]*@DELETE", contents)
    return count


def main():
    options, args = benchline.args.go(usage="usage: %%prog [options] dir_name\n%s" % __doc__,
                                      validate_args=validate_args)
    operation_count = count_operations(args[0])
    six.print_("Operations: %s" % operation_count)
    six.print_("Resources: Not Yet Implemented")


if __name__ == "__main__":
    main()
