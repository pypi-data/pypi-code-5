
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# Rest of counties class, representing all other counties
# ===========================================================================================


class ROC(object):
  """
  
  Class for the Rest of Counties object.  Most variable names should be self-explanatory (see 
  Initialize.getHDF5() and Config for more information). The Roc object receives government spending and
  imports dollars from organizations (via outside purchases by organizations).  It exports dollars to 
  organizations (via sales by organizations to Roc).  The Roc object provides a mechanism to alter the 
  trade balance.  
  
  In the simulation, the government would run a surplus if not for spending its excess to the Roc object.
  The surplus is caused by rising tax revenue due to the rising incomes of members, but flat government 
  spending on grants, subsidies, and contracts, and reduced government spending for assistance, due to 
  fewer unemployed people.   
  
  This class has no functions.  Receipts are handled in Gov and Org functions, and payments are
  handled in Org functions.  
  
  """
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "ROC"

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    
    
    for Type in [
    'R_gov_spending_dollars', 'R_org_spending_dollars',
    'P_org_spending_dollars', 'pool_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
    
    self.graphGroup = {}
    self.graphGroup['R+P'] = ['R_gov_spending_dollars', 'R_org_spending_dollars',
    'P_org_spending_dollars']

  
        
    
    

    
    
