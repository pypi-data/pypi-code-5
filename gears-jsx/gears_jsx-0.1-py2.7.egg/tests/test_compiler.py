#-*- coding: utf-8 -*-

import os
import unittest

from gears.environment import Environment
from gears.finders import FileSystemFinder

from gears_jsx import JSXCompiler


ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
JSX_DIR = os.path.join(ROOT_DIR, 'fixtures', 'jsx')
JS_DIR = os.path.join(ROOT_DIR, 'fixtures', 'js')
OUTPUT_DIR = os.path.join(ROOT_DIR, 'fixtures', 'output')


def fixture_load(name):
    f = open(os.path.join(JSX_DIR, "%s.jsx" % name), 'r')
    src_jsx = f.read()
    f.close()

    f = open(os.path.join(JS_DIR, "%s.js" % name), 'r')
    src_js = f.read()
    f.close()

    f = open(os.path.join(OUTPUT_DIR, "%s.js" % name), 'r')
    src_output = f.read()
    f.close()

    return src_jsx, src_js, src_output


class CompilerTest(unittest.TestCase):

    def setUp(self):
        self.compiler = JSXCompiler()

        self.env = Environment(root=OUTPUT_DIR, public_assets=(r'.*\.js',),
                               fingerprinting=False)
        self.env.finders.register(FileSystemFinder([JSX_DIR]))
        self.env.compilers.register('.jsx', self.compiler.as_handler())
        self.env.register_defaults()
        self.env.save()

    def test_transform(self):
        jsx, js, output = fixture_load('transform')
        self.assertEqual(js, output)
