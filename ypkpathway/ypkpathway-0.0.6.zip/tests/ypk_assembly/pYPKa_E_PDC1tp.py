#!/usr/bin/env python
# -*- coding: utf-8 -*- 

execfile("header.py")

def design():
    #---------------------------------------------------------------------------
    # This script should define a Dseqrecord named seq
    
    from pYPKa import pYPKa
    from pydna import read
    from pydna import Dseqrecord
    from pydna import pcr
    from pydna import parse

    from Bio.Restriction import EcoRV
    
    enz = EcoRV
    
    ins = read("PDC1.txt")
    
    fp = read('''
>pfw955
ttaaatAGGGTAGCCTCCCCAT
''', ds=False)
    
    rp = read('''
>prv955
taattaaTTTGATTGATTTGACTGT
''', ds=False)
    
    pYPKa_cut = pYPKa.cut(enz).pop()
    
    ins = pcr( fp, rp, ins)
    
    pYPKa_enz_tp = (pYPKa_cut + ins).looped()
    
    pYPKa_enz_tp = pYPKa_enz_tp.synced("tcgcgcgtttcggtgatgacggtgaaaacctctg")
    
    seq = pYPKa_enz_tp

    # This script should define a Dseqrecord named seq
    #---------------------------------------------------------------------------
    assert isinstance(seq, Dseqrecord)
    return seq
    
execfile("footer.py")
