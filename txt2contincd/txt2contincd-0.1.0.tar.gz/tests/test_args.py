#!/usr/bin/env nosetests -v
# coding=utf-8
from nose.tools import *
import numpy as np
from argparse import ArgumentTypeError
from mock import MagicMock as Mock

from txt2contincd.args import parse_using
from txt2contincd.args import parse_args


#-------------------------------------------------------------------------------
# parse_using
#-------------------------------------------------------------------------------
def test_parse_using_valid_format():
    eq_(parse_using('0:1'), (0, 1))
    eq_(parse_using('0:1:2'), (0, 1, 2))

@raises(ArgumentTypeError)
def test_parse_using_format1():
    parse_using('0:')

@raises(ArgumentTypeError)
def test_parse_using_format2():
    parse_using(':1')

@raises(ArgumentTypeError)
def test_parse_using_format3():
    parse_using('foo')


#-------------------------------------------------------------------------------
# parse_args
#-------------------------------------------------------------------------------
# reading options
def test_parse_args_parser_short():
    args = parse_args(['-p', 'foobar', 'piyo'])
    eq_(args.parser, 'foobar')
def test_parse_args_parser():
    args = parse_args(['--parser', 'foobar', 'piyo'])
    eq_(args.parser, 'foobar')
def test_parse_args_loader_short():
    args = parse_args(['-l', 'foobar', 'piyo'])
    eq_(args.loader, 'foobar')
def test_parse_args_loader():
    args = parse_args(['--loader', 'foobar', 'piyo'])
    eq_(args.loader, 'foobar')
def test_parse_args_using_short():
    args = parse_args(['-u', '0:1', 'piyo'])
    eq_(args.using, (0, 1))
def test_parse_args_using():
    args = parse_args(['--using', '0:1:2', 'piyo'])
    eq_(args.using, (0, 1, 2))
