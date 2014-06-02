VERSION = (0, 0, 1,)
__version__ = '.'.join(map(str, VERSION))

from .paginators import ExPaginator, DiggPaginator, QuerySetDiggPaginator
