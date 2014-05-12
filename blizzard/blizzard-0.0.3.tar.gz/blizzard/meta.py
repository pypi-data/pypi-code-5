import csv, json
from io import StringIO

from more_itertools import ilen
from special_snowflake import fromcsv

def snowflake(dataset):
    dataset.update(individual_metadata(dataset['download'].text))
    del(dataset['download'])
    return dataset

def individual_metadata(dataset_text):
    with StringIO(dataset_text) as fp:
        r = csv.DictReader(fp, delimiter = ';')
        nrow = ilen(r)
        fp.seek(0)
        column_names = next(r)
    with StringIO(dataset_text) as fp:
        unique_keys = list(sorted(fromcsv(fp, delimiter = ';')))
    return {
        'nrow': nrow,
        'unique_keys': unique_keys,
        'column_names': column_names,
    }

def pairwise_metadata(unique_key, left_text, right_text):
    left_hashes = _index_hashes(unique_key, left_text)
    right_hashes = _index_hashes(unique_key, right_text)
    return {
        'nrow_overlap': len(left_hashes.intersection(right_hashes)),
    }

def _index_hashes(unique_key, dataset_text):
    hashes = set()
    with StringIO(dataset_text) as fp:
        r = csv.DictReader(fp, delimiter = ';')
        for row in r:
            hashes.add(tuple(row[column_name] for column_name in sorted(unique_key)))
