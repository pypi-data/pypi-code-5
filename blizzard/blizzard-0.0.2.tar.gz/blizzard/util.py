import os
import argparse
from logging import getLogger

logger = getLogger('blizzard')

def ignore(dataset):
    url = dataset_url(dataset['catalog'], dataset['datasetid'])
    if 'geo_shape' in set(f['type'] for f in dataset['fields']):
        logger.debug('csv parser can\'t handle geo data at %s' % url)
        return True
    elif not dataset['download'].ok:
        logger.debug('Skipping status code %d at %s' % (dataset['download'].status_code, url))
        return True
    elif dataset['download'].text.strip() == '':
        logger.debug('Empty file at %s' % url)
        return True
    else:
        return False

def parser():
    p = argparse.ArgumentParser()
    p.add_argument('command', choices = ['index', 'graph'])
    return p

def dataset_url(catalog, datasetid):
    return '%s/explore/dataset/%s' % (catalog, datasetid)

def dataset_download_url(catalog, datasetid):
    return '%s/explore/dataset/%s/download/?format=csv' % (catalog, datasetid)
