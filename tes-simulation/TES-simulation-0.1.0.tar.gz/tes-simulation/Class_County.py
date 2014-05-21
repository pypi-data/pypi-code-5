
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# COUNTY class
# ===========================================================================================


class COUNTY(object):
  """
  
  Class for County object.  Explanations of some variable names are given below (see Initialize.getHDF5()
  for more information). The County object holds information about the county as a whole, whereas the 
  Ledda object holds information about the LEDDA within the county.
  
  rate_engagement               = The fraction of the county population that receives LEDDA support or
                                    that has a LFNJ.  These are people who have a work status of 1, 3, or 
                                    >=6.
  rate_nurture                  = The fraction of the county population who are unemployed or NIWF that 
                                    receive LEEDA support (via nurture funds).
  *_plus_savings_mean           = Mean of family incomes + savings, where savings is accumulated over 
                                    all years.

  """
  
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "County"
    self.population = Config.adult_county_population
    self.number_NILF = Config.adult_county_population * (1 - Config.rate_labor_participation) 

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    

    for Type in ['number_employed', 'number_unemployed']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'i')) 
      
    for Type in ['rate_unemployment', 'rate_engagement', 'rate_nurture',
      'R_dollars', 'R_tokens', 'R_total',
      
      'post_CBFS_family_income_tokens_mean', 'post_CBFS_family_income_dollars_mean',
      'post_CBFS_family_income_total_mean', 
      'post_CBFS_family_income_total_plus_savings_mean', 
      'post_CBFS_family_income_tokens_plus_savings_mean', 
      'post_CBFS_family_income_dollars_plus_savings_mean']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
    
    self.graphGroup = {}
    self.graphGroup['R+total'] = ['R_dollars', 'R_tokens', 'R_total']

    self.graphGroup['family+token'] = ['post_CBFS_family_income_tokens_mean', 
      'post_CBFS_family_income_tokens_plus_savings_mean']
    self.graphGroup['family+dollar'] = ['post_CBFS_family_income_dollars_mean', 
      'post_CBFS_family_income_dollars_plus_savings_mean']    
    self.graphGroup['family+total'] = ['post_CBFS_family_income_total_mean', 
      'post_CBFS_family_income_total_plus_savings_mean']  

    
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def updateCounty(self, Year):
    """
    
    Update County arrays and confirm that all tokens and dollars in the simulation economy balance.
    
    """      
    
    # income total
    self.R_dollars[Year] = Config.TP.cols.R_dollars[:].sum()
    self.R_tokens[Year] = Config.TP.cols.R_tokens[:].sum()
    self.R_total[Year] = Config.TP.cols.R_total[:].sum()
    
    # post-CBFS family income
    self.post_CBFS_family_income_tokens_mean[Year] = (Config.TF.cols.R_tokens[:] - \
      Config.TF.cols.P_CBFS_tokens[:]).mean()
    self.post_CBFS_family_income_dollars_mean[Year] = (Config.TF.cols.R_dollars[:] - \
      Config.TF.cols.P_CBFS_dollars[:]).mean()
    self.post_CBFS_family_income_total_mean[Year] = (Config.TF.cols.R_total[:] - \
      Config.TF.cols.P_CBFS_total[:]).mean()

    self.post_CBFS_family_income_tokens_plus_savings_mean[Year] = (Config.TF.cols.R_tokens[:] - \
      Config.TF.cols.P_CBFS_tokens[:] + Config.TF.cols.save_tokens[:]).mean()
    self.post_CBFS_family_income_dollars_plus_savings_mean[Year] = (Config.TF.cols.R_dollars[:] - \
      Config.TF.cols.P_CBFS_dollars[:] + Config.TF.cols.save_dollars[:]).mean()
    self.post_CBFS_family_income_total_plus_savings_mean[Year] = (Config.TF.cols.R_total[:] - \
      Config.TF.cols.P_CBFS_total[:] + Config.TF.cols.save_total[:]).mean()
    
    
    # Balance of total tokens in County, including pools (as if annual velocity == 1).  Should always 
    # equal zero.  Payments on loans by Org objects are not received by CBFS until following year.
    grand_total_tokens = -Config.Org.created_tokens.sum() + Config.Persons.R_tokens[Year] + \
      Config.Cbfs.pool_loan_SB_tokens[Year] + Config.Cbfs.pool_loan_PB_tokens[Year] + \
      Config.Cbfs.pool_loan_NP_tokens[Year] + Config.Cbfs.pool_subsidy_SB_tokens[Year] + \
      Config.Cbfs.pool_subsidy_PB_tokens[Year] + Config.Cbfs.pool_nurture_tokens[Year] + \
      Config.Cbfs.pool_donation_NP_tokens[Year] + Config.Org.P_CBFS_loan_SB_tokens[Year] + \
      Config.Org.P_CBFS_loan_PB_tokens[Year] + Config.Org.P_CBFS_loan_NP_tokens[Year]
    
    
    # Balance of total dollars in County, including pools (as if annual velocity == 1).  Should always
    # equal values at start. Payments on loans by Org objects are not received by CBFS until following 
    # year.
    grand_total_dollars = Config.Roc.pool_dollars[Year] + Config.Persons.R_dollars[Year] + \
      Config.Cbfs.pool_loan_SB_dollars[Year] + Config.Cbfs.pool_loan_PB_dollars[Year] + \
      Config.Cbfs.pool_loan_NP_dollars[Year] + Config.Cbfs.pool_subsidy_SB_dollars[Year] + \
      Config.Cbfs.pool_subsidy_PB_dollars[Year] + Config.Cbfs.pool_nurture_dollars[Year] + \
      Config.Cbfs.pool_donation_NP_dollars[Year] + \
      Config.Ledda.dollar_loss_inflation[Year] + \
      Config.Org.P_CBFS_loan_SB_dollars[Year] + \
      Config.Org.P_CBFS_loan_PB_dollars[Year] + Config.Org.P_CBFS_loan_NP_dollars[Year]

    assert np.allclose(grand_total_tokens, 0, atol=1)
    assert np.allclose(grand_total_dollars, self.R_dollars[0], atol=1)




