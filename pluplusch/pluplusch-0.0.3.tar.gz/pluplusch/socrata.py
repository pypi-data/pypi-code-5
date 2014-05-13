from io import StringIO
import datetime
import json
import functools
import itertools
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from logging import getLogger

from pluplusch.csv_colnames import colnames

logger = getLogger(__name__)

catalogs = [
    (('https','http',), 'data.colorado.gov'),
    (('https','http',), 'data.nola.gov'),
    (('https','http',), 'healthmeasures.aspe.hhs.gov'),
    (('https','http',), 'data.cityofchicago.org'),
    (('https','http',), 'data.wa.gov'),
    (('https','http',), 'opendata.go.ke'),
    (('https','http',), 'data.austintexas.gov'),
    (('https','http',), 'data.cityofnewyork.us'),
#   (('https','http',), 'info.samhsa.gov'),
    (('https','http',), 'data.taxpayer.net'),
    (('https','http',), 'data.cityofmadison.com'),
    (('https','http',), 'data.slcgov.com'),
    (('https','http',), 'data.illinois.gov'),
    (('https','http',), 'data.somervillema.gov'),
    (('https','http',), 'iranhumanrights.socrata.com'),
    (('https','http',), 'data.hawaii.gov'),
    (('https','http',), 'data.maryland.gov'),
    (('https','http',), 'data.ny.gov'),
    (('https','http',), 'data.mo.gov'),
    (('https','http',), 'data.nfpa.org'),
#   (('https','http',), 'nmfs.socrata.com'),
#   (('https','http',), 'data.govloop.com'),
    (('https','http',), 'data.sunlightlabs.com'),
    (('https','http',), 'electionsdata.kingcounty.gov'),
    (('https','http',), 'data.undp.org'),
#   (('https','http',), 'deleon.socrata.com'),
    (('https','http',), 'data.energystar.gov'),
    (('https','http',), 'explore.data.gov'),
    (('https','http',), 'data.weatherfordtx.gov'),
    (('https','http',), 'bronx.lehman.cuny.edu'),
    (('https','http',), 'data.sfgov.org'),
    (('https','http',), 'data.edmonton.ca'),
    (('https','http',), 'data.consumerfinance.gov'),
    (('https','http',), 'www.metrochicagodata.org'),
    (('https','http',), 'data.kingcounty.gov'),
    (('https','http',), 'data.baltimorecity.gov'),
    (('https','http',), 'health.data.ny.gov'),
    (('http',), 'dati.lombardia.it'),
    (('https','http',), 'datacatalog.cookcountyil.gov'),
    (('https','http',), 'www.opendatanyc.com'),
    (('https','http',), 'cookcounty.socrata.com'),
    (('https','http',), 'data.oregon.gov'),
    (('https','http',), 'data.oaklandnet.com'),
    (('https','http',), 'data.raleighnc.gov'),
    (('https','http',), 'finances.worldbank.org'),
    (('https','http',), 'data.honolulu.gov'),
    (('https','http',), 'opendata.socrata.com'),
    (('https','http',), 'data.cityofboston.gov'),
    (('https','http',), 'data.ok.gov'),
    (('https','http',), 'data.cms.gov'),
    (('http',), 'data.snostat.org'),
    (('https','http',), 'www.halifaxopendata.ca'),
    (('https','http',), 'data.wellingtonfl.gov'),
    (('https','http',), 'gettingpastgo.socrata.com'),
    (('https','http',), 'www.data.act.gov.au'),
    (('http',), 'data.redmond.gov'),
    (('https','http',), 'data.seattle.gov'),
    (('https','http',), 'data.montgomerycountymd.gov'),
    (('https','http',), 'data.acgov.org'),
    (('https','http',), 'data.medicare.gov'),
]
catalogs = []

def page(get, domain_with_scheme, page_number):
    full_url = urljoin(domain_with_scheme, '/api/views?page=%d' % page_number)
    response = get(full_url)
    return json.loads(response.text)

def csv(get, identifier):
    url = 'https://data.cityofnewyork.us/api/views/%s/rows.csv?accessType=DOWNLOAD' % identifier
    return get(url)

def download(get, domain, data, do_standardize):
    pages = (page(get, domain, page_number) for page_number in itertools.count(1))
    for search_results in itertools.takewhile(lambda x: x != [], pages):
        for dataset in search_results:
            try:
                func = {
                    'href': None,
                    'table': csv,
                    'tabular': csv,
                }.get(dataset.get('displayType', dataset['viewType']))
                if func == None:
                    func = lambda a, b: None
                if data:
                    try:
                        dataset['download'] = func(get, dataset['id']) 
                    except Exception as e:
                        logger.error('Error downloading full data for %s, %s' % (domain, dataset['id']))
                        logger.error(e)
                dataset['catalog'] = domain
                nonstandard_dataset = dataset
                if do_standardize:
                    standard_dataset = standardize(nonstandard_dataset)
                    standard_dataset['download'] = nonstandard_dataset.get('download')
                    if nonstandard_dataset['download'] != None:
                        standard_dataset['colnames'] = colnames(StringIO(standard_dataset['download'].text))
                    yield standard_dataset
                else:
                    yield nonstandard_dataset
            except Exception as e:
                logger.error('Error at %s, %s' % (domain, dataset['id']))
                logger.error(e)
                break

def standardize(original):
    return {
        'url': '%(catalog)s/d/%(id)s' % original,
        'title': original['name'],
        'creator_name' : original['owner']['displayName'],
        'creator_id': 'https://healthmeasures.aspe.hhs.gov/d/' + original['owner']['id'],
        'date': datetime.datetime.fromtimestamp(max(original.get(key, 0) for key in ['createdAt','publicationDate', 'rowsUpdatedAt', 'viewLastModified'])),
        'tags' : set(original['tags']),
        'colnames': set(),
    }
