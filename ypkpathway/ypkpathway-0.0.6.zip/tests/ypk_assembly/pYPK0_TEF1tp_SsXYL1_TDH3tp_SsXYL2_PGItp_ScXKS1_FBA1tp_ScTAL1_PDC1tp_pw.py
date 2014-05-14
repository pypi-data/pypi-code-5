#!/usr/bin/env python
# -*- coding: utf-8 -*- 

execfile("header.py")

def design():
    #---------------------------------------------------------------------------
    # This script should define a Dseqrecord named seq

    from pydna import pcr, parse, Genbank, Assembly
    from Bio.Restriction import EcoRV, ZraI
    
    (p577,
     p578,
     p512,
     p665) = parse(   '''   >577_crp585-557          
                            gttctgatcctcgagcatcttaagaattc
                                                                           
                            >578_crp42-70            
                            gttcttgtctcattgccacattcataagt
                            
                            >512_crp_EcoRV (29-mer)
                            ttcgccaattgattcaggtaaatccggat
                            
                            >665_crp_ZraI (29-mer) (new)
                            agcagagtctgtgcaatgcggccgctgac''', ds=False)

    from pYPK0 import pYPK0
    
    from pYPK0_TEF1tp_SsXYL1_TDH3tp import pYPK0_TEF1tp_SsXYL1_TDH3tp as cas1
    from pYPK0_TDH3tp_SsXYL2_PGItp import pYPK0_TDH3tp_SsXYL2_PGItp as cas2
    from pYPK0_PGItp_ScXKS1_FBA1tp import pYPK0_PGItp_ScXKS1_FBA1tp as cas3
    from pYPK0_FBA1tp_ScTAL1_PDC1tp import pYPK0_FBA1tp_ScTAL1_PDC1tp as cas4
    cas1  = pcr( p577, p778, cas1)
    cas2  = pcr( p775, p778, cas2)
    cas3  = pcr( p775, p778, cas3)
    cas4 = pcr( p775, p578, cas4)

    pYPK0_E_Z, stuffer = pYPK0.cut((EcoRV, ZraI))
    
    a = Assembly((pYPK0_E_Z, cas1,cas2,cas3,cas4))

    print a.analyze_overlaps(limit=61)

    print a.create_graph()

    print a.assemble_hr_circular()

    seq = a.circular_products[0]
    
    print seq.small_fig()
            
    seq = seq.synced("tcgcgcgtttcggtgatgacggtgaaaacctctg")     
    
    # This script should define a Dseqrecord named seq
    #---------------------------------------------------------------------------
    assert isinstance(seq, Dseqrecord)
    return seq
    
execfile("footer.py")
    


