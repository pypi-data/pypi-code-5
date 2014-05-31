# -*- coding: utf-8 -*-
"""
    sphinxjp.tk0miya
    ~~~~~~~~~~~~~~~~~~~~~~~~

    :copyright: Copyright 2014 by WAKAYAMA Shirou
    :license: BSD, see LICENSE for details.
"""

import sys
import random


import flickr_api

from docutils import nodes, utils
from docutils.parsers.rst import directives
from sphinx.util.compat import Directive


FLICKR_IMAGE_TEMPLATE = '''
<img src="{0}" />
'''


class searchnode(nodes.General, nodes.Element):
    pass


class SearchDirective(Directive):
    has_content = False
    required_arguments = 1
    optional_arguments = 1
    option_spec = {
        'random': directives.flag,
    }

    def run(self):
        env = self.state.document.settings.env
        api_key = env.config.flickr_api_key
        secret = env.config.flickr_secret

        if api_key is None or secret is None:
            # TODO: how to use warning?
            env.warn(__name__, 'please set your api_key and secret in conf.py')
            return []

        size = "Medium"  # TODO

        node = searchnode(api_key=api_key,
                          secret=secret,
                          searchtags=self.arguments[0],
                          random=('random' in self.options),
                          size=size)
        return [node]


def visit_search_node(self, node):
    searchtags = node['searchtags']
    api_key = node['api_key']
    secret = node['secret']
    size = node['size']

    try:
        flickr_api.set_keys(api_key=api_key, api_secret=secret)

        photos = flickr_api.Photo.search(tags=searchtags)

        if node['random']:
            p = random.choice(photos)
        else:
            p = photos[0]

        url = p.getPhotoFile(size_label="Medium")
        html = FLICKR_IMAGE_TEMPLATE.format(url)
        self.body.append(html)

    except Exception, e:
        self.builder.warn('fail to load flickr. check api_key in your conf.py')
        raise nodes.SkipNode


def depart_search_node(self, node):
    pass


def setup(app):
    app.add_config_value('flickr_api_key', None, 'env')
    app.add_config_value('flickr_secret', None, 'env')

    app.add_node(searchnode, html=(visit_search_node, depart_search_node))

    app.add_directive('flickr-search', SearchDirective)
