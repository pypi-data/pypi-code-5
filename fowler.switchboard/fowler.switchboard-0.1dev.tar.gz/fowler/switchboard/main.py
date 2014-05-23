from collections import Counter
from itertools import chain

from .util import WordUtterance, writer, get_conversation_ids
from .options import Dispatcher


dispatcher = Dispatcher()
command = dispatcher.command
dispatch = dispatcher.dispatch


@command()
def transcripts(
    utterances,
    format=('f', '{u.caller} {damsl_act_tag}: {u.text}', 'Format.'),
):
    """Print all the transcripts in a human readable way."""
    caller = None
    for utterance in utterances:
        if caller != utterance.caller:
            if caller is not None:
                print()
            caller = utterance.caller

        print(format.format(
            u=utterance,
            damsl_act_tag=utterance.damsl_act_tag(),
        ))


@command()
def tags(
    utterances,
    damsl=('d', False, 'Use the DAMSL tags.')
):
    """Count tag frequencies in the corpora."""
    if not damsl:
        counter = Counter(u.act_tag for u in utterances)
    else:
        counter = Counter(u.damsl_act_tag() for u in utterances)

    for tag, freq in counter.most_common():
        print(freq, tag)


@writer(
    command,
    extra_options=(
        ('', 'train_split', 'downloads/switchboard/ws97-train-convs.list.txt', 'The training splits'),
        ('', 'test_split', 'downloads/switchboard/ws97-test-convs.list.txt', 'The testing splits'),
    ),
)
def word_document(
    utterances,
    ngram_len,
    verbose,
    train_split,
    test_split,
):
    """Word document."""
    utterances = list(utterances)

    train_split = get_conversation_ids(train_split)
    test_split = get_conversation_ids(test_split)

    train_utterances = [u for u in utterances if u.conversation_no in train_split]
    test_utterances = [u for u in utterances if u.conversation_no in test_split]

    assert len(train_utterances) == 213543
    assert len(test_utterances) == 4514

    return WordUtterance(train_utterances + test_utterances, ngram_len=ngram_len, verbose=verbose)


@command()
def trees(utterances):
    for utterance in utterances:
        trees = list(utterance.trees)
        t = trees[0]
        t.draw()


@command()
def tokens(utterances):
    words = chain.from_iterable(u.pos_words() for u in utterances)

    freq = Counter(words)

    for w, f in freq.most_common():
        print(w, '\t', f)
