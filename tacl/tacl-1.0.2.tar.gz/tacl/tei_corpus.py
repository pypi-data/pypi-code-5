"""Module containing the TEICorpus class."""

import os.path
import re

from lxml import etree


text_name_pattern = re.compile(
    r'^(?P<prefix>[A-Z]{1,2})\d+n(?P<text>\d+)(?P<part>[A-Za-z])$')


class TEICorpus:

    """A TEICorpus represents a collection of TEI XML documents.

    The CBETA texts are TEI XML that are sometimes split into multiple
    files in different directories. This class provides a tidy method
    to consolidate these files so that the stripping process is always
    operating on a single XML document for each text.

    """

    def __init__ (self, input_dir, output_dir):
        self._input_dir = os.path.abspath(input_dir)
        self._output_dir = os.path.abspath(output_dir)
        self._transform = etree.XSLT(etree.XML(SIMPLIFY_XSLT))
        self._texts = {}

    def extract_text_name (self, filename):
        """Returns the name and part letter of the text in `filename`."""
        basename = os.path.splitext(os.path.basename(filename))[0]
        match = text_name_pattern.search(basename)
