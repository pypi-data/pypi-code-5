from manifestgen.args import parse_args

import unittest

class ParseArgsTests(unittest.TestCase):
    
    def test_cannonical(self):
        command_line =  "-c *.py -c *.img -c *.png -nc temp.py -n counter.html form.html -f / fallback.html -f /form fallbackform.html"
        args = parse_args(command_line.split())
        #self.assertEqual(args, Namespace(cache=[['*.py'], ['*.img'], ['*.png']], fallback=[['/', 'fallback.html '], ['/form', 'fallbackform.html']], network=[['counter.html', 'form.html']], no cache=[['temp.py']]))

        self.assertEqual( args.cache, [['*.py'], ['*.img'], ['*.png']])
        self.assertEqual( args.nocache, [['temp.py']])
        self.assertEqual( args.fallback, [['/', 'fallback.html'], ['/form', 'fallbackform.html']])


    def test_default_doc_root_is_none(self):
        command_line =  ""
        args = parse_args(command_line.split())
        self.assertEqual(args.doc_root, None)


    def test_doc_root_parsing(self):
        command_line = "-d C:/User/fuzzy -c *.png"
        args = parse_args(command_line.split())
        self.assertEqual(args.doc_root[0], "C:/User/fuzzy")


    def test_default_url_prefix_is_none(self):
        command_line =  ""
        args = parse_args(command_line.split())
        self.assertEqual(args.url_prefix, None) 

    def test_url_prefix_parsing(self):
        command_line = "-d C:/User/fuzzy -c *.png -u /prog/static/m"
        args = parse_args(command_line.split())
        self.assertEqual(args.url_prefix[0], "/prog/static/m")
 
