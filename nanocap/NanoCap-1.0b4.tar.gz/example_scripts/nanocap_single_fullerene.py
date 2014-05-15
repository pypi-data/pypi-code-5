'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Feb 2014
Copyright Marc Robinson 2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Script to constructed a single fullerene

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import sys,os,random,numpy
sys.path.append(os.path.abspath(os.path.dirname(__file__)+"/../"))
from nanocap.core import globals,minimisation,triangulation
from nanocap.objects import fullerene
from nanocap.core import output

def main():
    NCarbon = 200 
    DualLatticeMinimiser = "Thomson"
    CarbonLatticeMinimiser = "EDIP"
    DualLattice_mintol=1e-10
    DualLattice_minsteps=100
    CarbonLattice_mintol=1e-10
    CarbonLattice_minsteps=100
    mintype="LBFGS"
    seed = 12345
    
    my_fullerene = fullerene.Fullerene()
    my_fullerene.construct_dual_lattice(N_carbon=NCarbon,seed=seed)
    my_fullerene.set_fix_pole(False)
    my_fullerene.set_nfixed_to_equator(0)
    
    
    Dminimiser = minimisation.dualLatticeMinimiser(FFID=DualLatticeMinimiser,object = my_fullerene)
    Dminimiser.minimise(my_fullerene.dual_lattice,
                        mintype=mintype,
                        ftol=DualLattice_mintol,
                        minsteps=DualLattice_minsteps)
    
    output.write_xyz("C{}_dual_lattice.xyz".format(NCarbon),my_fullerene.dual_lattice)
    
    my_fullerene.construct_carbon_lattice()
    
    Cminimiser = minimisation.carbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,object = my_fullerene)
    
    Cminimiser.minimise_scale(my_fullerene.carbon_lattice)
    Cminimiser.minimise(my_fullerene.carbon_lattice,
                        mintype=mintype,
                        ftol=CarbonLattice_mintol,
                        minsteps=CarbonLattice_minsteps)
    
    output.write_xyz("C{}_carbon_atoms.xyz".format(NCarbon),my_fullerene.carbon_lattice)
    output.write_xyz("C{}_carbon_atoms_constrained.xyz".format(NCarbon),my_fullerene.carbon_lattice,constrained=True)

    
    my_fullerene.calculate_rings()
    
    print my_fullerene.ring_info['ringCount']
    
    print my_fullerene
    
if __name__=="__main__":
    main()
