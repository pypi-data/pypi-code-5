import warnings
import os

from craigsgenerator import craigsgenerator
import requests

from cloud_beds.db import db, get_session

def get_generator():
    if 'http_proxy' in os.environ:
        proxies = {'http': os.environ['http_proxy']}
    else:
        warnings.warn('I\'m not using a proxy because no http_proxy is set')
        proxies = {}

    def get(url):
        return requests.get(url, proxies = proxies)

    cachedir = os.path.join(os.environ['HOME'], 'dadawarehouse.thomaslevine.com', 'cloud-beds')
    sections = ['sub','roo','zip','maa','tla','gra']
    sites = [
        'philadelphia.craigslist.org','newyork.craigslist.org','newyork.craigslist.org',
        'chicago.craigslist.org','washingtondc.craigslist.org','sfbay.craigslist.org',
        'montreal.fr.craigslist.ca','nashville.craigslist.org',
    ]

    return craigsgenerator(get = get, threads_per_section = 10, superthreaded = False,
                           sites = sites, sections = sections,
                           cachedir = cachedir, scheme = 'http')

def main():
    database = os.environ['CLOUD_BEDS_DB']
    cg = get_generator()
    sink = db(get_session(database))
    for listing in cg:
        sink.send(listing)
