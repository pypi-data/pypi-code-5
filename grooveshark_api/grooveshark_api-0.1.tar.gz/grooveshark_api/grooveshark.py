# coding: utf-8

import hmac
import json
import requests
from grooveshark_api.exception import InvalidArgumentValueException, \
    InvalidCredentialsException, RequestErrorException


GROOVESHARK_SSL_ENDPOINT = 'https://api.grooveshark.com/ws3.php'


class Grooveshark(object):

    def __init__(self, key, secret, sessionID=None,
                 user_login=None, user_pass=None):
        self.KEY = key
        self.SECRET = secret
        user = {}
        if sessionID:
            self.sessionID = sessionID
        elif user_login and user_pass:
            self.sessionID = self._get_new_session()
            result = self._establish_session(user_login, user_pass)
            user['name'] = "{0} {1}".format(result.get("FName", None),
                                            result.get("LName", None))
            user['email'] = result.get("Email", None)
            user['login'] = user_login

        self.user = user

    def _request(self, method, params={}, sessionID=False):
        header = {"wsKey": self.KEY}
        if sessionID is True:
            header.update({'sessionID': self.sessionID})

        payload = {"method": method,
                   "parameters": params,
                   "header": header}

        sig = hmac.new(self.SECRET, json.dumps(payload))
        sig = sig.hexdigest()

        url = "{0}?sig={1}".format(GROOVESHARK_SSL_ENDPOINT,
                                   sig)

        response = requests.post(url, data=json.dumps(payload))
        response = json.loads(response.content)

        result = response.get("result", None)
        if result is None:
            raise RequestErrorException(response)
        else:
            return response

    def _establish_session(self, user_login, user_pass):
        params = {
            'login': user_login,
            'password': user_pass
        }
        response = self._request(method="authenticate", params=params,
                                 sessionID=True)

        result = response.get("result")
        if not result.get("success", False):
            raise InvalidCredentialsException("Invalid Login" +
                                              " or Password.")
        else:
            return result

    def _get_new_session(self):
        response = self._request(method="startSession")
        result = response.get("result", None)
        return result.get("sessionID")

    def get_user_playlists(self, limit=None):
        params = {}
        try:
            if limit is not None:
                limit = int(limit)
                params.update({'limit': limit})
        except ValueError:
            raise InvalidArgumentValueException
        response = self._request(method="getUserPlaylists",
                                 params=params, sessionID=True)
        return response

    def get_playlist(self, playlist_id, limit=None):
        try:
            playlist_id = int(playlist_id)
            params = {'playlistID': playlist_id}

            if limit is not None:
                limit = int(limit)
                params.update({'limit': limit})
        except ValueError:
            raise InvalidArgumentValueException

        response = self._request(method="getPlaylist", params=params)
        return response

    def get_does_song_exist(self, song_id):
        params = {'songID': song_id}
        response = self._request(method='getDoesSongExist', params=params)
        return response.get('result', None)

    def get_songs_info(self, songs_id):
        params = {'songIDs': songs_id}
        response = self._request(method='getSongsInfo', params=params)
        return response.get('result', None)

    def get_stream_key_stream_server(self, song_id, ip):
        country = self._request(method="getCountry", params={'ip': ip})
        params = {'songID': song_id,
                  'country': country.get('result')}

        response = self._request(method='getStreamKeyStreamServer',
                                 params=params,
                                 sessionID=True)
        return response.get('result', None)
