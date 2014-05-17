from django.conf import settings
from bambu_formatrules.formatters import FormatterBase

FORMATTERS = getattr(settings, 'FORMATRULES_FORMATTERS',
    (
        'bambu_formatrules.formatters.block.BlockFormatter',
        'bambu_formatrules.formatters.bookmark.BookmarkFormatter',
    )
)

__version__ = '2.0'