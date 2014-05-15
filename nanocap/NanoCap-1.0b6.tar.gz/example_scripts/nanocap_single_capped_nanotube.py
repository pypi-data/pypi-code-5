'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Apr 10, 2014
Copyright Marc Robinson  2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Script to constructed a single capped 
nanotube

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import sys,os,random,numpy
sys.path.append(os.path.abspath(os.path.dirname(__file__)+"/../"))
from nanocap.core import globals

globals.DEBUG=False
from nanocap.core import minimisation,triangulation
from nanocap.objects import cappednanotube
from nanocap.core import output


def main():
    n,m = 7,3
    l = 10.0 
    cap_estimate = True
         
    DualLatticeMinimiser = "Thomson"
    CarbonLatticeMinimiser = "EDIP"
    DualLattice_mintol=1e-10
    DualLattice_minsteps=100
    CarbonLattice_mintol=1e-10
    CarbonLattice_minsteps=100
    mintype="LBFGS"
    seed = 12345
    
    
    
    my_nanotube = cappednanotube.CappedNanotube()
    
    my_nanotube.setup_nanotube(n,m,l=l)
    
    if(cap_estimate):
        NCapDual = my_nanotube.get_cap_dual_lattice_estimate(n,m)

    my_nanotube.construct_dual_lattice(N_cap_dual=NCapDual,seed=seed)
    
    my_nanotube.set_Z_cutoff(N_cap_dual=NCapDual)

    output.write_xyz("n_{}_m_{}_l_{}_cap_{}_dual_lattice_initial.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.dual_lattice)

    
    Dminimiser = minimisation.DualLatticeMinimiser(FFID=DualLatticeMinimiser,structure = my_nanotube)
    Dminimiser.minimise(my_nanotube.dual_lattice,
                        min_type=mintype,
                        ftol=DualLattice_mintol,
                        min_steps=DualLattice_minsteps)
    
    my_nanotube.update_caps()
    output.write_xyz("n_{}_m_{}_l_{}_cap_{}_dual_lattice.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.dual_lattice)
    
    my_nanotube.construct_carbon_lattice()
    
    Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=CarbonLatticeMinimiser,structure = my_nanotube)
    
    Cminimiser.minimise_scale(my_nanotube.carbon_lattice)
    Cminimiser.minimise(my_nanotube.carbon_lattice,
                        min_type=mintype,
                        ftol=CarbonLattice_mintol,
                        min_steps=CarbonLattice_minsteps)
    
    output.write_xyz("n_{}_m_{}_l_{}_cap_{}_carbon_atoms.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.carbon_lattice)
    output.write_xyz("n_{}_m_{}_l_{}_cap_{}_carbon_atoms_constrained.xyz".format(n,m,l,my_nanotube.cap.dual_lattice.npoints),my_nanotube.carbon_lattice,constrained=True)


    print my_nanotube
    
    
if __name__=="__main__":
    main()
