from .common import RUTRACKER_URL
from .common import clear_text, html_from_url
from .common import categories, pages, subforums, topics, next_page
from .common import PageBlocked

__version__ = '0.5.2'
__description__ = 'Package to parse rutracker.org forum'
requires = [
    'beautifulsoup4 >= 4'
]

README = __description__
