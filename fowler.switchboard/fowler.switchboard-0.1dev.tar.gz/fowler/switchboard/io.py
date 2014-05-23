import pandas as pd


def write_cooccurrence_matrix(counter, output, utterances, metadata):
    if output == '-':
        for (row, column), count in counter.items():
            print(row, column, count)
    else:
        write_cooccurrence_matrix_hd5(counter, output, utterances, metadata)


def write_cooccurrence_matrix_hd5(counter, output, utterances, metadata):
    rows_set = set(row for row, _ in counter.keys())
    cols_set = set(col for _, col in counter.keys())

    row2id = pd.Series(range(len(rows_set)), index=rows_set)
    col2id = pd.Series(range(len(cols_set)), index=cols_set)

    row_ids = []
    col_ids = []
    row_labels = []
    col_labels = []
    data = []

    labels = [u.damsl_act_tag() for u in utterances]

    for (row, col), count in counter.items():
        row_labels.append(row)
        col_labels.append(col)
        row_ids.append(row2id[row])
        col_ids.append(col2id[col])
        data.append(count)

    with pd.get_store(output, mode='w', complib='zlib', complevel=9) as store:
        store['row2id'] = row2id
        store['col2id'] = col2id

        store['row_labels'] = pd.Series(row_labels)
        store['col_labels'] = pd.Series(col_labels)
        store['row_ids'] = pd.Series(row_ids)
        store['col_ids'] = pd.Series(col_ids)
        store['data'] = pd.Series(data)
        store['labels'] = pd.Series(labels)

        metadata['documetns'] = len(col2id)
        metadata['features'] = len(row2id)
        store.get_storer('data').attrs.metadata = metadata
