__authors__ = ""
__copyright__ = "(c) 2014, pymal"
__license__ = "BSD License"
__contact__ = "Name Of Current Guardian of this file <email@address>"

import hashlib
from xml.etree import ElementTree
from urllib import parse

import bs4
from requests.auth import HTTPBasicAuth

from pymal.global_functions import _connect, connect
from pymal.decorators import load, SingletonFactory
from pymal.AccountAnimes import AccountAnimes
from pymal.AccountMangas import AccountMangas

__all__ = ['Account']


class Account(object, metaclass=SingletonFactory):
    """
    """
    __all__ = ['animes', 'mangas', 'reload', 'search', 'auth_connect',
               'connect', 'is_user_by_name', 'is_user_by_id', 'is_auth']
    
    __AUTH_CHECKER_URL =\
        r'http://myanimelist.net/api/account/verify_credentials.xml'
    __SEARCH_URL = 'http://myanimelist.net/api/{0:s}/search.xml'
    __ANIME_SEARCH_URL = __SEARCH_URL.format('anime')
    __MANGA_SEARCH_URL = __SEARCH_URL.format('manga')

    def __init__(self, username: str, password: str or None=None):
        """
        """
        self._username = username
        self._password = password
        self.connect = connect
        self.__user_id = 0
        self.__auth_object = None
        self.__cookies = dict()

        self._is_loaded = False
        self.__animes = None
        self.__mangas = None

        if password is not None:
            self.change_password(password)

    @property
    @load
    def animes(self):
        return self.__animes

    @property
    @load
    def mangas(self):
        return self.__mangas

    def reload(self):
        self.__animes = AccountAnimes(self._username, self)
        self.__mangas = AccountMangas(self._username, self)
        self._is_loaded = True

    def search(self, search_line: str, is_anime: bool=True) -> set:
        """
        """
        params = {'q': search_line}
        if is_anime:
            base_url = self.__ANIME_SEARCH_URL
            from pymal.Anime import Anime
            searched_object = Anime
            account_object_list = self.animes
        else:
            base_url = self.__MANGA_SEARCH_URL
            from pymal.Anime import Manga
            searched_object = Manga
            account_object_list = self.mangas

        url_parts = list(parse.urlparse(base_url))
        query = dict(parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = parse.urlencode(query)
        search_url = parse.urlunparse(url_parts)

        data = self.auth_connect(search_url)
        entries = bs4.BeautifulSoup(data).body.anime.findAll(
            name='entry', recursive=False)

        def get_object(entry):
            object_id = int(entry.id.text)
            if object_id in account_object_list:
                return list(filter(
                    lambda x: x == object_id,
                    account_object_list
                ))[0]
            return searched_object(object_id)
        return set(map(get_object, entries))

    def change_password(self, password: str) -> bool:
        """
        Checking if the new password is valid
        """
        self.__auth_object = HTTPBasicAuth(self._username, password)
        data = self.auth_connect(self.__AUTH_CHECKER_URL)
        if data == 'Invalid credentials':
            self.__auth_object = None
            self._password = None
            return False
        xml_user = ElementTree.fromstring(data)

        assert 'user' == xml_user.tag, 'user == {0:s}'.format(xml_user.tag)
        l = list(xml_user)
        xml_username = l[1]
        assert 'username' == xml_username.tag,\
            'username == {0:s}'.format(xml_username.tag)
        assert self.is_user_by_name(xml_username.text.strip()),\
            'username = {0:s}'.format(xml_username.text.strip())

        xml_id = l[0]
        assert 'id' == xml_id.tag, 'id == {0:s}'.format(xml_id.tag)
        self.__user_id = int(xml_id.text.strip())

        self._password = password

        return True

    def auth_connect(self, url: str, data: str or None=None,
                     headers: dict or None=None) -> str:
        """
        """
        assert self.is_auth, "Not auth yet!"
        return _connect(url, data=data, headers=headers,
                        auth=self.__auth_object).text.strip()

    def is_user_by_name(self, username: str) -> bool:
        """
        """
        return username == self._username

    def is_user_by_id(self, user_id: int) -> bool:
        """
        """
        return user_id == self.__user_id

    @property
    def __cookies_string(self):
        return ";".join(["=".join(item)for item in self.__cookies.items()])

    @property
    def is_auth(self) -> bool:
        """
        """
        return self.__auth_object is not None

    def __repr__(self):
        return "<Account username: {0:s}>".format(self._username)

    def __hash__(self):
        hash_md5 = hashlib.md5()
        hash_md5.update(self._username.encode())
        return int(hash_md5.hexdigest(), 16)
