import os

from pickle_warehouse import Warehouse

home = os.path.expanduser('~')
indices = Warehouse(os.path.join(home, '.,', 'indices'))
values = lambda index: Warehouse(os.path.join(home, '.,', 'values', str(hash(index))))
