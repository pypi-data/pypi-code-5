
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# GOVERNMENT class
# ===========================================================================================


class GOVERNMENT(object):
  """
  
  Class for Government object.  Most variable names should be self-explanatory (see Initialize.getHDF5() 
  for more information). The government object holds tax payment and spending information.  The 
  government does not have local employees of its own.  Any budget surplus is spent in other counties 
  (recorded in the Roc object).  The government spends funds as contracts, subsidies, grants, and 
  support, where support (or assistance) refers to income assistance funds paid to individuals.  
  All persons who are NIWF or are unemployed receive some level of government support.  Goverment 
  spending in the LEDDA county remains fixed, except for assistance to individuals (which goes down as 
  unemployment drops).  Thus, spending in other counties increases over time. 
  
  Tax levels are determined in Initialize.setGovRates().
  
  """  
  
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "Gov"
    self.support_dollars_mean = None   # placeholder, parameters set in InitializeFx.setGovRates()

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    

    # ----------------------- receipts of government -----------------------
    for Type in [
      'R_tax_dollars']:        
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))

    # ----------------------- payments of government -----------------------
    
    # dollars, raw
    for Type in [
      'P_support_dollars', 
      'P_contract_SB_dollars', 'P_contract_PB_dollars', 'P_contract_NP_dollars',
      'P_subsidy_SB_dollars', 'P_subsidy_PB_dollars', 
      'P_grant_NP_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))

    # dollars, summaries
    for Type in [      
      'P_contract_dollars', 'P_subsidy_dollars', 
      'P_SB_dollars', 'P_PB_dollars', 'P_NP_dollars', 'P_Roc_spending_dollars',
      'P_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))

    # ----------------------- pools for unspent currency -----
    for Type in [
      'surplus_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
    
    self.graphGroup = {}
    self.graphGroup['funding+type'] = ['P_contract_SB_dollars', 'P_contract_PB_dollars', 
      'P_contract_NP_dollars', 'P_subsidy_SB_dollars', 'P_subsidy_PB_dollars', 'P_grant_NP_dollars', 
      'P_support_dollars']
    self.graphGroup['funding+sums'] = ['P_contract_dollars', 'P_subsidy_dollars']
    self.graphGroup['funding+org'] = ['P_SB_dollars', 'P_PB_dollars', 'P_NP_dollars']
    self.graphGroup['total'] = ['P_dollars', 'R_tax_dollars']
    
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizeReceipts(self,Year):
    """
    
    Collect receipts of tokens and dollars
    
    """     
    # ---------- receipts of government, from previous year ----------
    self.R_tax_dollars[Year] = Config.Persons.P_gov_tax_dollars[Year-1] 


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def makePayments(self,Year):    
    """
    
    Make payments of tokens and dollars. Government support for non-LEDDA-supported NIWF and unemployed 
    persons remains fixed at each individual's initial support level.  Government support for LEDDA-
    supported NIWF and unemployed is set at each individual's initial support level, unless that is lower
    than the mean of initial government support.  In that case, it is set to the mean.
    
    """    
    # ----------------------- payments of government -----------------
        
    self.P_support_dollars[Year] = Config.TP.cols.R_gov_support_dollars[:].sum()
    
    # grants and contracts to NP
    self.P_grant_NP_dollars[Year] = Config.Gov.P_grant_NP_dollars_annual
    self.P_contract_NP_dollars[Year] = Config.Gov.P_contract_NP_dollars_annual
    
    # split contracts and subsidies according to income ratios between SB & PB from previous year 
    SB_PB_wages_total = Config.Persons.R_wages_SB_total[Year-1] + Config.Persons.R_wages_PB_total[Year-1]
    fraction_SB_wages = Config.Persons.R_wages_SB_total[Year-1] / SB_PB_wages_total
    fraction_PB_wages = Config.Persons.R_wages_PB_total[Year-1] / SB_PB_wages_total

    self.P_contract_SB_dollars[Year] = Config.Gov.P_contract_forprofit_dollars_annual * fraction_SB_wages
    self.P_contract_PB_dollars[Year] = Config.Gov.P_contract_forprofit_dollars_annual * fraction_PB_wages
    
    self.P_subsidy_SB_dollars[Year] = Config.Gov.P_subsidy_forprofit_dollars_annual * fraction_SB_wages
    self.P_subsidy_PB_dollars[Year] = Config.Gov.P_subsidy_forprofit_dollars_annual * fraction_PB_wages
    

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizePayments(self, Year):    
    """
    
    Summarize payments for tokens, dollars, and tokens + dollars.
    
    """
    # ----------------------- payments of government -----------------------
    
    self.P_contract_dollars[Year] = self.P_contract_NP_dollars[Year] + \
      self.P_contract_SB_dollars[Year] + self.P_contract_PB_dollars[Year]
    
    self.P_subsidy_dollars[Year] = self.P_subsidy_SB_dollars[Year] + \
      self.P_subsidy_PB_dollars[Year]
    
    self.P_dollars[Year] = self.P_contract_dollars[Year] + self.P_subsidy_dollars[Year] + \
      self.P_support_dollars[Year] + self.P_grant_NP_dollars[Year]
    
    self.P_SB_dollars[Year] = self.P_contract_SB_dollars[Year] + \
      self.P_subsidy_SB_dollars[Year]
    
    self.P_PB_dollars[Year] = self.P_contract_PB_dollars[Year] + \
      self.P_subsidy_PB_dollars[Year]
    
    self.P_NP_dollars[Year] = self.P_contract_NP_dollars[Year] + \
      self.P_grant_NP_dollars[Year]
    
    if Year > 1:
      # all surplus is spent in other counties
      self.P_Roc_spending_dollars[Year] = self.R_tax_dollars[Year] - self.P_dollars[Year]
      self.surplus_dollars[Year] = self.R_tax_dollars[Year] - self.P_dollars[Year] 
      self.P_dollars[Year] += self.P_Roc_spending_dollars[Year]
    
      # rest of counties receipts
      Config.Roc.R_gov_spending_dollars[Year] = self.P_Roc_spending_dollars[Year]


      assert np.allclose(self.R_tax_dollars[Year], self.P_dollars[Year], atol=.01)


