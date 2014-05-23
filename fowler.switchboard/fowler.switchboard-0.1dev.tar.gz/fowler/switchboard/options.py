import inspect
from itertools import islice

import opster

from .swda import CorpusReader


class Dispatcher(opster.Dispatcher):
    def __init__(self, *globaloptions):
        globaloptions = (
            tuple(globaloptions) +
            (
                ('l', 'limit', 0, 'Limit the number of utterances by this value.'),
                ('p', 'path', './swda', 'The path to the swda dir.'),
            )
        )

        super(Dispatcher, self).__init__(
            globaloptions=globaloptions,
            middleware=_middleware,
        )


def _middleware(func):
    def wrapper(*args, **kwargs):
        if func.__name__ == 'help_inner':
            return func(*args, **kwargs)

        f_args = inspect.getargspec(func)[0]

        limit = kwargs.pop('limit')
        path = kwargs.pop('path')

        corpus = CorpusReader(path)

        def utterances_iter():
            utterances = corpus.iter_utterances(display_progress=False)
            if limit:
                utterances = islice(utterances, limit)

            for u in utterances:
                yield u

        if 'utterances' in f_args:
            kwargs['utterances'] = utterances_iter()

        if 'utterances_iter' in f_args:
            kwargs['utterances_iter'] = utterances_iter

        if 'corpus' in f_args:
            kwargs['corpus'] = corpus

        if 'limit' in f_args:
            kwargs['limit'] = limit

        return func(*args, **kwargs)

    return wrapper
