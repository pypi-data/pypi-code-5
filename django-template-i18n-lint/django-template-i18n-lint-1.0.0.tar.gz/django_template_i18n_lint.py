#! /usr/bin/python
"""
Prints out all
"""

import os
import re
import sys
from optparse import OptionParser


def location(str, pos):
    """Given a string str and an integer pos, find the line number and character in that line that correspond to pos"""
    lineno, charpos = 1, 1
    counter = 0
    for char in str:
        if counter == pos:
            return lineno, charpos
        elif char == '\n':
            lineno += 1
            charpos = 1
            counter += 1
        else:
            charpos += 1
            counter += 1

    return lineno, charpos

# Things that are OK:
GOOD_STRINGS = re.compile(
    r"""
          # django comment
       ( {%\ comment\ %}.*?{%\ endcomment\ %}

         # already translated text
        |{%\ ?blocktrans.*?{%\ ?endblocktrans\ ?%}

         # any django template function (catches {% trans ..) aswell
        |{%.*?%}

         # CSS
        |<style.*?</style>

         # JS
        |<script.*?</script>

         # A html title or value attribute that's been translated
        |(?:value|title|summary|alt)="{%\ ?trans.*?%}"

         # A html title or value attribute that's just a template var
        |(?:value|title|summary|alt)="{{.*?}}"

         # An <option> value tag
        |<option[^<>]+?value="[^"]*?"

         # Any html attribute that's not value or title
        |[a-z:-]+?(?<!alt)(?<!value)(?<!title)(?<!summary)='[^']*?'

         # Any html attribute that's not value or title
        |[a-z:-]+?(?<!alt)(?<!value)(?<!title)(?<!summary)="[^"]*?"

        # Any html attribute that's not value or title
        |[a-z:-]+?(?<!alt)(?<!value)(?<!title)(?<!summary)=[^\W]*?[(\w|>)]

         # Boolean attributes
        |<[^<>]+?(?:checked|selected|disabled|readonly|multiple|ismap|defer|declare|noresize|nowrap|noshade|compact)[^<>]*?>

         # HTML opening tag
        |<[\w:]+

         # End of a html opening tag
        |>
        |/>

         # closing html tag
        |</.*?>

         # any django template variable
        |{{.*?}}

         # any django template tag
        |{%.*?%}

         # HTML doctype
        |<!DOCTYPE.*?>

         # IE specific HTML
        |<!--\[if.*?<!\[endif\]-->

         # HTML comment
        |<!--.*?-->

         # HTML entities
        |&[a-z]{1,10};

        # HTML entities
        |&\#x[0-9]{1,10};

         # CSS style
        |<style.*?</style>

         # another common template comment
        |{\#.*?\#}
        )""",

    # MULTILINE to match across lines and DOTALL to make . include the newline
    re.MULTILINE | re.DOTALL | re.VERBOSE | re.IGNORECASE)

# Stops us matching non-letter parts, e.g. just hypens, full stops etc.
LETTERS = re.compile("\w")


def replace_strings(filename):
    full_text_lines = []
    for index, message in enumerate(GOOD_STRINGS.split(open(filename).read())):
        if index % 2 == 0 and re.search("\w", message):
            before, message, after = re.match("^(\s*)(.*?)(\s*)$", message, re.DOTALL).groups()
            message = message.strip().replace("\n", "").replace("\r", "")
            change = raw_input("Make '%s' translatable? [Y/n] " % message)
            if change == 'y' or change == "":
                message = '%s{%% trans "%s" %%}%s' % (before, message, after)
        full_text_lines.append(message)

    full_text = "".join(full_text_lines)
    if options.overwrite:
        save_filename = filename
    else:
        save_filename = filename.split(".")[0] + "_translated.html"
    open(save_filename, 'w').write(full_text)
    print "Fully translated! Saved as: %s" % save_filename


def non_translated_text(template):

    offset = 0

    # Find the parts of the template that don't match this regex
    # taken from http://www.technomancy.org/python/strings-that-dont-match-regex/
    for index, match in enumerate(GOOD_STRINGS.split(template)):
        if index % 2 == 0:

            # Ignore it if it doesn't have letters
            if LETTERS.search(match):
                lineno, charpos = location(template, offset)
                yield (lineno, charpos, match.strip().replace("\n", "").replace("\r", "")[:120])

        offset += len(match)


def print_strings(filename):
    with open(filename) as fp:
        file_contents = fp.read()

    for lineno, charpos, message in non_translated_text(file_contents):
        print "%s:%s:%s:%s" % (filename, lineno, charpos, message)


def main():
    parser = OptionParser(usage="usage: %prog [options] <filenames>")
    parser.add_option("-r", "--replace", action="store_true", dest="replace",
                      help="Ask to replace the strings in the file.", default=False)
    parser.add_option("-o", "--overwrite", action="store_true", dest="overwrite",
                      help="When replacing the strings, overwrite the original file.  If not specified, the file will be saved in a seperate file named X_translated.html", default=False)
    parser.add_option("-e", "--exclude", action="append", dest="exclude_filename",
                      help="Exclude these filenames from being linted", default=[])
    (options, args) = parser.parse_args()

    # Create a list of files to check
    if len(args) == 0:
        args = [os.getcwd()]
    files = []
    for arg in args:
        if os.path.isdir(arg):
            for dirpath, dirs, filenames in os.walk(arg):
                files.extend(os.path.join(dirpath, fname)
                             for fname in filenames
                             if (fname.endswith('.html') or fname.endswith('.txt')) and fname not in options.exclude_filename)
        else:
            files.append(arg)

    for filename in files:
        if options.replace:
            replace_strings(filename)
        else:
            print_strings(filename)

if __name__ == '__main__':
    main()
