'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Feb 2014
Copyright Marc Robinson 2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Script to constructed multiple 
fullerenes

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

import sys,os,random,numpy
from nanocap.core import globals,minimisation,triangulation,minimasearch
from nanocap.structures import fullerene
from nanocap.core import output
from nanocap.db import database

def main():
    NCarbon = 200 
    dual_lattice_minimiser = "Thomson"
    carbon_lattice_minimiser = "EDIP"
    seed = 12345
    
    N_max_structures = 2
    basin_climb = True
    calc_rings = True
    
    mintype="LBFGS"
    seed = 123456
    
    NFullerenes = 5
    NMaxStructures = 20
    BasinClimb = True
    CalcRings = True
    
    my_fullerene = fullerene.Fullerene()
    my_fullerene.construct_dual_lattice(N_carbon=NCarbon,seed=seed)
    my_fullerene.construct_carbon_lattice()
    my_fullerene.set_fix_pole(False)
    my_fullerene.set_nfixed_to_equator(0)
    
    Dminimiser = minimisation.DualLatticeMinimiser(FFID=dual_lattice_minimiser,
                                      structure = my_fullerene,
                                      min_type= "LBFGS",
                                      ftol = 1e-10,
                                      min_steps = 10)
   
    Cminimiser = minimisation.CarbonLatticeMinimiser(FFID=carbon_lattice_minimiser,
                                      structure = my_fullerene,
                                      min_type= "LBFGS",
                                      ftol = 1e-10,
                                      min_steps = 10)
    
    Searcher = minimasearch.MinimaSearch(Dminimiser,carbon_lattice_minimiser= Cminimiser,
                            basin_climb=basin_climb,calc_rings=calc_rings)
    
    Searcher.start_search(my_fullerene.dual_lattice,NFullerenes,NMaxStructures)
    
    Searcher.continue_search(my_fullerene.dual_lattice,NFullerenes,NMaxStructures)
    
    Searcher.structure_log.write_log(os.getcwd(),"myStructures.out")
    
    for i,structure in enumerate(Searcher.structure_log.structures):
        output.write_points("C{}_carbon_atoms_{}".format(structure.carbon_lattice.npoints,i),
                            structure.carbon_lattice,
                            "xyz")
        
        my_db = database.Database()
        my_db.init()
        my_db.add_structure(structure,add_dual_lattice=True,add_carbon_lattice=True)
    
if __name__=="__main__":
    main()
