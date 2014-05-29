__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import hashlib
from urllib import request
import os

from bs4.element import NavigableString

from pymal.decorators import load, SingletonFactory
from pymal.consts import HOST_NAME, DEBUG, XMLS_DIRECTORY, MALAPI_NONE_TIME
from pymal.global_functions import connect, make_list, get_next_index,\
    check_side_content_div, get_content_wrapper_div, make_time, make_counter

__all__ = ['Manga']


class Manga(object, metaclass=SingletonFactory):
    """
    """
    __all__ = ['id', 'title', 'image_url', 'english', 'synonyms', 'japanese',
               'type', 'status', 'start_time', 'end_time', 'creators',
               'genres', 'score', 'rank', 'popularity', 'synopsis',
               'adaptations', 'characters', 'sequals', 'prequel', 'spin_offs',
               'alternative_versions', 'side_stories', 'summaries', 'others',
               'parent_stories', 'alternative_settings', 'volumes', 'chapters',
               'reload', 'add']
    
    __GLOBAL_MAL_URL = request.urljoin(HOST_NAME, "manga/{0:d}")
    __MY_MAL_XML_TEMPLATE_PATH = os.path.join(
        os.path.dirname(__file__), XMLS_DIRECTORY,
        'myanimelist_official_api_manga.xml')
    __MY_MAL_ADD_URL = request.urljoin(
        HOST_NAME, 'api/mangalist/add/{0:d}.xml')

    def __init__(self, mal_id: int, mal_xml=None):
        """
        """
        self._id = mal_id
        self._is_loaded = False

        self._mal_url = self.__GLOBAL_MAL_URL.format(self._id)

        # Getting staff from html
        # staff from side content
        self._title = None
        self._image_url = None
        self._english = ''
        self._synonyms = None
        self._japanese = ''
        self._type = None
        self._status = None
        self._start_time = None
        self._end_time = None
        self._creators = dict()
        self._genres = dict()
        self._score = 0.0
        self._rank = 0
        self._popularity = 0

        self._chapters = None
        self._volumes = None

        # staff from main content
        # staff from row 1
        self._synopsis = ''

        # staff from row 2
        self._adaptations = list()
        self._characters = list()
        self._sequals = list()
        self._prequel = list()
        self._spin_offs = list()
        self._alternative_versions = list()
        self._side_stories = list()
        self._summaries = list()
        self._others = list()
        self._parent_stories = list()
        self._alternative_settings = list()

        self.related_str_to_list_dict = {
            'Adaptation:': self._adaptations,
            'Character:': self._characters,
            'Sequel:': self._sequals,
            'Prequel:': self._prequel,
            'Spin-off:': self._spin_offs,
            'Alternative version:': self._alternative_versions,
            'Side story:': self._side_stories,
            'Summary:': self._summaries,
            'Other:': self._others,
            'Parent story:': self._parent_stories,
            'Alternative setting:': self._alternative_settings,
        }

        if mal_xml is not None:
            self._title = mal_xml.find('series_title').text.strip()
            self._synonyms = mal_xml.find('series_synonyms').text
            if self._synonyms is not None:
                self._synonyms = self._synonyms.strip()
            # TODO: make this number to a string (or the string to a number?)
            self._type = mal_xml.find('series_type').text.strip()
            self_status = mal_xml.find('series_status').text.strip()
            if self_status.isdigit():
                self._status = int(self_status)
            else:
                self._status = self_status
                print('self._status=', self._status)
            self._start_time = make_time(mal_xml.find('series_start').text.strip())
            self._end_time = make_time(mal_xml.find('series_end').text.strip())
            self._image_url = mal_xml.find('series_image').text.strip()

            self._chapters = int(mal_xml.find('series_chapters').text.strip())
            self._volumes = int(mal_xml.find('series_volumes').text.strip())

    @property
    def id(self):
        return self._id

    @property
    def title(self):
        if self._title is None:
            self.reload()
        return self._title

    @property
    def image_url(self):
        if self._image_url is None:
            self.reload()
        return self._image_url

    @property
    @load
    def english(self):
        return self._english

    @property
    def synonyms(self):
        if self._synonyms is None:
            self.reload()
        return self._synonyms

    @property
    @load
    def japanese(self):
        return self._japanese

    @property
    def type(self):
        if self._type is None:
            self.reload()
        return self._type

    @property
    def status(self):
        if self._status is None:
            self.reload()
        return self._status

    @property
    def start_time(self):
        if self._start_time is None:
            self.reload()
        return self._start_time

    @property
    def end_time(self):
        if self._end_time is None:
            self.reload()
        return self._end_time

    @property
    @load
    def creators(self):
        return self._creators

    @property
    @load
    def genres(self):
        return self._genres

    @property
    @load
    def score(self):
        return self._score

    @property
    @load
    def rank(self):
        return self._rank

    @property
    @load
    def popularity(self):
        return self._popularity

    @property
    @load
    def synopsis(self):
        return self._synopsis

    # staff from main content
    @property
    @load
    def adaptations(self):
        return self._adaptations

    @property
    @load
    def characters(self):
        return self._characters

    @property
    @load
    def sequals(self):
        return self._sequals

    @property
    @load
    def prequel(self):
        return self._prequel

    @property
    @load
    def spin_offs(self):
        return self._spin_offs

    @property
    @load
    def alternative_versions(self):
        return self._alternative_versions

    @property
    @load
    def side_stories(self):
        return self._side_stories

    @property
    @load
    def summaries(self):
        return self._summaries

    @property
    @load
    def others(self):
        return self._others

    @property
    @load
    def parent_stories(self):
        return self._parent_stories

    @property
    @load
    def alternative_settings(self):
        return self._alternative_settings

    @property
    def volumes(self):
        if self._volumes is None:
            self.reload()
        return self._volumes

    @property
    def chapters(self):
        if self._chapters is None:
            self.reload()
        return self._chapters

    def reload(self):
        # Getting content wrapper <div>
        content_wrapper_div = get_content_wrapper_div(self._mal_url, connect)

        # Getting title <div>
        self._title = content_wrapper_div.h1.contents[1].strip()

        # Getting content <div>
        content_div = content_wrapper_div.find(
            name="div", attrs={"id": "content"}, recursive=False)
        if DEBUG:
            assert content_div is not None

        content_table = content_div.table

        contents = content_table.tbody.tr.findAll(name="td", recursive=False)

        # Data from side content
        side_content = contents[0]
        side_contents_divs = side_content.findAll(name="div", recursive=False)

        # Getting manga image url <img>
        img_div = side_contents_divs[0]
        img_link = img_div.find(name="a")
        assert img_link is not None
        self._image_url = img_link.img['src']

        side_contents_divs_index = 3

        # english <div>
        english_div = side_contents_divs[side_contents_divs_index]
        if check_side_content_div('English', english_div):
            english_span, self._english = english_div.contents
            self._english = self._english.strip()
            side_contents_divs_index += 1
        else:
            self._english = ''

        # synonyms <div>
        synonyms_div = side_contents_divs[side_contents_divs_index]
        if check_side_content_div('Synonyms', synonyms_div):
            synonyms_span, self._synonyms = synonyms_div.contents
            self._synonyms = self._synonyms.strip()
            side_contents_divs_index += 1
        else:
            self._synonyms = ''

        # japanese <div>
        japanese_div = side_contents_divs[side_contents_divs_index]
        if check_side_content_div('Japanese', japanese_div):
            japanese_span, self._japanese = japanese_div.contents
            self._japanese = self._japanese.strip()
            side_contents_divs_index += 1
        else:
            self._japanese = ''

        # type <div>
        type_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Type', type_div)
        type_span, self._type = type_div.contents
        self._type = self._type.strip()
        side_contents_divs_index += 1

        # volumes <div>
        volumes_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Volumes', volumes_div)
        volumes_span, self_volumes = volumes_div.contents
        self._volumes = make_counter(self_volumes.strip())
        side_contents_divs_index += 1

        # chapters <div>
        chapters_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Chapters', chapters_div)
        chapters_span, self_chapters = chapters_div.contents
        self._chapters = make_counter(self_chapters .strip())
        side_contents_divs_index += 1

        # status <div>
        status_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Status', status_div)
        status_span, self._status = status_div.contents
        self._status = self._status.strip()
        side_contents_divs_index += 1

        # published <div>
        published_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Published', published_div)
        published_span, published = published_div.contents
        start_time, end_time = published.split('to')
        start_time, end_time = start_time.strip(), end_time.strip()
        self._start_time = make_time(start_time)
        self._end_time = make_time(end_time)
        side_contents_divs_index += 1

        # genres <div>
        genres_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Genres', genres_div)
        for genre_link in genres_div.findAll(name='a'):
            self._genres[genre_link.text.strip()] = genre_link['href']
        side_contents_divs_index += 1

        # authors <div>
        authors_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Authors', authors_div)
        for authors_link in authors_div.findAll(name='a'):
            self._creators[authors_link.text.strip()] = authors_link['href']
        side_contents_divs_index += 1

        side_contents_divs_index += 1

        # score <div>
        score_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Score', score_div)
        score_span, self_score = score_div.contents[:2]
        self._score = float(self_score.strip())
        side_contents_divs_index += 1

        # rank <div>
        rank_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Ranked', rank_div)
        rank_span, self_rank = rank_div.contents[:2]
        self_rank = self_rank.strip()
        assert self_rank.startswith("#")
        self._rank = int(self_rank[1:])
        side_contents_divs_index += 1

        # popularity <div>
        popularity_div = side_contents_divs[side_contents_divs_index]
        assert check_side_content_div('Popularity', popularity_div)
        popularity_span, self_popularity = popularity_div.contents[:2]
        self_popularity = self_popularity.strip()
        assert self_popularity.startswith("#")
        self._popularity = int(self_popularity[1:])

        # Data from main content
        main_content = contents[1]
        main_content_inner_divs = main_content.findAll(
            name='div', recursive=False)
        if DEBUG:
            assert 2 == len(main_content_inner_divs), \
                "Got len(main_content_inner_divs) == {0:d}".format(
                    len(main_content_inner_divs))
        main_content_datas = main_content_inner_divs[
            1].table.tbody.findAll(name="tr", recursive=False)

        synopsis_cell = main_content_datas[0]
        main_content_other_data = main_content_datas[1]

        # Getting synopsis
        synopsis_cell = synopsis_cell.td
        synopsis_cell_contents = synopsis_cell.contents
        if DEBUG:
            assert 'Synopsis' == synopsis_cell.h2.text.strip(
            ), synopsis_cell.h2.text.strip()
        self._synopsis = os.linesep.join([
            synopsis_cell_content.strip()
            for synopsis_cell_content in synopsis_cell_contents[1:-1]
            if isinstance(synopsis_cell_content, NavigableString)
        ])

        # Getting other data
        main_content_other_data = main_content_other_data.td
        other_data_kids = [i for i in main_content_other_data.children]

        # Getting all the data under 'Related Manga'
        index = 0
        index = get_next_index(index, other_data_kids)
        if 'h2' == other_data_kids[index].name and\
           'Related Manga' == other_data_kids[index].text.strip():
            index += 1
            while other_data_kids[index + 1].name != 'br':
                index = make_list(
                    self.related_str_to_list_dict[
                        other_data_kids[index].strip()],
                    index, other_data_kids)
        else:
            index -= 2
        next_index = get_next_index(index, other_data_kids)

        if DEBUG:
            assert next_index - \
                index == 2, "{0:d} - {1:d}".format(next_index, index)
            index = next_index + 1

            # Getting all the data under 'Characters & Voice Actors'
            assert 'h2' == other_data_kids[index].name, 'h2 == {0:s}'.format(
                other_data_kids[index].name)
            assert 'Characters' == other_data_kids[index].contents[-1],\
                other_data_kids[index].contents[-1]

        self._is_loaded = True

    @property
    def MY_MAL_XML_TEMPLATE(self):
        with open(self.__MY_MAL_XML_TEMPLATE_PATH) as f:
            data = f.read()
        return data

    def add(self, account):
        """
        """
        data = self.MY_MAL_XML_TEMPLATE.format(0, 0, 6, 0, 0, 0, 0,
                                               MALAPI_NONE_TIME,
                                               MALAPI_NONE_TIME, 0, False,
                                               False, '', '', '', 0)
        self.ret_data = account.auth_connect(
            self.__MY_MAL_ADD_URL.format(self.id), data=data)
        print(self.ret_data)
        assert self.ret_data.isdigit()

    def __eq__(self, other):
        if isinstance(other, Manga):
            return self.id == other.id
        elif isinstance(other, int):
            return self.id == other
        elif isinstance(other, str) and other.isdigit():
            return self.id == int(other)
        elif hasattr(other, 'id'):
            return self.id == other.id
        return False

    def __hash__(self):
        hash_md5 = hashlib.md5()
        hash_md5.update(str(self.id).encode())
        hash_md5.update(b'Manga')
        return int(hash_md5.hexdigest(), 16)

    def __repr__(self):
        title = '' if self._title is None else ' ' + self._title
        return "<{0:s}{1:s} id={2:d}>".format(self.__class__.__name__, title,
                                              self._id)
