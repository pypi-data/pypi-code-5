import sys
from itertools import chain
from collections import Counter, deque
from functools import wraps

from .io import write_cooccurrence_matrix


def WordUtterance(utterances, ngram_len, verbose=False):
    for document_id, utterance in enumerate(utterances):
        ngrams = utterance_ngrams(utterance, ngram_len=ngram_len)

        if verbose:
            sys.stderr.write(
                'Document id: {document_id}\n'
                'Words: {ngrams}\n'
                '\n'.format(
                    document_id=document_id,
                    ngrams=' '.join(ngrams),
                )
            )

        # TODO: it would be nice to treat utterances that don't
        # contain any word differently.
        if not ngrams:
            yield '<NON_VERBAL>', document_id
        for ngram in ngrams:
            yield ngram, document_id


def writer(
    command,
    extra_options=tuple(),
):
    def wrapper(f):
        options = extra_options + (
            ('n', 'ngram_len', 1, 'Length of the tokens (bigrams, ngrams).'),
            ('o', 'output', 'swda-{limit}items-{ngram_len}gram.h5', 'The output file.'),
            ('v', 'verbose', False, 'Be verbose.'),
        )

        @command(options=options)
        @wraps(f)
        def wrapped(
            utterances_iter,
            output,
            corpus,
            limit,
            **context
        ):
            counter = Counter(f(utterances_iter(), **context))

            output = output.format(
                limit=limit,
                ngram_len=context['ngram_len'],
            )

            metadata = {
                'ngram length': context['ngram_len'],
            }

            return write_cooccurrence_matrix(counter, output, utterances_iter(), metadata)

        return wrapped

    return wrapper


def get_conversation_ids(f_name):
    """Read the conversation ids from test/train split.

    The splits are:

     * http://www.stanford.edu/~jurafsky/ws97/ws97-train-convs.list
     * http://www.stanford.edu/~jurafsky/ws97/ws97-test-convs.list

    """
    with open(f_name) as f:
        return set(int(l.strip()[2:]) for l in f)

