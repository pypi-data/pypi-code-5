#!/usr/bin/env python
# -*- coding: utf-8 -*- 

execfile("header.py")

def design():
    #---------------------------------------------------------------------------
    # This script should define a Dseqrecord named seq
    
    from pydna import pcr, parse, Genbank, Assembly
    
    p577,578,p468,p467,p567,p568  =  parse(''' >577_crp585-557          
                                                gttctgatcctcgagcatcttaagaattc
                                                
                                                >578_crp42-70            
                                                gttcttgtctcattgccacattcataagt

                                                >468_pCAPs_release_fw (25-mer) 79.66
                                                gtcgaggaacgccaggttgcccact

                                                >467_pCAPs_release_re (31-mer) 
                                                ATTTAAatcctgatgcgtttgtctgcacaga

                                                >567_pCAPsAjiIF (23-mer)
                                                GTcggctgcaggtcactagtgag

                                                >568_pCAPsAjiIR (22-mer)
                                                GTGCcatctgtgcagacaaacg''')
                                                
    from Bio.Restriction import ZraI, AjiI, EcoRV
    
    from pYPK0 import pYPK0
    
    from pYPKa_Z_FBA1tp import pYPKa_Z_FBA1tp as first
    from pYPKa_A_ScTAL1 import pYPKa_A_ScTAL1 as middle
    from pYPKa_E_PDC1tp import pYPKa_E_PDC1tp as last                                                                               

    first  = pcr( p577, p567, first)
    middle = pcr( p468, p467, middle)
    last   = pcr( p568, p578, last)
    
    pYPK0_E_Z, stuffer = pYPK0.cut((EcoRV, ZraI))
    
    a = Assembly([first, middle, last, pYPK0_E_Z])
    
    print a.analyze_overlaps(limit=31)
    
    print a.create_graph()
    
    print a.assemble_hr_circular()

    seq = a.circular_products[0]
    
    seq=seq.synced("tcgcgcgtttcggtgatgacggtgaaaacctctg")

    # This script should define a Dseqrecord named seq
    #---------------------------------------------------------------------------
    assert isinstance(seq, Dseqrecord)
    return seq

execfile("footer.py")
