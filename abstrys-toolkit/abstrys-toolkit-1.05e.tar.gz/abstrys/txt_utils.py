# abstrys text utility functions and classes.
import re

def camel2snake(text, sep=r'_'):
    """Convert *text* from CamelCase (or camelCase) into snake_case."""
    rebounds = [r'([a-z])([A-Z])', r'([A-Z])([A-Z])']
    # make a copy, don't operate on original.
    ophic_text = str(text)
    for b in rebounds:
        ophic_text = re.sub(b, (r'\g<1>'+ sep + r'\g<2>'), ophic_text)
    return ophic_text.lower()


def snakeify(text, sep=r'_'):
    """Snakeify the input text: convert spaces to underscores and lowercase
    everything. Return the result"""
    ophic_text = sep.join(text.split()).lower()

    # remove any quote characters
    ophic_text = re.sub('[\?\!\@\#\$\%\^\*<\'\">]', '', ophic_text)

    # turn commas into sep characters
    ophic_text = re.sub('[,:;]', sep, ophic_text)

    # remove any periods that are followed by a sep character.
    ophic_text = ophic_text.replace('.%s' % sep, sep)

    # remove any sep characters that follow an open brace or parentheses.
    ophic_text = ophic_text.replace('(%s' % sep, "(")
    ophic_text = ophic_text.replace('[%s' % sep, "[")
    ophic_text = ophic_text.replace('{%s' % sep, "{")

    # replace any '&' or '+' characters with the word 'and'
    ophic_text = re.sub('[&\+]', 'and', ophic_text)

    # reduce sequence of dashes or underscores to a single sep character
    ophic_text = re.sub('[\-_]+', sep, ophic_text)

    return ophic_text

