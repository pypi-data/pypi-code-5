from concurrent.futures import ThreadPoolExecutor
import logging

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

def pluplusch(catalogs = None, cache_dir = '.pluplusch', proxies = {}, data = False, standardize = False):
    '''
    pluplusch downloads data from open data websites. Here are
    its inputs.

    catalogs
        List of catalogs do download, each item being either
        a full URL string, including the scheme, or a tuple
        of the full URL string and the software, in case pluplusch
        doesn't know about the catalog
    cache_dir
        String directory to cache downloads to
    proxies
        A dictionary containing any or neither of "http_proxy"
        and "https_proxy"
    data
        Should the full datasets be downloaded (True), or should
        just the metadata be downloaded (False)?
    standardize
        Should the metadata be reduced and standardized across data
        catalog softwares (True), or should they be kept as is (False)?

    It returns a generator of datasets.
    '''

    @cache(cache_dir, mutable = False)
    def _get(url):
        return requests.get(url, proxies = proxies, verify = False)
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

    submodules = i.submodules()

    if catalogs == None:
        # Use all catalogs.
        catalogs = list(i.all_catalogs())

    catalog_names = ((catalog[0] if len(catalog) == 2 else catalog) for catalog in catalogs)
    catalog_softwares = ((catalog[1] if len(catalog) == 2 else i.catalog_to_software(catalog)) for catalog in catalogs)
    standardized_catalogs = zip(catalog_names, catalog_softwares)

    generators = {catalog_name: getattr(submodules[catalog_software], 'download')(get, catalog_name, data, standardize) for (catalog_name, catalog_software) in standardized_catalogs}
    def f(generator):
        try:
            return next(generator)
        except StopIteration:
            pass
        except Exception as e:
            logger.error(e)

    while generators != {}:
        with ThreadPoolExecutor(len(generators)) as e:
            datasets = e.map(f, generators.values())
            remove = set()
            for catalog, dataset in zip(list(generators.keys()), datasets):
                if dataset == None:
                    remove.add(catalog)
                else:
                    yield dataset
            for catalog in remove:
                del(generators[catalog])
