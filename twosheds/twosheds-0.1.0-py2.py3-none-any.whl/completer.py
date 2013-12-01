"""

    twosheds.completer
    ~~~~~~~~~~~~~~~~~~

    This module implements command completion.

"""
import os
import re
import readline
import sys
import traceback

class Completer(object):
    """A completer completes words when given a unique abbreviation.
    
    Type part of a word (for example `ls /usr/lost') and hit the tab key to
    run the completer.
    
    The shell completes the filename `/usr/lost' to `/usr/lost+found/',
    replacing the incomplete word with the complete word in the input buffer.
    
    (Note the terminal `/'; completion adds a `/' to the end of completed
    directories and a space to the end of other completed words, to speed
    typing and provide a visual indicator of successful completion.
    Completer.use_suffix can be set False to prevent this.)
    
    If no match is found (perhaps `/usr/lost+found' doesn't exist), then no
    matches will appear.
    
    If the word is already complete (perhaps there is a `/usr/lost' on your
    system, or perhaps you were thinking too far ahead and typed the whole
    thing) a `/' or space is added to the end if it isn't already there.

    The shell will list the remaining choices (if any) below the unfinished
    command line whenever completion fails, for example:

        $ ls /usr/l[tab]
        lbin/       lib/        local/      lost+found/

    `excludes` can be set to a list of regular expression patterns to be
    ignored by completion. Consider that the completer were initialized to
    ignore [r'.*~', r'.*.o']:

        $ ls
        Makefile        condiments.h~   main.o          side.c
        README          main.c          meal            side.o
        condiments.h    main.c~
        $ emacs ma[tab]
        main.c

    Completion will always happen on the shortest possible unique match, even
    if more typing might result in a longer match. Therefore:

        $ ls
        fodder   foo      food     foonly
        $ rm fo[tab]

    just beeps, because `fo' could expand to `fod' or `foo', but if we type
    another `o',

        $ rm foo[tab]
        $ rm foo

    the completion completes on `foo', even though `food' and `foonly' also
    match.
    """
    def __init__(self, grammar, use_suffix=True, exclude=None):
        self.grammar = grammar
        self.use_suffix = use_suffix
        self.exclude_patterns = exclude or []

    def inflect(self, filename):
        """Inflect a filename to indicate its type.

        If the file is a directory, the suffix "/" is appended, otherwise
        a space is appended.
        """
        return filename + ("/" if os.path.isdir(filename) else " ")

    def complete_filename(self, word):
        """Find all files that match `word`."""
        head, tail = os.path.split(word)

        filenames = os.listdir(head or '.')

        if tail:
            matches = [os.path.join(head, filename) for filename in filenames
                       if filename.startswith(tail)]
        else:
            # do not show hidden files when listing contents of a directory
            matches = [os.path.join(head, filename) for filename in filenames
                       if not filename.startswith('.')]
        # return results that match anywhere in the file if no results are
        # found
        if not matches:
            matches = [os.path.join(head, filename) for filename in filenames
                       if tail in filename]
        return matches

    def complete_variable(self, word):
        """Get possible variable completions for ``word``.""" 
        for k in os.environ:
            if k.startswith(word):
                yield k

    def get_matches(self, word):
        """Get possible completions for ``word``."""
        for match in self.complete_filename(word):
            yield match
        if word.startswith("$"):
            for match in self.complete_variable(word[1:]):
                yield match

    def exclude_matches(self, matches):
        """Filter any matches that match an exclude pattern."""
        for match in matches:
            for exclude_pattern in self.exclude_patterns:
                if re.match(exclude_pattern, match) is not None:
                    break
            else:
                yield match

    def get_completion_word(self):
        """Get the word to complete."""
        line_buffer = readline.get_line_buffer()
        sentence = self.grammar.expand(line_buffer)
        if sentence.endswith(" "):
            return ""
        else:
            tokens = sentence.split()
            return tokens[-1] if tokens else ""

    def complete(self, text, state):
        """Return the next possible completion for 'text'.

        This is called successively with state == 0, 1, 2, ... until it
        returns None.
        
        The completion should begin with 'text'.
        """
        matches = self.get_matches(self.get_completion_word())
        # defend this against bad user input for regular expression patterns
        try:
            matches = self.exclude_matches(matches)
        except:
            sys.stderr.write(traceback.format_exc())
        if self.use_suffix:
            matches = [self.inflect(match) for match in matches]
        try:
            return list(matches)[state]
        except IndexError:
            return None
