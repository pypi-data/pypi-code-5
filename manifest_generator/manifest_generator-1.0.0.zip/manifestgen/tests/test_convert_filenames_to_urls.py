from manifestgen.app import convert_filenames_to_urls

import unittest

class TestConvertFilenamesToUrls(unittest.TestCase):
    
    def test_cannonical(self):
        result = convert_filenames_to_urls( [ '/usr/proj/index.html', '/usr/proj/js/util.js'], '/usr/proj', '/sample/static' )
        self.assertEqual( result, [ '/sample/static/index.html', '/sample/static/js/util.js' ])


    def test_no_url_prefix(self):
        result = convert_filenames_to_urls( [ '/usr/proj/index.html', '/usr/proj/js/util.js'], '/usr/proj')
        self.assertEqual( result, [ '/index.html', '/js/util.js' ])

    def test_no_docroot(self):
        result = convert_filenames_to_urls( [ '/usr/proj/index.html', '/usr/proj/js/util.js'],  url_prefix='/sample/static')
        self.assertEqual( result, [ '/sample/static/usr/proj/index.html', '/sample/static/usr/proj/js/util.js' ])

    def test_no_docroot_no_url_prefix(self):
        result = convert_filenames_to_urls( [ '/usr/proj/index.html', '/usr/proj/js/util.js'])
        self.assertEqual( result, [ '/usr/proj/index.html', '/usr/proj/js/util.js' ])
 

