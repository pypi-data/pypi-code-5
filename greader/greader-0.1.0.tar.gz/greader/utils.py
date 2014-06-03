import xml.dom.minidom


def get_continuation_from_string(string):
    return get_continuation_from_dom(xml.dom.minidom.parseString(string))


def get_continuation_from_dom(x):
    ret = None
    try:
        ret = x.getElementsByTagName('gr:continuation')[0].childNodes[0].data
    except:
        pass
    return ret


def get_items_from_string(string):
    return get_items_from_dom(xml.dom.minidom.parseString(string))


def get_items_from_handler(handler):
    return get_items_from_dom(xml.dom.minidom.parse(handler))


def get_items_from_dom(x):
    ret = []

    for e in x.getElementsByTagName('entry'):
        item = e.getElementsByTagName('id')[0].childNodes[0].data
        stream = e.getElementsByTagName('source')[0].getAttribute('gr:stream-id')
        ret.append({'stream': stream, 'item': item})

    return ret
