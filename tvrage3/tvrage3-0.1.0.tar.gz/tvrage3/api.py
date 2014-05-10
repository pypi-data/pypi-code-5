import urllib.request
import urllib.parse
import xmltodict
import re


class Show():
    """Information about a tvshow. Should be initialized by the TVRage search
    object. If the requests information about a show is unavailable then it
    will return None."""
    def __init__(self, show_id=None, quick_info=None,
                 full_info=None, search_info=None):
        self.quick_info = self.parse_quick_info(quick_info)
        self.full_info = full_info
        self.search_info = search_info
        if show_id:
            self.get_full_info(show_id)
        if not (show_id or quick_info or full_info or search_info):
            raise ValueError('Atleast one arg needs a value')

    # Internal: Converts a quickinfo response from tvrage into an dict
    def parse_quick_info(self, info):
        if not info:
            return None
        quick_info = {}
        quick_info['showid'] = re.search('Show ID@(.+)\n', info).group(1)
        quick_info['name'] = re.search('Show Name@(.+)\n', info).group(1)
        quick_info['link'] = re.search('Show URL@(.+)\n', info).group(1)
        started = re.search('Started@(.+)\n', info)
        if started:
            quick_info['started'] = started.group(1)
        else:
            quick_info['started'] = None
        ended = re.search('Ended@(.+)\n', info)
        if ended:
            quick_info['ended'] = ended.group(1)
        else:
            quick_info['ended'] = None
        status = re.search('Status@(.+)\n', info)
        if status:
            quick_info['status'] = status.group(1)
        else:
            quick_info['status'] = None
        classification = re.search('Classification@(.+)\n', info)
        if classification:
            quick_info['classification'] = classification.group(1)
        else:
            quick_info['classification'] = None

        genres = quick_info['genres'] = re.search('Genres@(.+)\n', info)
        if genres:
            quick_info['genres'] = genres.group(1).split(' | ')
        else:
            quick_info['genres'] = None
        runtime = re.search('Runtime@(.+)\n', info)
        if runtime:
            quick_info['runtime'] = runtime.group(1)
        else:
            quick_info['runtime'] = None
        return quick_info

    # Internal: Get full show info by id. If Show is initialized with
    # quick_info then some info will be missing, if missing info is required
    # then this function will be called to fill it.
    def get_full_info(self, show_id):
        response = urllib.request.urlopen('http://services.tvrage.com/feeds/' +
                                          'showinfo.php?sid=' + show_id)
        self.full_info = xmltodict.parse(response.read())['Showinfo']

    # Internal: Due to tvrage bug where for some reason the first genre is
    # empty which results in empty or a None entry into the genres list.
    # Also if there is only one genre the parser will return a string instead
    # of a list, this fixed that also.
    def fix_genres(self, list):
        if isinstance(list, str):
            return [list]
        return [x for x in list if x]

    @property
    def show_id(self):
        """Show id as a string"""
        if self.search_info:
            return self.search_info['showid']
        elif self.full_info:
            return self.full_info['showid']
        elif self.quick_info:
            return self.quick_info['showid']

    @property
    def name(self):
        """The name of the show"""
        if self.full_info:
            return self.full_info['showname']
        elif self.search_info:
            return self.search_info['name']
        elif self.quick_info:
            return self.quick_info['name']

    @property
    def link(self):
        """The link to the tvrage page with more info about the show"""
        if self.full_info:
            if self.full_info['showlink'][7:10] == 'www':
                return self.full_info['showlink']
            else:
                return self.full_info['showlink'].replace('http://',
                                                          'http://www.')
        elif self.search_info:
            return self.search_info['link']
        elif self.quick_info:
            return self.quick_info['link']

    @property
    def seasons(self):
        """Number of seasons the show has ran"""
        try:
            if self.full_info:
                return int(self.full_info['seasons'])
            elif self.search_info:
                return int(self.search_info['seasons'])
            elif self.quick_info:
                self.get_full_info(self.quick_info['showid'])
                return self.seasons
        except:
            return None

    @property
    def started_year(self):
        """The year the show started"""
        try:
            if self.full_info:
                return int(self.full_info['started'][-4:])
            elif self.search_info:
                return int(self.search_info['started'][-4:])
            elif self.quick_info:
                return int(self.quick_info['started'][-4:])
        except:
            return None

    @property
    def ended_year(self):
        """The year the show ended"""
        try:
            if self.full_info:
                return int(self.full_info['ended'][-4:])
            elif self.search_info:
                return int(self.search_info['ended'][-4:])
            elif self.quick_info:
                return int(self.quick_info['ended'][-4:])
        except:
            return None

    @property
    def country(self):
        """Country the show was produced for"""
        try:
            if self.full_info:
                return self.full_info['origin_country']
            elif self.search_info:
                return self.search_info['country']
            elif self.quick_info:
                self.get_full_info(self.quick_info['showid'])
                return self.country
        except:
            return None

    @property
    def status(self):
        """Current status of the show"""
        try:
            if self.full_info:
                return self.full_info['status']
            elif self.search_info:
                return self.search_info['status']
            elif self.quick_info:
                return self.quick_info['status']
        except:
            return None

    @property
    def classification(self):
        """The classification of the show"""
        try:
            if self.full_info:
                return self.full_info['classification']
            elif self.search_info:
                return self.search_info['classification']
            elif self.quick_info:
                return self.quick_info['classification']
        except:
            return None

    @property
    def genres(self):
        """The genres of the show"""
        try:
            if self.full_info:
                return self.fix_genres(self.full_info['genres']['genre'])
            elif self.search_info:
                return self.fix_genres(self.search_info['genres']['genre'])
            elif self.quick_info:
                return self.fix_genres(self.quick_info['genres'])
        except:
            return None

    @property
    def runtime(self):
        """How many minutes an episode of the show is"""
        try:
            if self.full_info:
                return int(self.full_info['runtime'])
            elif self.search_info:
                return int(self.search_info['runtime'])
            elif self.quick_info:
                return int(self.quick_info['runtime'])
        except:
            return None

    @property
    def network(self):
        """What country/network the show is running on"""
        try:
            if self.full_info:
                return self.full_info['network']
            elif self.search_info:
                return self.search_info['network']
            elif self.quick_info:
                self.get_full_info(self.quick_info['showid'])
                return self.network
        except:
            return None

    @property
    def air_time(self):
        """What time new episodes are televised in the country of origin"""
        try:
            if self.full_info:
                return self.full_info['airtime']
            elif self.search_info:
                return self.search_info['airtime']
            elif self.quick_info:
                self.get_full_info(self.quick_info['showid'])
                return self.air_time
        except:
            return None

    @property
    def air_day(self):
        """What day new episodes are televised in the country of orgin"""
        try:
            if self.full_info:
                return self.full_info['airday']
            elif self.search_info:
                return self.search_info['airday']
            elif self.quick_info:
                self.get_full_info(self.quick_info['showid'])
                return self.air_day
        except:
            return None
