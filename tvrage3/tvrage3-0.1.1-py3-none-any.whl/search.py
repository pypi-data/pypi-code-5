import urllib.request
import urllib.parse
import xmltodict
from tvrage3.api import Show

QUICK_URL = 'http://services.tvrage.com/tools/quickinfo.php?show='
SEARCH_URL = ('http://services.tvrage.com/feeds/full_search.php?show=')
ID_URL = 'http://services.tvrage.com/feeds/showinfo.php?sid='


def quick_info(name, exact=False):
    """Search tvrage for name, will return the first match as a Show
    object. If nothing is found it will return 'None' value. If exact is
    'True' then it will only return an exact match against search term."""
    url_name = urllib.parse.quote_plus(name)
    if exact:
        url = QUICK_URL + url_name + '&exact=1'
    else:
        url = QUICK_URL + url_name
    response = urllib.request.urlopen(url).read().decode()
    if response[:7] == 'No Show':
        return None
    return Show(quick_info=response)


def search(name):
    """Search tvrage for name, will return all search results as a list of
    'Show' objects."""
    url_name = urllib.parse.quote_plus(name)
    response = urllib.request.urlopen(SEARCH_URL + url_name).read()
    shows_info = xmltodict.parse(response)
    if shows_info['Results'] == '0':
        return []
    if isinstance(shows_info['Results']['show'], dict):
        return [Show(search_info=shows_info['Results']['show'])]
    results = []
    for show_info in shows_info['Results']['show']:
        results.append(Show(search_info=show_info))
    return results


def search_id(id):
    """Will return 'Show' object with show of supplied id. If no show
    is found with with supplied id then 'None' value is returned."""
    response = urllib.request.urlopen(ID_URL + id).read()
    show_info = xmltodict.parse(response)
    if not show_info['Showinfo']:
        return None
    return Show(full_info=show_info['Showinfo'])
