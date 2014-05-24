'''routines generally helpful for dealing with icky xml'''

from collections import defaultdict
import re
import xml.dom.minidom
from xml.etree import cElementTree as ElementTree

from dhp.VI import iteritems

# pylint: disable=W0141
def etree_to_dict(tree):
    '''transform element tree to a dictionary'''
    d_parent = {tree.tag: {} if tree.attrib else None}
    children = list(tree)

    if children:
        # make __missing__ returns an empty list
        dd_l = defaultdict(list)
        for d_child in map(etree_to_dict, children):
            for k, val in iteritems(d_child):
                dd_l[k].append(val)

        temp = {}
        for k, val in iteritems(dd_l):
            if len(val) == 1:
                temp[k] = val[0]
            else:
                temp[k] = val
        d_parent = {tree.tag: temp}

    if tree.attrib:
        d_parent[tree.tag
                ].update(('@' + k, val) for k, val in iteritems(tree.attrib))

    if tree.text:
        text = tree.text.strip()

        if children or tree.attrib:
            if text:
                d_parent[tree.tag]['#text'] = text
        else:
            d_parent[tree.tag] = text

    return d_parent

def xml_to_dict(xml):
    '''convert xml string to a dictionary, not always pretty, but reliable'''

    eltree = ElementTree.XML(xml)
    return etree_to_dict(eltree)


def ppxml(xmls):
    '''pretty print xml, stripping an existing formatting'''

    #xml_doc = xml.dom.minidom.parse(xml_fname)
    xml_doc = xml.dom.minidom.parseString(xmls)
    better_xml = xml_doc.toprettyxml(indent='  ')
    text_re = re.compile(r'>\n\s+([^<>\s].*?)\n\s+</', re.DOTALL)
    outbuf = ''
    buf = text_re.sub(r'>\g<1></', better_xml)
    for line in buf.split('\n'):
        if len(line.strip()):
            outbuf += line
            outbuf += '\n'
    return outbuf
