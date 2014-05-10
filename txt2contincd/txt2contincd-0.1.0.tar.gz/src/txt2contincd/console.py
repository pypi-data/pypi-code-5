#!/usr/bin/env python
# coding=utf-8
"""
"""
__author__ = 'Alisue <lambdalisue@hashnote.net>'
import os
import tolerance
import maidenhair
from maidenhair.utils.plugins import registry
from txt2contincd.args import parse_args
from txt2contincd.conf import parse_conf
from txt2contincd.main import translate_dataset
from txt2contincd.main import print_contincd_in

def ask(prompt, validation=None):
    validation = validation or (lambda x: x)
    validation = tolerance.tolerate(False)(validation)
    input_text = ""
    while not validation(input_text):
        input_text = raw_input(prompt)
    return validation(input_text)

def txt2contincd(args=None):
    # parse config file and arguments
    args = parse_args(args)
    conf = parse_conf('txt2contincd', args)

    if conf['experiment'].get('number') is None:
        print ("Please specify the number of residues (amino acids) in the "
               "sample.")
        conf['experiment']['number'] = ask("N: ", int)
    if conf['experiment'].get('molecular_weight') is None:
        print ("Please specify the molecular weight of the sample in kDa "
               "(= kg/mol)")
        conf['experiment']['molecular_weight'] = ask("m: ", float)
    if (conf['experiment'].get('concentration') is None and
        conf['experiment'].get('molar_concentration') is None):
        print ("Please specify the concentration of the sample in g/L")
        conf['experiment']['concentration'] = ask("c: ", float)
    if conf['experiment'].get('length') is None:
        print ("Please specify the length of the light pathway in centimeter")
        conf['experiment']['length'] = ask("l: ", float)
    
    # load dataset
    parser = registry.find(conf['default']['parser'])()
    loader = registry.find(conf['default']['loader'])()
    dataset = maidenhair.load(args.pathname,
                              using=conf['default']['using'],
                              unite=conf['default']['average'],
                              relative=False,
                              baseline=None,
                              parser=parser,
                              loader=loader,
                              with_filename=False)

    # translate dataset into mean resudie ellipticities
    dataset = translate_dataset(dataset,
                                conf['experiment']['number'],
                                conf['experiment']['molecular_weight'],
                                (conf['experiment']['concentration'] or
                                 conf['experiment']['molar_concentration']),
                                conf['experiment']['length'],
                                (conf['experiment']['molar_concentration'] is
                                    not None))

    # print
    with open(conf['default']['output'], 'wb') as f:
        print_contincd_in(dataset,
                          os.path.basename(args.pathname),
                          f,
                          conf['default']['strict'])


if __name__ == '__main__':
    txt2contincd()
