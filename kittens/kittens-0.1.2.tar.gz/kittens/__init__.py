# The MIT License (MIT)

# Copyright (c) 2014 Samuel Lucidi

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
kitten_cannon.py

A means of sending friendly images of kittens
to a target.

Author: Sam Lucidi <sam@samlucidi.com>

"""

import os
import sys
import json
import random
import requests
try:
	import configparser
except:
	import ConfigParser as configparser

config = configparser.ConfigParser()
config_files = config.read([os.path.expanduser('~/.kitten.conf'), '/etc/kitten.conf'])

mogreet_url = "https://api.mogreet.com/moms/transaction.send"
client_id = config.get("mogreet", "client_id")
token = config.get("mogreet", "token")
campaign_id = config.get("mogreet", "campaign_id")
image_list = json.loads(config.get("kittens", "image_urls"))
fmt = "json"

def _select_image():
	"""
	Internal API for choosing an image to send.

	"""

	return random.choice(image_list)

def fire_kitten(phone_number, message, image_url):
	"""
	Send an MMS to target phone number via the Mogreet
	MMS api.

	:param phone_number: an international phone number
	:type phone_number: str

	:param message: a message to send along with the image
	:type message: str

	:param image_url: the url of an image to send to the target
					  phone number. Must be in a format that
					  Mogreet supports. (Most common formats
					  are safe, see their API docs for details.)
	:type image_url: str

	:returns: JSON response from the Mogreet API
	:rtype: dict

	"""

	params = {
		"client_id": client_id,
		"token": token,
		"campaign_id": campaign_id,
		"content_url": image_url,
		"format": fmt,
		"to": phone_number,
		"message": "The warhead has been armed."
	}
	return requests.get(mogreet_url, params=params).json()