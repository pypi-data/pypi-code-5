import datetime
import json
from logging import getLogger
logger = getLogger(__name__)

catalogs = [
    (('http',), 'data.iledefrance.fr'),
    (('http',), 'opendata.paris.fr.opendatasoft.com'),
    (('http',), 'tourisme04.opendatasoft.com'),
    (('http',), 'tourisme62.opendatasoft.com'),
    (('http',), 'grandnancy.opendatasoft.com'),
    (('http',), 'bistrotdepays.opendatasoft.com'),
    (('http',), 'scisf.opendatasoft.com'),
    (('http',), 'pod.opendatasoft.com'),
    (('http',), 'dataratp.opendatasoft.com'),
    (('http',), 'public.opendatasoft.com'),
    (('http',), 'ressources.data.sncf.com'),
    (('http',), 'data.enseignementsup-recherche.gouv.fr'),
]

def datasets(get, catalog):
    # Search an OpenDataSoft portal, and add things.
    # I chose OpenDataSoft because they care a lot about metadata.
    response = get(catalog + '/api/datasets/1.0/search?rows=1000000')
    result = json.loads(response.text)['datasets']
    for r in result:
        r['catalog'] = catalog
    return result

def dataset_download(get, catalog, datasetid):
    url = '%s/explore/dataset/%s/download/?format=csv' % (catalog, datasetid)
    return get(url)

def download(get, catalog, data, do_standardize):
    '''
    Download everything from an OpenDataSoft catalog.
    '''
    for dataset in datasets(get, catalog):
        try:
            if data:
                dataset['download'] = dataset_download(get, catalog, dataset['datasetid'])
            nonstandard_dataset = dataset
            if do_standardize:
                standard_dataset = standardize(nonstandard_dataset)
                standard_dataset['download'] = nonstandard_dataset.get('download')
                yield standard_dataset
            else:
                yield nonstandard_dataset
        except Exception as e:
            logger.error('Error at %s, %s' % (catalog, dataset['datasetid']))
            logger.error(e)
            break

def standardize(original):
    return {
        'url': '%(catalog)s/explore/dataset/%(datasetid)s' % original,
        "title": original['metas']['title'],
        "creator_name" : original['metas']['publisher'],
        "creator_id": None,
        "date": datetime.datetime.strptime(original['metas']['modified'], '%Y-%m-%dT%H:%M:%S+00:00'),
        "tags" : set(original['metas']['keyword']),
        'colnames': set(field['name'] for field in original['fields']) if 'fields' in original else set(),
    }
