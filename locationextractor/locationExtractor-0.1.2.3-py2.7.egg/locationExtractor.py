# -*- coding: utf-8 -*-
import pycountry
from locations import Locations

def detect(haystack):
 	location = Locations.detect(haystack)
 	if location != None:
 		location["country"] = pycountry.countries.get(
 			alpha2=location["code"]).name
 		return location
