#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from holmes.facters import Facter


class CSSFacter(Facter):

    def get_facts(self):
        css_files = self.get_css()

        self.review.data['page.css'] = set()
        self.review.data['total.size.css'] = 0
        self.review.data['total.size.css.gzipped'] = 0

        self.add_fact(
            key='page.css',
            value=set(),
            title='CSS',
            unit='css'
        )

        self.add_fact(
            key='total.size.css',
            value=0,
            unit='kb',
            title='Total CSS size'
        )

        self.add_fact(
            key='total.size.css.gzipped',
            value=0,
            unit='kb',
            title='Total CSS size gzipped'
        )

        num_css = 0

        css_to_get = []

        for css_file in css_files:
            src = css_file.get('href')
            if not src.endswith('.css'):
                continue

            if not self.is_absolute(src):
                src = self.rebase(src)

            css_to_get.append(src)
            num_css += 1

        self.add_fact(
            key='total.requests.css',
            value=num_css,
            title='Total CSS requests'
        )

        for url in css_to_get:
            self.async_get(url, self.handle_url_loaded)

    def handle_url_loaded(self, url, response):
        logging.debug('Got response (%s) from %s!' % (response.status_code,
                                                      url))

        self.review.facts['page.css']['value'].add(url)
        self.review.data['page.css'].add((url, response))

        if response.text is not None:
            size_css = len(response.text) / 1024.0
            size_gzip = len(self.to_gzip(response.text)) / 1024.0
        else:
            size_css = 0
            size_gzip = 0

        self.review.facts['total.size.css']['value'] += size_css
        self.review.data['total.size.css'] += size_css

        self.review.facts['total.size.css.gzipped']['value'] += size_gzip
        self.review.data['total.size.css.gzipped'] += size_gzip

    def get_css(self):
        return self.reviewer.current_html.cssselect('link[href]')
