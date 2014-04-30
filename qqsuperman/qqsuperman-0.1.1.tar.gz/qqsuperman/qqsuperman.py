#!/usr/bin/env python
# coding: utf-8

import requests
import itertools

class QQSuperman(object):

    api = "http://api.sz789.net:88/index.do"

    def __init__(self, username, password, soft_id=0):
        self.username = username
        self.password = password
        self.soft_id  = soft_id

    def remainder_point(self):
        response = requests.post(self.api, data={
            'm'       : 'getinfo',
            'username': self.username,
            'password': self.password
        })

        return response.text

    def decode_image(self, path=None, hex_content=None):
        if path:
            image_data = open(path).read().encode('hex')

        if hex_content:
            image_data = hex_content

        if not path and not hex_content:
            raise ValueError('Please provide path or hex content')

        response = requests.post(self.api, data={
            'm'       : 'send',
            'username': self.username,
            'password': self.password,
            'softid'  : self.soft_id,
            'imgdata' : image_data
        })

        return dict(itertools.izip(('code', 'worker'), response.text.split('|')))

    def report_error(self, worker):
        response = requests.post(self.api, data={
            'm'       : 'reporterr',
            'username': self.username,
            'worker'  : worker
        })

        return response.text
