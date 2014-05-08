import json
import functools
import itertools
try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin
from logging import getLogger

logger = getLogger(__name__)

catalogs = [
    (('http','https',), 'data.colorado.gov'),
    (('http','https',), 'data.nola.gov'),
    (('http','https',), 'healthmeasures.aspe.hhs.gov'),
    (('http','https',), 'data.cityofchicago.org'),
    (('http','https',), 'data.wa.gov'),
    (('http','https',), 'opendata.go.ke'),
    (('http','https',), 'data.austintexas.gov'),
    (('http','https',), 'data.cityofnewyork.us'),
    (('http','https',), 'info.samhsa.gov'),
    (('http','https',), 'data.taxpayer.net'),
    (('http','https',), 'data.cityofmadison.com'),
    (('http','https',), 'data.slcgov.com'),
    (('http','https',), 'data.illinois.gov'),
    (('http','https',), 'data.somervillema.gov'),
    (('http','https',), 'iranhumanrights.socrata.com'),
    (('http','https',), 'data.hawaii.gov'),
    (('http','https',), 'data.maryland.gov'),
    (('http','https',), 'data.ny.gov'),
    (('http','https',), 'data.mo.gov'),
    (('http','https',), 'data.nfpa.org'),
    (('http','https',), 'nmfs.socrata.com'),
    (('http','https',), 'data.govloop.com'),
    (('http','https',), 'data.sunlightlabs.com'),
    (('http','https',), 'electionsdata.kingcounty.gov'),
    (('http','https',), 'data.undp.org'),
    (('http','https',), 'deleon.socrata.com'),
    (('http','https',), 'data.energystar.gov'),
    (('http','https',), 'explore.data.gov'),
    (('http','https',), 'data.weatherfordtx.gov'),
    (('http','https',), 'bronx.lehman.cuny.edu'),
    (('http','https',), 'data.sfgov.org'),
    (('http','https',), 'data.edmonton.ca'),
    (('http','https',), 'data.consumerfinance.gov'),
    (('http','https',), 'www.metrochicagodata.org'),
    (('http','https',), 'data.kingcounty.gov'),
    (('http','https',), 'data.baltimorecity.gov'),
    (('http','https',), 'health.data.ny.gov'),
    (('http','https',), 'dati.lombardia.it'),
    (('http','https',), 'datacatalog.cookcountyil.gov'),
    (('http','https',), 'www.opendatanyc.com'),
    (('http','https',), 'cookcounty.socrata.com'),
    (('http','https',), 'data.oregon.gov'),
    (('http','https',), 'data.oaklandnet.com'),
    (('http','https',), 'data.raleighnc.gov'),
    (('http','https',), 'finances.worldbank.org'),
    (('http','https',), 'data.honolulu.gov'),
    (('http','https',), 'opendata.socrata.com'),
    (('http','https',), 'data.cityofboston.gov'),
    (('http','https',), 'data.ok.gov'),
    (('http','https',), 'data.cms.gov'),
    (('http','https',), 'data.snostat.org'),
    (('http','https',), 'www.halifaxopendata.ca'),
    (('http','https',), 'data.wellingtonfl.gov'),
    (('http','https',), 'gettingpastgo.socrata.com'),
    (('http','https',), 'www.data.act.gov.au'),
    (('http','https',), 'data.redmond.gov'),
    (('http','https',), 'data.seattle.gov'),
    (('http','https',), 'data.montgomerycountymd.gov'),
    (('http','https',), 'data.acgov.org'),
    (('http','https',), 'data.medicare.gov'),
]

def page(get, domain_with_scheme, page_number):
    full_url = urljoin(domain_with_scheme, '/api/views?page=%d' % page_number)
    response = get(full_url)
    return json.loads(response.text)

def csv(get, identifier):
    url = 'https://data.cityofnewyork.us/api/views/%s/rows.csv?accessType=DOWNLOAD' % identifier
    return get(url)

def download(get, domain, data):
    pages = (page(get, domain, page_number) for page_number in itertools.count(1))
    for search_results in itertools.takewhile(lambda x: x != [], pages):
        for dataset in search_results:
            func = {
                'href': None,
                'table': csv,
            }.get(dataset['displayType'])
            if func == None:
                func = lambda a, b: None
            if data:
                try:
                    dataset['download'] = func(get, dataset['id']) 
                except Exception as e:
                    logger.error(e)
            yield dataset
