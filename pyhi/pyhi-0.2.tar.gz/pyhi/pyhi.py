#!/usr/bin/env python

import requests
import json
import re
import urlparse
import logging

log = logging.getLogger('')

def maybe_pretty(obj, indent=4):
    """ Prettify to indented multiline string if obj is jsonable, if not - return original obj. """
    try:
        newobj = obj
        if isinstance(obj, str):
            newobj = json.loads(obj)
        prettified = json.dumps(newobj, sort_keys=True, indent=indent)
    except Exception as error:
        prettified = obj
    return prettified

class HiData(object):
    """ Client for a HI server. Based on REST API, enables opening and closing sessions, getting market data, buying and selling. """

    def __init__(self, restId, restPassword, instrument, resolution, automatonName, studies=[], initialTime=0, accountbalance=1000, baseurl='http://historicalinvestor.com'):
        self.restId = restId
        self.restPassword = restPassword
        self.instrument = instrument
        self.resolution = resolution
        self.automatonName = automatonName
        self.studies = studies
        self.initialTime = initialTime
        self.accountBalance = accountbalance
        self._baseurl = baseurl
        self._req = None
        self.make_session()

    def __tmpl_new_session(self):
        """ New session template """
        return {
            "sessionParams": {
                "accountBalance": 1000,
                "resolution": "",
                "automatonName": "",
                "instrument": "",
                "studies": [
                    {
                        "params": {
                            "parametr": "",
                            "periods": ""
                            },
                        "name": ""
                    }
                    ],
                "initialTime": 0
                },
            "restPassword": "",
            "restId": ""
        }

    def __update_nested_keys(self, d):
        """ Update specified nested dictionary with values for keys stored in self.__dict__ """
        for k in d:
            v = d[k]
            if isinstance(v, dict):
                self.__update_nested_keys(v)
            else:
                if k in self.__dict__ and not str(k).startswith('_'):
                    d[k] = self.__dict__[k]

    def _connect(self, path, data):
        """ Generic server connect method. """
        headers = {'content-type': 'application/json'}
        url = urlparse.urljoin(self._baseurl, path)
        log.debug('Base URL: %s', self._baseurl)
        log.info('Opening URL: %s', url)
        log.debug('Data: %s', maybe_pretty(data))
        if isinstance(data, dict):
            data = json.dumps(data)
        self._req = requests.post(url, data=data, headers=headers)
        self._req.raise_for_status()
        t = self._req.text
        return json.loads(t)

    def make_session(self):
        """ Internal function, creating session. """
        d = self.__tmpl_new_session()
        self.__update_nested_keys(d)
        dat = json.dumps(d)        
        res = self._connect('/rest/session/connect', dat)
        log.debug('Request result: %s', res)
        self._connect_result = res
        self._session = res['session']
        self._token = self._session['token']
        self._instrument = res['instrument']
        return self._session

    def get_data(self, start_time, candle_num, skip=0):
        """ Get market data. 
                start_time: time in milliseconds since 1970
                candle_num: number of candles to get_data
                skip: number of candles to skip after specified start_time
        """
        path = '/rest/data?token={0}'.format(self._token)
        d = {'from': start_time, 'amount': candle_num, 'skip': skip}
        res = self._connect(path, d)
        lastdat = res[-1]
        self._last_time = lastdat['t']
        return res

    def order(self, order_time, volume):
        """ Buy/sell.
                 order_time: bid or offer time in milliseconds since 1970.
                 volume: number of lots
        """
        path = '/rest/session/order?token={0}'.format(self._token)
        d = {'time': order_time, 'volume': volume}
        return self._connect(path, d)

    def finish(self):
        path = '/rest/session/end?token={0}&time={1}'.format(self._token, self._last_time)
        self._connect(path, '')

