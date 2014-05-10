# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'

def ichunk(s, chunk_size):
    """
    Create an iterator which yield chunk string with specified size
 
    Args:
        s (str): A base string
        chunk_size (int): A chunk string length
 
    Yields:
        Chunked string
    """
    for index in xrange(0, len(s), chunk_size):
        yield s[index:index+chunk_size]


