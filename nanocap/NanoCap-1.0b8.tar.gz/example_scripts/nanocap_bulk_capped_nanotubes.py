'''
-=-=-=-=-=-=-= NanoCap -=-=-=-=-=-=-=
Created: Feb 2014
Copyright Marc Robinson 2014
-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=

Script to constructed multiple 
capped nanotubes

-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=
'''

''''
input
-----

n,m = nanotube chirality
l   = nanotube length
cap_estimate = if True the number of cap atoms is
      determined by the surface density of the tube
      else set 'NCapDual' manually
       
output
------

will output a log file of the structures found to myStructures.out

the xyz positions for each structure are saved as CN_carbon_atoms_i.xyz
where N is the number of carbon atoms and i is the structure ID.    

'''
    
import numpy,os,sys
from nanocap.core.minimisation import DualLatticeMinimiser
from nanocap.core.minimisation import CarbonLatticeMinimiser
from nanocap.core.minimasearch import MinimaSearch
from nanocap.structures .cappednanotube import CappedNanotube
from nanocap.core import output
from nanocap.db import database

def my_capped_nanotube_search():
    n,m = 10,10
    l = 20.0 
    cap_estimate = True
    
    dual_lattice_minimiser = "Thomson"
    carbon_lattice_minimiser = "EDIP"
    seed = 12345
    
    N_nanotubes = 1
    N_max_structures = 2
    basin_climb = True
    calc_rings = True
    
    my_nanotube = CappedNanotube()
    my_nanotube.setup_nanotube(n,m,l=l)
    
    if(cap_estimate):
        N_cap_dual = my_nanotube.get_cap_dual_lattice_estimate(n,m)

    my_nanotube.construct_dual_lattice(N_cap_dual=N_cap_dual,seed=seed)
    my_nanotube.set_Z_cutoff(N_cap_dual=N_cap_dual)
    
    Dminimiser = DualLatticeMinimiser(FFID=dual_lattice_minimiser,
                                      structure = my_nanotube,
                                      min_type= "LBFGS",
                                      ftol = 1e-10,
                                      min_steps = 10)
   
    Cminimiser = CarbonLatticeMinimiser(FFID=carbon_lattice_minimiser,
                                      structure = my_nanotube,
                                      min_type= "LBFGS",
                                      ftol = 1e-10,
                                      min_steps = 10)
    
    Searcher = MinimaSearch(Dminimiser,carbon_lattice_minimiser= Cminimiser,
                            basin_climb=basin_climb,calc_rings=calc_rings)
    
    Searcher.start_search(my_nanotube.dual_lattice,N_nanotubes,N_max_structures)
    Searcher.structure_log.write_log(os.getcwd(),"myStructures.out")
    
    for i,structure in enumerate(Searcher.structure_log.structures):
        carbon_lattice = structure.carbon_lattice
        filename = "C{}_carbon_atoms_{}".format(carbon_lattice.npoints,i)
        output.write_points(filename,carbon_lattice,format="xyz")
        
        my_db = database.Database()
        my_db.init()
        my_db.add_structure(structure,add_dual_lattice=True,add_carbon_lattice=True)
        

if __name__=="__main__":
    my_capped_nanotube_search()



