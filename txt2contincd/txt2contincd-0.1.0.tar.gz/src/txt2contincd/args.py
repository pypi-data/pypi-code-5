# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import re
import argparse
import txt2contincd

USING_FORMAT_PATTERN = re.compile(r"^(\d+:)*\d+$")

def parse_using(value):
    m = USING_FORMAT_PATTERN.match(value)
    if m is None:
        raise argparse.ArgumentTypeError('Value has to be a colon (:) '
                                         'separated column indexes (e.g. '
                                         '"0:1" or "0:1:2").')
    indexes = value.split(":")
    return tuple(map(int, indexes))


def parse_args(args=None):
    usage = None
    description = None

    parser = argparse.ArgumentParser(prog='txt2contincd',
                                     usage=usage,
                                     description=description,
                                     version=txt2contincd.__version__)

    group1 = parser.add_argument_group('Reading options')
    group1.add_argument('-p', '--parser', default=None,
                        help=('A maidenhair parser name which will be used to '
                              'parse the raw text data.'))
    group1.add_argument('-l', '--loader', default=None,
                        help=('A maidenhair loader name which will be used to '
                              'load the raw text data.'))
    group1.add_argument('-u', '--using', default=None, type=parse_using,
                        help=('A colon (:) separated column indexes. '
                              'It is used for limiting the reading columns.'))
    group1.add_argument('-a', '--average', action='store_true', default=None,
                        help=('Calculate the average value of the specified '
                              'data.'))
    group1.add_argument('-s', '--no-strict', action='store_false', default=None,
                        dest='strict',
                        help=('Do not strict the wavelength range into 190-240 '
                              '.'))
    group1.add_argument('-o', '--output', default=None,
                        help=('A output filename. '
                              'The default is "contin-cd.in".'))
    # Experimental properties
    group2 = parser.add_argument_group('Experimental properties')
    group2.add_argument('-n', '--number', default=None, type=int,
                        help=('The number of residues (amino acids) in the '
                              'sample.'))
    group2.add_argument('-m', '--molecular-weight', default=None, type=float,
                        help=('A molecular weight of the sample '
                              'in kDa (=kg/mol). '))
    group2.add_argument('-c', '--concentration', default=None, type=float,
                        help=('A concentration of the sample in g/L. '
                              'See --molar-concentration as an alternative.'))
    group2.add_argument('--molar-concentration', default=None, type=float,
                        help=('A molar concentration of the sample in '
                              'mol/L. '
                              'It is used as an alternative option of '
                              '--concentration.'))
    group2.add_argument('-L', '--length', default=None, type=float,
                        help=('A light pathway length (cuvette length) '
                              'in centimeter'))
    # Required
    parser.add_argument('pathname',
                        help=('An unix grob style filename pattern for the '
                              'data files'))
    args = parser.parse_args(args)
    return args
