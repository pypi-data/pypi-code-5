from itertools import combinations
import json, pickle

import networkx as nx

class Graph(nx.Graph):
    def add_dataset(self, dataset):
        dataset_id = (dataset['catalog'], dataset['datasetid'])
       #dataset_url = '%s/explore/dataset/%s' % (dataset['catalog'], dataset['datasetid'])
        self.add_node(dataset_id, kind = 'dataset')
        for unique_index in dataset['unique_keys']:
            i = tuple(sorted(unique_index))
            self.add_node(i, kind = 'index')
            self.add_edge(i, dataset_id)

    def similarly_indexed_datasets(self):
        'Returns an iterable of (dataset node, dataset node)'
        indices = (index for index,data in self.nodes(data = True) if data['kind'] == 'index')
        seen = set()
        for index in indices:
            for datasets in combinations(self.neighbors(index),2):
                a, b = tuple(sorted(datasets))
                if not ((a, b) in seen or (b, a) in seen):
                    yield a, b
                    seen.add((a, b))
