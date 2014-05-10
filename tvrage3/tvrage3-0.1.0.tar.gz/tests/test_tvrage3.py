#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_tvrage3
----------------------------------

Tests for `tvrage3` module.
"""

import unittest
import urllib
import xmltodict
from tvrage3.api import Show
from tvrage3.search import search, search_id, quick_info

def get_test_objects_equality():
    response = urllib.request.urlopen('http://services.tvrage.com/feeds/ful' +
                                      'l_search.php?show=breadwinners')
    doc = xmltodict.parse(response.read())
    tv1 = Show(search_info=doc['Results']['show'][0])
    response = urllib.request.urlopen('http://services.tvrage.com/feeds/' +
                                      'showinfo.php?sid=8464')
    doc = xmltodict.parse(response.read())
    tv2 = Show(full_info=doc['Showinfo'])
    response = urllib.request.urlopen('http://services.tvrage.com/tools/qu' +
                                      'ickinfo.php?show=breadwinners&exact=1')
    tv3 = Show(quick_info=response.read().decode())
    return (tv1, tv2, tv3)


class TestTvrage3(unittest.TestCase):

    def setUp(self):
        pass

    def test_equality(self):
        '''Test to make sure the diffrent ways to retrive tvrage info returns
        the exact same results'''
        tv1, tv2, tv3 = get_test_objects_equality()
        self.assertEqual(tv1.show_id, tv2.show_id)
        self.assertEqual(tv2.show_id, tv3.show_id)

        self.assertEqual(tv1.name, tv2.name)
        self.assertEqual(tv2.name, tv3.name)

        self.assertEqual(tv1.link, tv2.link)
        self.assertEqual(tv2.link, tv3.link)

        self.assertEqual(tv1.started_year, tv2.started_year)
        self.assertEqual(tv2.started_year, tv3.started_year)

        self.assertEqual(tv1.ended_year, tv2.ended_year)
        self.assertEqual(tv2.ended_year, tv3.ended_year)

        self.assertEqual(tv1.status, tv2.status)
        self.assertEqual(tv2.status, tv3.status)

        self.assertEqual(tv1.classification, tv2.classification)
        self.assertEqual(tv2.classification, tv3.classification)

        self.assertEqual(tv1.genres, tv2.genres)
        self.assertEqual(tv2.genres, tv3.genres)

        self.assertEqual(tv1.runtime, tv2.runtime)
        self.assertEqual(tv2.runtime, tv3.runtime)

        self.assertEqual(tv1.country, tv2.country)
        self.assertEqual(tv2.country, tv3.country)

        self.assertEqual(tv1.seasons, tv2.seasons)
        self.assertEqual(tv2.seasons, tv3.seasons)

        self.assertEqual(tv1.network, tv2.network)
        self.assertEqual(tv2.network, tv2.network)

        self.assertEqual(tv1.air_time, tv2.air_time)
        self.assertEqual(tv2.air_time, tv3.air_time)

        self.assertEqual(tv1.air_day, tv2.air_day)
        self.assertEqual(tv2.air_day, tv3.air_day)

    def test_incomplete_info(self):
        """Test a show where tvrage cant supply all the info"""
        tv = Show(show_id='8464')
        self.assertEqual(tv.show_id, '8464')
        self.assertEqual(tv.name, 'Breadwinners')
        self.assertEqual(tv.link, 'http://www.tvrage.com/shows/id-8464')
        self.assertEqual(tv.started_year, 2007)
        self.assertEqual(tv.ended_year, None)
        self.assertEqual(tv.status, 'Pilot Rejected')
        self.assertEqual(tv.classification, 'Scripted')
        self.assertEqual(tv.genres, None)
        self.assertEqual(tv.runtime, 30)
        self.assertEqual(tv.country, 'US')
        self.assertEqual(tv.seasons, 1)

    def test_quick_search(self):
        result1 = quick_info('CSI crime')
        result2 = quick_info('CSI crime', exact=True)
        self.assertTrue(isinstance(result1, Show))
        self.assertEqual(result2, None)

    def test_search(self):
        result = search("Buffy")
        self.assertTrue(len(result) == 3)
        self.assertEqual(result[0].name, 'Buffy the Vampire Slayer')
        self.assertEqual(result[2].name, 'Buffy the Animated Series')

    def test_search_id(self):
        result = search_id('2930')
        self.assertEqual(result.name, 'Buffy the Vampire Slayer')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
