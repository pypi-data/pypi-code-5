
"""

          ****  "TES_simulation"  ****

View README.rst for information on this package.

Author: John Boik
Address: http://www.PrincipledSocietiesProject.org
GNU General Public License, version 3 (GPL-3.0). 

"""


# =====================================================================
# Python imports and module options
# =====================================================================

import cPickle, os, pylab, pdb, time, sys, os, glob
import numpy as np
import tables as tb
from scipy import stats

# Read modules in local directory. 
sys.path.append('./')  # 

import Config, MiscFx, InitializeFx
import Debug


# numpy options
np.set_printoptions(4, 120, 150, 220, True)
np.seterr(all='raise', divide='raise', over='raise', under='raise', invalid='raise')




# =====================================================================
# Setup folders and objects 
# =====================================================================

InitializeFx.makeFolders()

        
# initialize objects
InitializeFx.initializeObjects()


# =====================================================================
# Run simulation
# =====================================================================

Config.logRoot.info("""

# =====================================================================
# Run simulation
# ===================================================================== 

""")


for Year in range(Config.start_simulation_year, Config.simulation_period - 1):
  
  Config.logRoot.info("""

  # =====================================================================
  # Year """ + str(Year) + """
  # ===================================================================== 

  """)
  
  # =====================================================================
  # Conduct annual cycle
  # =====================================================================
  
  # if Year > 0, save old tables and make copies for current year
  if Year > 0:
    MiscFx.copyTables(Year)
  
  if Year >= (Config.burn_in_period - 1):
    # add new members
    Config.Ledda.addMembers(Year)

  if Year > Config.burn_in_period:
    # job loss for Ledda members due to structural unemployment
    Config.Ledda.loseJobs(Year)
    
  if Year >= Config.burn_in_period:    
    # raise wages of employed members according to target income schedule
    Config.Org.raiseWages(Year)

  if Year >= Config.burn_in_period:  
    # CBFS spending and job creation based on previous year contributions
    Config.Cbfs.summarizeReceipts(Year)
    if Year > Config.burn_in_period:
      Config.Cbfs.makePayments(Year)
    Config.Cbfs.summarizePayments(Year)
      
  if Year > 0:
    # government spending
    Config.Gov.summarizeReceipts(Year)
    Config.Gov.makePayments(Year)
    Config.Gov.summarizePayments(Year)

    # Organizations pay wages.  
    Config.Org.summarizeReceipts(Year)  
    Config.Org.makePayments(Year)
    Config.Org.summarizePayments(Year)
    
  # individuals pay taxes, make CBFS contributions, and spend money
  Config.Persons.summarizeReceipts(Year)
  Config.Persons.makePayments(Year)
  Config.Persons.summarizePayments(Year)

    
  # =====================================================================
  # Update object arrays and tables, and graph results
  # =====================================================================

  # update unemployment rates after job creation and loss
  Config.Ledda.updateUnemployment(Year)

  if Year > 0:
    # update family table
    Config.Persons.updateFamily(Year)

  # update County & Ledda arrays
  Config.County.updateCounty(Year)
  
  if Year >= Config.burn_in_period-1: 
    Config.Ledda.updateLedda(Year)
  
  # print year-end info from objects
  Config.logRoot.info("\n")
  MiscFx.PrintObj(Config.County, Year)
  MiscFx.PrintObj(Config.Ledda, Year)
  MiscFx.PrintObj(Config.Cbfs, Year) 
  MiscFx.PrintObj(Config.Persons, Year) 
  MiscFx.PrintObj(Config.Org, Year)
  MiscFx.PrintObj(Config.Roc, Year)
  MiscFx.PrintObj(Config.Gov, Year) 
     
  # do some final checks to object's data
  MiscFx.doChecks(Year)
  
  # graph results, turn graphing off to speed simulation
  if Config.make_graphs == True:
    MiscFx.graphResults(Year, Start=Config.burn_in_period-1)


# =================== end of loop ======================================= 

# make annimations from saved graphs
MiscFx.makeAnnimations()

# close HDF5 table and save objects
MiscFx.saveData()


Config.logRoot.info("\n   *** The simulation has finished ***\n")




