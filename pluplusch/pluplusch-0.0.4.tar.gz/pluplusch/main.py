import os
from concurrent.futures import ThreadPoolExecutor
import logging
import functools

from thready import threaded
from pickle_warehouse import Warehouse
from picklecache import cache
import requests

import pluplusch.index as i

def getlogger():
    logger = logging.getLogger(__name__)
    fp_stream = logging.StreamHandler()
    fp_stream.setLevel(logging.ERROR)
    logger.addHandler(fp_stream)
    return logger
logger = getlogger()

def _pluplusch(get, catalogs = [], standardize = True, download_data = False):
    '''
    pluplusch downloads data from open data websites. Here are
    its inputs.

    catalogs
        List of catalogs to download, each item being either
        a full URL string, including the scheme, or a tuple
        of the full URL string and the software, in case pluplusch
        doesn't know about the catalog
    standardize
        Should the metadata schema be standardized across softwares?
    download_data
        Should the full data file be downloaded if needed?
        (This is only relevant if standardize is True.)

    It returns a generator of datasets.
    '''

    # Use all catalogs by default.
    if catalogs == []:
        catalogs = list(i.all_catalogs())

    # Detect catalog softwares if they're not specified.
    catalog_names = [(catalog[0] if len(catalog) == 2 else catalog) for catalog in catalogs]
    catalog_softwares = [(catalog[1] if len(catalog) == 2 else i.catalog_to_software(catalog)) for catalog in catalogs]
    catalog_names_softwares = list(zip(catalog_names, catalog_softwares))

    # Threading
    queue = []
    running = set(catalog_names)
    submodules = i.submodules()

    def enqueue_datasets(catalog_name_software):
        catalog_name, catalog_software = catalog_name_software
        try:
            for dataset in submodules[catalog_software].metadata(get, catalog_name):
                if not standardize:
                    out = dataset
                    out['_catalog'] = catalog_name
                    out['_software'] = catalog_software
                else:
                    out = submodules[catalog_software].standardize(dataset)
                    if catalog_software == 'ckan' and not download_data:
                        # Getting column names from CKAN involves downloading all the data
                        out['colnames'] = set()
                    else:
                        out['colnames'] = submodules[catalog_software].colnames(get, dataset)
                queue.append(out)
        except Exception as e:
            logger.error(e)
        running.remove(catalog_name)

    threaded(catalog_names_softwares, enqueue_datasets, join = False)

    from time import sleep
    while len(running) > 0:
        sleep(0.0001)
        if queue != []:
            yield queue.pop(0)

def pluplusch(catalogs = [], standardize = True, download_data = False,
        cache_dir = os.path.join(os.path.expanduser('~'), '.pluplusch')):
    '''
    pluplusch downloads data from open data websites. Here are
    its inputs.

    cache_dir
        Directory to store the cache in
    catalogs
        List of catalogs to download, each item being either
        a full URL string, including the scheme, or a tuple
        of the full URL string and the software, in case pluplusch
        doesn't know about the catalog
    standardize
        Should the metadata schema be standardized across softwares?
    download_data
        Should the full data file be downloaded if needed?
        (This is only relevant if standardize is True.)

    It returns a generator of datasets.
    '''

    @cache(cache_dir, mutable = False)
    def _get(url):
        return requests.get(url, verify = False)
    def get(url):
        try:
            response = _get(url)
        except Exception as e:
            logger.error('Could not download ' + url)
            logger.error(e)
            raise e
        if response.ok:
            return response
        else:
            raise ValueError('%d response at %s' % (response.status_code, url))

    yield from _pluplusch(get, catalogs = catalogs, standardize = standardize,
                          download_data = download_data)
