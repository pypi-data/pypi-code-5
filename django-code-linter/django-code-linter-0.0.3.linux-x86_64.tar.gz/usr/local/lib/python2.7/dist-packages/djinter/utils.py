# -*- coding: utf-8 -*-


def grep(filepath, match_pattern, dont_match_pattern):
    """
    finds patt in file - patt is a compiled regex
    returns all lines that match patt

    http://grantmcwilliams.com/tech/programming/python/item/581-grep-a-file-in-python

    """
    matchlines = []
    f = open(filepath)
    for line in f.readlines():
        match = match_pattern.search(line)
        if match and not dont_match_pattern.search(line):
            matchlines.append(line)
    results = '\n '.join(matchlines)
    if results:
        return results
    else:
        return None
