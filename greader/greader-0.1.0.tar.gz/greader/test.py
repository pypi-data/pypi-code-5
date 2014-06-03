#!/usr/bin/env python

import time
import greader.API
import greader.utils

TESTS = {
    'parse-gatom': False,
    'list-tag': False,
    'upload-tag': True
    }


def main():
    u2 = '****@gmail.com'
    p2 = '****'

    """
    Parse gatom file
    """
    if TESTS['parse-gatom']:
        i = greader.utils.get_items_from_handler(open('shared.xml'))
        i.reverse()

        for r in i:
            print str(r)

    """
    List remote tag
    """
    if TESTS['list-tag']:
        api = greader.API.API(u2, p2)
        api.login()
        for i in api.list_tag('like'):
            print i

    """
    Upload a tag
    """
    if TESTS['upload-tag']:
        tag = 'broadcast'
        api = greader.API.API(u2, p2)
        api.login()
        items = greader.utils.get_items_from_handler(tag + '.xml')
        items.reverse()
        n = len(items)
        s = 194
        c = s + 1
        for i in items[s:]:
            print "Tagging with '%s' %d of %d: %s" % (tag, c, n,  str(i))
            api.add_tag(tag, i['stream'], i['item'])
            c = c + 1
            time.sleep(3)

if __name__ == '__main__':
    main()
