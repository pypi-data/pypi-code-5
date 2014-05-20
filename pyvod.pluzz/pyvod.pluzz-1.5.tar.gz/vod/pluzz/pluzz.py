"""\
Pluzz Downloader

Downloads a movie from the French Television VOD

Usage:
  pypluzz gui [<id>] [-t <target>] [--avconv <avconv>] [--verbose]
  pypluzz fetch <id> [-t <target>] [--avconv <avconv>] [--verbose]
  pypluzz get <id> [<key>...] [--verbose]
  pypluzz show <id> [--verbose]
  pypluzz list [<category>] [<channel>] [-l <limit>] [-s <sort>] [-i] [--verbose]
  pypluzz search <query> [<category>] [<channel>] [-l <limit>] [-s <sort>] [-i] [--verbose]

Commands:
  gui                    Launch graphical user interface.
  get                    Get list of keys.
  get <key>              Get value for key.
  show                   Give summary for key.
  fetch                  Download the TV show.
  list                   List TV shows.
  search <query>         Search a TV show.

Options for `list` and `search` commands:
  <query>                Terms of the show to look up.
  <category>             Category to list. `help` or no value gives the list.
  <channel>              Channels to list. `help` or no value gives the list.
  -l --limit <limit>     Number of shows to output. [default: 100]
  -s --sort <sort>       Sort the output (alpha, date, relevance) [default: alpha]
  -i --image             Show thumbnail image URL for the show

Options for `get`, `show` and `fetch` commands:
  <id>                   URL or ID of the TV show
  -t --target <target>   Target directory to download the file to [default: ~/Downloads]
  --avconv <avconv>      Sets full path to avconv binary [default: /usr/bin/avconv]
  -V --verbose           Show more output.
  -h --help              Show this screen.

(c)2014 Bernard `Guyzmo` Pratz
Under the WTFPL <http://wtfpl.net>
"""

import sys
import json
import time
import textwrap
import itertools
from lxml import etree

from vod.ui.cli import run
from vod.video import AVConvDownloader
from vod.vodservice import VodService
from vod.vodservice import VodServiceShow

class PluzzShow(VodServiceShow):
    @property
    def id(self):
        return self['id']

    @property
    def title(self):
        return self['titre']

    @property
    def image(self):
        return self['image']

    def save(self, target_path="~/Downloads", callback=lambda p, t, d, s: print(p, t, d, s), avconv_path='/usr/bin/avconv', verbose=False):
        with self.downloader(target_path, avconv_path, verbose) as downloader:
            p = self.get(list(filter(lambda x: x['format'] == 'm3u8-download', self.data['videos']))[0]['url']).text
            video_url = list(filter(lambda l: "index_2" in l, p.split()))[0]
            dest_file = "{}_{}.mkv".format(self.data['code_programme'], self.id)
            return downloader.save(dest_file, video_url, callback)

    def get_summary(self):
        t_when = time.strftime(_("On %d %h %Y at %H:%M"), time.localtime(self['diffusion']['timestamp']))
        # t_until = time.strftime(_("On %d %h %Y at %H:%M"), time.localtime(m['diffusion']['???']))
        yield _('Id'),          str(self['id']),                                          'short'
        # yield _('AEDRA'),       self['id_aedra'],                                       'short'
        yield _('Broadcast'),   t_when,                                                   'short'
        #yield _('Until'),       t_until,                                                 'short'
        yield _('Length'),      str(self['duree']),                                       'short'
        yield _('Genre'),       str(self['genre']),                                       'short'
        yield _('Season'),      str(self['saison']),                                      'short'
        yield _('Channel'),     str(self['chaine']),                                      'short'
        yield _('Rights'),      str(self['droit']['csa']),                                'short'
        yield _('Picture'),     str("http://pluzz.francetv.fr/{}".format(self['image'])), 'image'
        yield _('Website'),     str(self['url_site']),                                    'link'
        yield _('Pluzz'),       str(self['url_site']),                                    'link'

    def get_crew(self):
        for p in self['personnes']:
            yield ", ".join(p['fonctions']), p['prenom'], p['nom']

    def get_synopsis(self):
        for line in textwrap.wrap(self['synopsis'], initial_indent="    "):
            yield "  {}".format(line)

class PluzzService(VodService):
    Show = PluzzShow

    SORT= {'relevance': 'pertinence', 'date': 'date', 'alpha': 'alpha'}

    search_url = 'http://pluzz.francetv.fr/ajax/launchsearch/{filter}/{sort}/nb/{limit}'
    video_url = "http://webservices.francetelevisions.fr/tools/getInfosOeuvre/v2/?idDiffusion={show}&catalogue=Pluzz"
    filter_category = 'rubrique/{}'
    filter_channel = 'chaine/{}'
    filter_query = 'requete/{}'
    filter_page = 'debut/{}'
    sort = 'tri/{}'

    _main_page_cache = None;

    def get_categories(self):
        if self._main_page_cache is None:
            self._main_page_cache = etree.HTML(self.get('http://pluzz.francetv.fr/a-z').text)
        return [i.attrib['value'] for i in self._main_page_cache.xpath('id("chx_rubrique")/li/input')] + ['all']

    def get_channels(self):
        if self._main_page_cache is None:
            self._main_page_cache = etree.HTML(self.get('http://pluzz.francetv.fr/a-z').text)
        return [i.attrib['data-chaine'] for i in self._main_page_cache.xpath('id("chx_chaine")/li')] + ['all']

    def list(self, query=None, category=None, channel=None, limit=100, sort="", page=0):
        filter_ = [""]

        if category == "all": category = None
        if channel == "all": channel = None

        if    query: filter_ += [self.filter_query.format(query)]
        if category: filter_ += [self.filter_category.format(category)]
        if  channel: filter_ += [self.filter_channel.format(channel)]

        if sort:
            try:
                sort = self.SORT[sort]
            except KeyError:
                sort = ""

        url = self.search_url.format(filter="/".join(filter_),
                              sort=self.sort.format(sort),
                              limit=limit)

        h = etree.HTML(self.get(url).text)
        if h.xpath('//span[@class="noresult-big"]/text()'):
            if self.verbose:
                print(h.xpath('//span[@class="noresult-big"]/text()'), file=sys.stderr)
            raise Exception("No results found")
        l = h.xpath('//article/h3/a|//article/a/img')
        return [self.Show({'id': i[0].attrib['href'].split(',')[-1].split('.')[0],
                           'titre': i[0].text.strip(),
                           'image': i[1].attrib['data-src']}) for i in itertools.zip_longest(*[iter(l)]*2, fillvalue=None)]

    def get_show(self, uri):
        if uri.startswith('http://') and 'pluzz' in uri:
            p = etree.HTML(self.get(uri).text)
            show_id = p.xpath('//meta[@property="og:url"]/@content')[0].split(',')[-1].split('.')[0]
        else:
            show_id = uri
        print(_('Get Data…'), end="\r", file=self.out)
        show = json.loads(self.get(self.video_url.format(show=show_id)).text)
        if 'code' in show.keys() and show['status'] == 'NOK':
            raise Exception(show['message'])
        return self.Show(show,
                         self.out,
                         AVConvDownloader)

###################################################################################

def main():
    run(PluzzService, __doc__)

if __name__ == "__main__":
    run(PluzzService, __doc__)
