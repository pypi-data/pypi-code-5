from collections import OrderedDict

import pandas as pd

from fowler.switchboard import io

import pytest


@pytest.fixture
def output(tmpdir):
    return str(tmpdir.join('store.hd5'))


@pytest.fixture
def counter():
    return OrderedDict((
        ('aZ', 3),
        ('bY', 4),
        ('aX', 2),
        ('cW', 1),
    ))


@pytest.fixture
def utterances():

    class Utterance(object):
        @staticmethod
        def damsl_act_tag():
            return 'Q'

    return [
        Utterance,
        Utterance,
        Utterance,
        Utterance,
        Utterance,
    ]


@pytest.fixture
def metadata():
    return {
        'key': 'value',
        'other key': 'other value',
    }


def test_write_cooccurrence_matrix_hd5(counter, output, utterances, metadata):
    io.write_cooccurrence_matrix_hd5(counter, output, utterances, metadata)

    with pd.get_store(output) as store:

        row2id = store['row2id']
        assert row2id.ix['a'] != row2id.ix['b']
        with pytest.raises(KeyError):
            row2id.ix['Z']

        col2id = store['col2id']
        assert col2id.ix['Z'] != col2id.ix['Y']
        with pytest.raises(KeyError):
            col2id['a']

        assert tuple(store['row_labels']) == tuple('abac')
        assert tuple(store['col_labels']) == tuple('ZYXW')
        assert tuple(store['row_ids']) == tuple(row2id[r] for r in store['row_labels'])
        assert tuple(store['col_ids']) == tuple(col2id[c] for c in store['col_labels'])

        assert tuple(store['data'].values) == (3, 4, 2, 1)

        assert store.get_storer('data').attrs.metadata == metadata
