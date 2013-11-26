#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import logging

from holmes.facters import Facter
from holmes.utils import get_domain_from_url

REMOVE_HASH = re.compile('([#].*)$')
URL_RE = re.compile(
    r'^(?:http|ftp)s?://'  # http:// or https://
    r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
    r'localhost|'  # localhost...
    r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
    r'(?::\d+)?'  # optional port
    r'(?:/?|[/?]\S+)$', re.IGNORECASE)


class LinkFacter(Facter):
    def looks_like_image(self, url):
        image_types = ['png', 'webp', 'gif', 'jpg', 'jpeg']
        for image_type in image_types:
            if url.endswith(image_type):
                return True

        return False

    def get_facts(self):
        links = self.get_links()

        self.review.data['page.links'] = set()
        self.review.data['page.all_links'] = links

        self.add_fact(
            key='page.links',
            value=set(),
            title='Links',
            unit='links'
        )

        num_links = 0

        links_to_get = set()

        for link in links:
            url = link.get('href').strip()
            url = REMOVE_HASH.sub('', url)

            if not url:
                continue

            if self.looks_like_image(url):
                continue

            is_absolute = self.is_absolute(url)

            should_get = False
            if not is_absolute:
                url = self.rebase(url)
                should_get = True
            else:
                domain, domain_url = get_domain_from_url(url)
                if domain in self.page_url:
                    should_get = True

            if should_get and URL_RE.match(url):
                num_links += 1
                links_to_get.add(url)

        for url in links_to_get:
            self.async_get(url, self.handle_url_loaded)

        self.add_fact(
            key='total.number.links',
            value=num_links,
            title='Link Count'
        )

    def handle_url_loaded(self, url, response):
        logging.debug('Got response (%s) from %s!' % (response.status_code, url))
        self.review.facts['page.links']['value'].add(url)
        self.review.data['page.links'].add((url, response))

    def get_links(self):
        return self.reviewer.current_html.cssselect('a[href]')
