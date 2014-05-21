
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# CBFS class
# ===========================================================================================


class CBFS(object):
  """
  
  Class for CBFS object.  Explanations of some variable names are given below (see Initialize.getHDF5() 
  and Config for more information).  The CBFS receives first funds in Year == Config.burn_in_period, and 
  uses them the following year.
  
  R_loan_prin_*                 = amounts received from organizations as payment of loan principal
  loan_outstd_*                 = amount of outstanding CBFS loans owed by organizations
  P_TS_*                        = token share of payments for different CBFS accounts
  *_contrib_*                   = dollar and tokens shares of CBFS contributions
  factor_*                      = Factors that affect the token and dollar shares of contributions.
                                    See Ledda.initialTokenDollarContributions() for more info.
  *_token_share_CBFS            = token share of CBFS total payments and receipts
  engagements_created_nurture   = akin to jobs_created_*, only for nurture engagements.
  pool_*                        = Amount remaining at end of year in each CBFS account after all 
                                    payments have been made.  An excess of tokens or dollars might 
                                    occur in an account if the account receives too many or too few 
                                    tokens relative to the amount of dollars it receives.  Job creation
                                    and support are provided at some ratio of tokens and dollars, 
                                    which depends on the individual who receives the job/support.  All
                                    pools are essentially zeroed out at the end of the year, however.
                                    Any extra nurture funds are transfered to subsidy and donation
                                    accounts for additional job creation, and any remaining subsidy and
                                    donation funds are sent to organizations without accounting for job
                                    creation.  See self.makePayments()
  pool_token_share              = token share within all pools in total
  nurture_fraction_P            = fraction of contributed nurture funds that are spent on nurture 
                                    engagements.  A low fraction suggests that too many dollars are being
                                    contributed to the nurture fund relative to tokens. See 
                                    Ledda.initialTokenDollarContributions() for more info.  
  *_preTrans                    = The residual amount in pools after initial payments have been made but
                                  prior to any transfer of funds into other pools.  If the token and 
                                  dollar amounts in preTrans pools are too high, it suggests that the 
                                  earmarks corresponding to those pools are too high.
    
  """  
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "CBFS"
    self.earmark_lending_SB = Config.earmark_lending_SB    
    self.earmark_lending_PB = Config.earmark_lending_PB 
    self.earmark_lending_NP = Config.earmark_lending_NP          
    self.earmark_subsidy_SB = Config.earmark_subsidy_SB
    self.earmark_subsidy_PB = Config.earmark_subsidy_PB
    self.earmark_nurture = Config.earmark_nurture
    self.earmark_donation_NP = Config.earmark_donation_NP

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    

    # ----------------------- CBFS pools for currency -----------------------
    for Type in [
      'R_loan_SB_tokens', 'R_loan_PB_tokens', 'R_loan_NP_tokens', 
      'R_loan_SB_dollars', 'R_loan_PB_dollars', 'R_loan_NP_dollars',
      'R_subsidy_SB_tokens', 'R_subsidy_PB_tokens',
      'R_subsidy_SB_dollars', 'R_subsidy_PB_dollars',
      'R_nurture_dollars', 'R_nurture_tokens',
      'R_donation_NP_tokens', 'R_donation_NP_dollars',
      'R_loan_prin_tokens', 'R_loan_prin_dollars', 'R_loan_prin_total',
      
      'P_loan_SB_tokens', 'P_loan_PB_tokens', 'P_loan_NP_tokens', 
      'P_loan_SB_dollars', 'P_loan_PB_dollars', 'P_loan_NP_dollars',
      'P_subsidy_SB_tokens', 'P_subsidy_PB_tokens',
      'P_subsidy_SB_dollars', 'P_subsidy_PB_dollars',
      'P_nurture_dollars', 'P_nurture_tokens',
      'P_donation_NP_tokens', 'P_donation_NP_dollars',
      
      'nurture_fraction_P',
      
      'P_loan_tokens', 'P_loan_dollars', 'P_loan_total',
      'R_loan_tokens', 'R_loan_dollars', 'R_loan_total',
      'loan_outstd_tokens', 'loan_outstd_dollars', 'loan_outstd_total',

      'pool_loan_SB_tokens', 'pool_loan_PB_tokens', 'pool_loan_NP_tokens', 
      'pool_subsidy_SB_tokens', 'pool_subsidy_PB_tokens',
      'pool_nurture_tokens', 'pool_donation_NP_tokens',
      
      'pool_loan_SB_dollars', 'pool_loan_PB_dollars', 'pool_loan_NP_dollars',
      'pool_subsidy_SB_dollars', 'pool_subsidy_PB_dollars',
      'pool_nurture_dollars', 'pool_donation_NP_dollars',
      'pool_loan_tokens', 'pool_loan_dollars', 'pool_loan_total', 
      'pool_tokens', 'pool_dollars', 'pool_total', 

      'pool_loan_SB_tokens_preTrans', 'pool_loan_PB_tokens_preTrans', 'pool_loan_NP_tokens_preTrans', 
      'pool_subsidy_SB_tokens_preTrans', 'pool_subsidy_PB_tokens_preTrans',
      'pool_nurture_tokens_preTrans', 'pool_donation_NP_tokens_preTrans',
      
      'pool_loan_SB_dollars_preTrans', 'pool_loan_PB_dollars_preTrans', 'pool_loan_NP_dollars_preTrans',
      'pool_subsidy_SB_dollars_preTrans', 'pool_subsidy_PB_dollars_preTrans',
      'pool_nurture_dollars_preTrans', 'pool_donation_NP_dollars_preTrans',

      'P_TS_loan_SB', 'P_TS_loan_PB', 'P_TS_loan_NP', 
      'P_TS_subsidy_SB', 'P_TS_subsidy_PB', 
      'P_TS_donation_NP', 'P_TS_nurture', 'pool_token_share',     

      'DS_contrib', 'DS_contrib_nurture', 'TS_contrib', 'factor_gov_support', 'factor_growth',
             
      'R_tokens', 'R_dollars', 'R_total', 'R_token_share_CBFS',
      'P_tokens', 'P_dollars', 'P_total', 'P_token_share_CBFS',
      
      'jobs_created_SB', 'jobs_created_PB', 'jobs_created_NP', 
      'engagements_created_nurture']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    

    # graph groups
    self.graphGroup = {}

    # loans
    self.graphGroup['P+R+loan+SB+tokens'] = ['R_loan_SB_tokens', 'P_loan_SB_tokens']
    self.graphGroup['P+R+loan+PB+tokens'] = ['R_loan_PB_tokens', 'P_loan_PB_tokens']
    self.graphGroup['P+R+loan+NP+tokens'] = ['R_loan_NP_tokens', 'P_loan_NP_tokens']

    self.graphGroup['P+R+loan+SB+dollars'] = ['R_loan_SB_dollars', 'P_loan_SB_dollars']
    self.graphGroup['P+R+loan+PB+dollars'] = ['R_loan_PB_dollars', 'P_loan_PB_dollars']
    self.graphGroup['P+R+loan+NP+dollars'] = ['R_loan_NP_dollars', 'P_loan_NP_dollars']
    
    self.graphGroup['P+R+loan+tokens'] = ['R_loan_tokens', 'P_loan_tokens']
    self.graphGroup['P+R+loan+dollars'] = ['R_loan_dollars', 'P_loan_dollars']
    self.graphGroup['P+R+loan+total'] = ['R_loan_total', 'P_loan_total']

    self.graphGroup['principal'] = ['R_loan_prin_tokens', 'R_loan_prin_dollars', 'R_loan_prin_total']

    self.graphGroup['loan+outstanding'] = ['loan_outstd_tokens', 'loan_outstd_dollars', 
      'loan_outstd_total']
      
    # pools
    self.graphGroup['pool+loan+tokens'] = ['pool_loan_SB_tokens', 'pool_loan_PB_tokens', 
      'pool_loan_NP_tokens']

    self.graphGroup['pool+loan+dollars'] = ['pool_loan_SB_dollars', 'pool_loan_PB_dollars', 
      'pool_loan_NP_dollars'] 
      
    self.graphGroup['pool+loan+sum'] = ['pool_loan_tokens', 'pool_loan_dollars', 'pool_loan_total']

    self.graphGroup['pool+subsidy'] = ['pool_subsidy_SB_tokens', 'pool_subsidy_PB_tokens',
      'pool_subsidy_SB_dollars', 'pool_subsidy_PB_dollars']

    self.graphGroup['pool+nurture'] = ['pool_nurture_dollars', 'pool_nurture_tokens']            

    self.graphGroup['pool+donation'] = ['pool_donation_NP_tokens', 'pool_donation_NP_dollars']  
      
    self.graphGroup['pool+sum'] = ['pool_tokens', 'pool_dollars', 'pool_total']

    # pools, pre-transfer
    self.graphGroup['preTrans+pool+loan+SB'] = ['pool_loan_SB_tokens_preTrans', 
      'pool_loan_SB_dollars_preTrans']
    self.graphGroup['preTrans+pool+loan+PB'] = ['pool_loan_PB_tokens_preTrans', 
      'pool_loan_PB_dollars_preTrans']      
    self.graphGroup['preTrans+pool+loan+NP'] = ['pool_loan_NP_tokens_preTrans', 
      'pool_loan_NP_dollars_preTrans']      
      
    self.graphGroup['preTrans+pool+subsidy+SB'] = ['pool_subsidy_SB_tokens_preTrans', 
      'pool_subsidy_SB_dollars_preTrans']

    self.graphGroup['preTrans+pool+subsidy+PB'] = ['pool_subsidy_PB_tokens_preTrans', \
      'pool_subsidy_PB_dollars_preTrans']

    self.graphGroup['preTrans+pool+nurture'] = ['pool_nurture_dollars_preTrans', 
      'pool_nurture_tokens_preTrans']            

    self.graphGroup['preTrans+pool+donation'] = ['pool_donation_NP_tokens_preTrans', 
      'pool_donation_NP_dollars_preTrans']  
      
    # subsidy
    self.graphGroup['P+R+subsidy+tokens'] = ['R_subsidy_SB_tokens', 'R_subsidy_PB_tokens',
      'P_subsidy_SB_tokens', 'P_subsidy_PB_tokens']
    
    self.graphGroup['P+R+subsidy+dollars'] = ['R_subsidy_SB_dollars', 'R_subsidy_PB_dollars',
      'P_subsidy_SB_dollars', 'P_subsidy_PB_dollars']
      
    # nurture 
    self.graphGroup['P+R+nurture+tokens'] = ['R_nurture_tokens', 'P_nurture_tokens']
    
    self.graphGroup['P+R+nurture+dollars'] = ['R_nurture_dollars', 'P_nurture_dollars']
    
    # donation
    self.graphGroup['P+R+donation+tokens'] = ['R_donation_NP_tokens', 'P_donation_NP_tokens']
    
    self.graphGroup['P+R+donation+dollars'] = ['R_donation_NP_dollars', 'P_donation_NP_dollars']
    
    # other
    self.graphGroup['P+R+totals'] = ['R_tokens', 'R_dollars', 'R_total',
      'P_tokens', 'P_dollars', 'P_total']
    
    self.graphGroup['jobs'] = ['jobs_created_SB', 'jobs_created_PB', 'jobs_created_NP', 
      'engagements_created_nurture']
    
    self.graphGroup['share+CBFS'] = ['R_token_share_CBFS', 'P_token_share_CBFS']

    self.graphGroup['share+P'] = ['P_TS_loan_SB', 'P_TS_loan_PB', 'P_TS_loan_NP', 
      'P_TS_subsidy_SB', 'P_TS_subsidy_PB', 'P_TS_donation_NP', 'P_TS_nurture']
    
    self.graphGroup['share+contribution'] = ['DS_contrib', 'DS_contrib_nurture', 'TS_contrib']
     

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizeReceipts(self, Year):
    """
    
    Summarize CBFS receipts for tokens, dollars, and tokens + dollars.
    
    """
    # ----------------------- receipts of CBFS -----------------------
        
    self.R_loan_SB_tokens[Year] = Config.Persons.P_CBFS_loan_SB_tokens[Year-1]
    self.R_loan_PB_tokens[Year] = Config.Persons.P_CBFS_loan_PB_tokens[Year-1]
    self.R_loan_NP_tokens[Year] = Config.Persons.P_CBFS_loan_NP_tokens[Year-1]
    self.R_loan_SB_dollars[Year] = Config.Persons.P_CBFS_loan_SB_dollars[Year-1]
    self.R_loan_PB_dollars[Year] = Config.Persons.P_CBFS_loan_PB_dollars[Year-1]
    self.R_loan_NP_dollars[Year] = Config.Persons.P_CBFS_loan_NP_dollars[Year-1]
    self.R_subsidy_SB_tokens[Year] = Config.Persons.P_CBFS_subsidy_SB_tokens[Year-1]
    self.R_subsidy_PB_tokens[Year] = Config.Persons.P_CBFS_subsidy_PB_tokens[Year-1]
    self.R_subsidy_SB_dollars[Year] = Config.Persons.P_CBFS_subsidy_SB_dollars[Year-1]
    self.R_subsidy_PB_dollars[Year] = Config.Persons.P_CBFS_subsidy_PB_dollars[Year-1]
    self.R_nurture_tokens[Year] = Config.Persons.P_CBFS_nurture_tokens[Year-1]
    self.R_nurture_dollars[Year] = Config.Persons.P_CBFS_nurture_dollars[Year-1]
    self.R_donation_NP_tokens[Year] = Config.Persons.P_CBFS_donation_NP_tokens[Year-1]
    self.R_donation_NP_dollars[Year] = Config.Persons.P_CBFS_donation_NP_dollars[Year-1]

    # account for returned loan principal by Orgs, assumes 3-year average loan maturity
    self.R_loan_prin_tokens[Year] = Config.Org.P_CBFS_loan_SB_tokens[Year-1] + \
      Config.Org.P_CBFS_loan_PB_tokens[Year-1] + Config.Org.P_CBFS_loan_NP_tokens[Year-1] 
    self.R_loan_prin_dollars[Year] = Config.Org.P_CBFS_loan_SB_dollars[Year-1] + \
      Config.Org.P_CBFS_loan_PB_dollars[Year-1] + Config.Org.P_CBFS_loan_NP_dollars[Year-1]
    self.R_loan_prin_total[Year] = self.R_loan_prin_tokens[Year] + self.R_loan_prin_dollars[Year]
    
    self.R_loan_SB_tokens[Year] += Config.Org.P_CBFS_loan_SB_tokens[Year-1] 
    self.R_loan_PB_tokens[Year] += Config.Org.P_CBFS_loan_PB_tokens[Year-1] 
    self.R_loan_NP_tokens[Year] += Config.Org.P_CBFS_loan_NP_tokens[Year-1] 
    
    self.R_loan_SB_dollars[Year] += Config.Org.P_CBFS_loan_SB_dollars[Year-1] 
    self.R_loan_PB_dollars[Year] += Config.Org.P_CBFS_loan_PB_dollars[Year-1] 
    self.R_loan_NP_dollars[Year] += Config.Org.P_CBFS_loan_NP_dollars[Year-1]         

    # loan totals
    self.R_loan_tokens[Year] = self.R_loan_SB_tokens[Year] + self.R_loan_PB_tokens[Year] + \
      self.R_loan_NP_tokens[Year]
    self.R_loan_dollars[Year] = self.R_loan_SB_dollars[Year] + self.R_loan_PB_dollars[Year] + \
      self.R_loan_NP_dollars[Year]
    self.R_loan_total[Year] = self.R_loan_tokens[Year] + self.R_loan_dollars[Year]

    # carry over previous year pools and add receipts
    self.pool_loan_SB_tokens[Year] = self.pool_loan_SB_tokens[Year-1] + self.R_loan_SB_tokens[Year]
    self.pool_loan_PB_tokens[Year] = self.pool_loan_PB_tokens[Year-1] + self.R_loan_PB_tokens[Year]
    self.pool_loan_NP_tokens[Year] = self.pool_loan_NP_tokens[Year-1] + self.R_loan_NP_tokens[Year]
    self.pool_loan_SB_dollars[Year] = self.pool_loan_SB_dollars[Year-1] + self.R_loan_SB_dollars[Year]
    self.pool_loan_PB_dollars[Year] = self.pool_loan_PB_dollars[Year-1] + self.R_loan_PB_dollars[Year]
    self.pool_loan_NP_dollars[Year] = self.pool_loan_NP_dollars[Year-1] + self.R_loan_NP_dollars[Year]
    self.pool_subsidy_SB_tokens[Year] = self.pool_subsidy_SB_tokens[Year-1] + \
      self.R_subsidy_SB_tokens[Year]
    self.pool_subsidy_PB_tokens[Year] = self.pool_subsidy_PB_tokens[Year-1] + \
      self.R_subsidy_PB_tokens[Year]
    self.pool_subsidy_SB_dollars[Year] = self.pool_subsidy_SB_dollars[Year-1] + \
      self.R_subsidy_SB_dollars[Year]
    self.pool_subsidy_PB_dollars[Year] = self.pool_subsidy_PB_dollars[Year-1] + \
      self.R_subsidy_PB_dollars[Year]
    self.pool_nurture_tokens[Year] = self.pool_nurture_tokens[Year-1] + self.R_nurture_tokens[Year]
    self.pool_nurture_dollars[Year] = self.pool_nurture_dollars[Year-1] + self.R_nurture_dollars[Year]
    self.pool_donation_NP_tokens[Year] = self.pool_donation_NP_tokens[Year-1] + \
      self.R_donation_NP_tokens[Year]
    self.pool_donation_NP_dollars[Year] = self.pool_donation_NP_dollars[Year-1] + \
      self.R_donation_NP_dollars[Year]

    # totals
    self.R_tokens[Year] = self.R_loan_SB_tokens[Year] + self.R_loan_PB_tokens[Year] + \
      self.R_loan_NP_tokens[Year] + self.R_subsidy_SB_tokens[Year] + \
      self.R_subsidy_PB_tokens[Year] + self.R_nurture_tokens[Year] + \
      self.R_donation_NP_tokens[Year] 
        
    self.R_dollars[Year] = self.R_loan_SB_dollars[Year] + self.R_loan_PB_dollars[Year] + \
      self.R_loan_NP_dollars[Year] + self.R_subsidy_SB_dollars[Year] + \
      self.R_subsidy_PB_dollars[Year] + self.R_nurture_dollars[Year] + \
      self.R_donation_NP_dollars[Year] 

    self.R_total[Year] = self.R_tokens[Year] + self.R_dollars[Year]
    
    if self.R_total[Year] != 0:
      self.R_token_share_CBFS[Year] = self.R_tokens[Year] / self.R_total[Year]

    
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def makePayments(self,Year):    
    """
    
    Make payments of tokens and dollars. Payments are made to organizations (loans, subsidies, donations)
    and to persons (nurture). As well, wages are paid to organizations (via CBFS donations) for LFNJ 
    nonprofit employees.  Once the initial round of payments has finished, transfer any remaining pool 
    funds to other CBFS accounts and create more jobs.  Then transfer any remaining pool funds to 
    organizations (to make accounting more simple, without job creation).
    
    """    

    # nurture payments to NIWF and unemployed, and nonprofit employees 
    self.donationExisting(Year)
    self.nurtureExisting(Year)
    self.nurtureNew(Year)
    
    # loans, subsidies, donations to orgs, record job creation 
    self.fundJobs(Year)

    # allow nurture pool to go negative
    #if (self.pool_nurture_tokens[Year] < 0) or (self.pool_nurture_dollars[Year] < 0):
    #  MiscFx.errorCode(1020)
    #  raise MiscFx.ParameterError     
    
    # Add new support for unemployed and NIWF using any nurture funds returned (a person who
    # received nuture support might obtain a job).
    self.nurtureNew(Year)

    # record amounts in pools prior to transfers
    self.pool_loan_SB_tokens_preTrans[Year] = self.pool_loan_SB_tokens[Year]
    self.pool_loan_PB_tokens_preTrans[Year] = self.pool_loan_PB_tokens[Year]
    self.pool_loan_NP_tokens_preTrans[Year] = self.pool_loan_NP_tokens[Year]
    self.pool_subsidy_SB_tokens_preTrans[Year] = self.pool_subsidy_SB_tokens[Year]
    self.pool_subsidy_PB_tokens_preTrans[Year] = self.pool_subsidy_PB_tokens[Year]
    self.pool_nurture_tokens_preTrans[Year] = self.pool_nurture_tokens[Year]
    self.pool_donation_NP_tokens_preTrans[Year] = self.pool_donation_NP_tokens[Year]
    self.pool_loan_SB_dollars_preTrans[Year] = self.pool_loan_SB_dollars[Year]
    self.pool_loan_PB_dollars_preTrans[Year] = self.pool_loan_PB_dollars[Year]
    self.pool_loan_NP_dollars_preTrans[Year] = self.pool_loan_NP_dollars[Year]
    self.pool_subsidy_SB_dollars_preTrans[Year] = self.pool_subsidy_SB_dollars[Year]
    self.pool_subsidy_PB_dollars_preTrans[Year] = self.pool_subsidy_PB_dollars[Year]
    self.pool_nurture_dollars_preTrans[Year] = self.pool_nurture_dollars[Year]
    self.pool_donation_NP_dollars_preTrans[Year] = self.pool_donation_NP_dollars[Year]
    
    Config.logRoot.debug("\n   ======== Making 1st Pool Transfers ========\n")
    
    # transfer remaining (unbalanced) nurture funds to subsidy pools
    # do not include NP, as too many people might be hired relative to long-term funding
    wages_SB = Config.TP.cols.R_wages_SB_tokens[:].sum() + Config.TP.cols.R_wages_SB_dollars[:].sum()
    wages_PB = Config.TP.cols.R_wages_PB_tokens[:].sum() + Config.TP.cols.R_wages_PB_dollars[:].sum()
    wages_total = wages_SB + wages_PB
    subsidy_SB_fraction = wages_SB / wages_total
    subsidy_PB_fraction = wages_PB / wages_total
    
    # keep small reserve in nurture pool
    reserve = 0
    subsidy_SB_share_tokens = \
      max(0, self.pool_nurture_tokens[Year] - reserve) * subsidy_SB_fraction
    subsidy_SB_share_dollars = \
      max(0, self.pool_nurture_dollars[Year] - reserve) * subsidy_SB_fraction
    subsidy_PB_share_tokens = \
      max(0, self.pool_nurture_tokens[Year] - reserve) * subsidy_PB_fraction
    subsidy_PB_share_dollars = \
      max(0, self.pool_nurture_dollars[Year] - reserve) * subsidy_PB_fraction


    self.pool_nurture_tokens[Year] -= subsidy_SB_share_tokens
    self.pool_nurture_dollars[Year] -= subsidy_SB_share_dollars
    self.pool_subsidy_SB_tokens[Year] += subsidy_SB_share_tokens
    self.pool_subsidy_SB_dollars[Year] += subsidy_SB_share_dollars

    self.pool_nurture_tokens[Year] -= subsidy_PB_share_tokens
    self.pool_nurture_dollars[Year] -= subsidy_PB_share_dollars
    self.pool_subsidy_PB_tokens[Year] += subsidy_PB_share_tokens
    self.pool_subsidy_PB_dollars[Year] += subsidy_PB_share_dollars    


    # transfered pools used for job creation 
    self.fundJobs(Year, omitLoans=True)    

    Config.logRoot.debug("\n   ======== Making 2nd Pool Transfers ========\n")
    
    # transfer remaining (positive) subsidy funds to orgs, no job creation (conservative)
    subsidy_SB_share_tokens = self.pool_subsidy_SB_tokens[Year]
    subsidy_SB_share_dollars = self.pool_subsidy_SB_dollars[Year]
    self.pool_subsidy_SB_tokens[Year] = 0
    self.pool_subsidy_SB_dollars[Year] = 0
    self.P_subsidy_SB_tokens[Year] += subsidy_SB_share_tokens
    self.P_subsidy_SB_dollars[Year] += subsidy_SB_share_dollars       
    
    subsidy_PB_share_tokens = self.pool_subsidy_PB_tokens[Year] 
    subsidy_PB_share_dollars = self.pool_subsidy_PB_dollars[Year]
    self.pool_subsidy_PB_tokens[Year] = 0
    self.pool_subsidy_PB_dollars[Year] = 0
    self.P_subsidy_PB_tokens[Year] += subsidy_PB_share_tokens
    self.P_subsidy_PB_dollars[Year] += subsidy_PB_share_dollars   
  
    donation_NP_share_tokens = max(0, self.pool_donation_NP_tokens[Year])
    donation_NP_share_dollars = max(0, self.pool_donation_NP_dollars[Year])
    self.pool_donation_NP_tokens[Year] = self.pool_donation_NP_tokens[Year] - donation_NP_share_tokens 
    self.pool_donation_NP_dollars[Year] = self.pool_donation_NP_dollars[Year] - donation_NP_share_dollars
    self.P_donation_NP_tokens[Year] += donation_NP_share_tokens
    self.P_donation_NP_dollars[Year] += donation_NP_share_dollars   
    
    # dump any remaining positive loan funds to orgs
    loan_SB_share_tokens = self.pool_loan_SB_tokens[Year] 
    loan_SB_share_dollars = self.pool_loan_SB_dollars[Year]
    self.pool_loan_SB_tokens[Year] = 0
    self.pool_loan_SB_dollars[Year] = 0
    self.P_loan_SB_tokens[Year] += loan_SB_share_tokens
    self.P_loan_SB_dollars[Year] += loan_SB_share_dollars       
    
    loan_PB_share_tokens = self.pool_loan_PB_tokens[Year] 
    loan_PB_share_dollars = self.pool_loan_PB_dollars[Year]
    self.pool_loan_PB_tokens[Year] = 0
    self.pool_loan_PB_dollars[Year] = 0
    self.P_loan_PB_tokens[Year] += loan_PB_share_tokens
    self.P_loan_PB_dollars[Year] += loan_PB_share_dollars   
  
    loan_NP_share_tokens = self.pool_loan_NP_tokens[Year] 
    loan_NP_share_dollars = self.pool_loan_NP_dollars[Year]
    self.pool_loan_NP_tokens[Year] = 0
    self.pool_loan_NP_dollars[Year] = 0
    self.P_loan_NP_tokens[Year] += loan_NP_share_tokens
    self.P_loan_NP_dollars[Year] += loan_NP_share_dollars     
 
      
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def donationExisting(self, Year):
    """
        
    CBFS donations are used to cover wages of LFNJ nonprofit employees.  
    
    """
    
    # -------------------------------------------------------------------------------
    # LFNJ nonprofit employees
    # -------------------------------------------------------------------------------
    
    Wn1 = Config.TP.getWhereList("(membership==1) & (work_status==6)")
    
    Config.logRoot.debug(
      "\nPaying wages for NP LFNJ employees:\n  number of employees= {0:d}\n".format(Wn1.size))
    
    if (self.pool_donation_NP_tokens[Year] + self.pool_donation_NP_dollars[Year]) == 0:
      Config.logRoot.debug("\n  *** donation funds are zero ***\n")
      
      if Wn1.size > 0:
        Config.logRoot.debug(
          "\n  *** no donation funds to provide support to LFNJ nonprofit employees ***\n")
        assert Wn1.size == 0
      else:
        return
    
    Config.logRoot.debug("  token share donation pool= {0:.4g}".format(
      self.pool_donation_NP_tokens[Year] / (self.pool_donation_NP_tokens[Year] + \
      self.pool_donation_NP_dollars[Year])))
    
    assert np.allclose(Config.TP.cols.R_tokens[:][Wn1], Config.TP.cols.R_wages_NP_tokens[:][Wn1])
    assert np.allclose(Config.TP.cols.R_dollars[:][Wn1], Config.TP.cols.R_wages_NP_dollars[:][Wn1])
    
    # raises to NP members were already given in Org.raiseWages(), just need to adjust pool and 
    # account for payments
    self.pool_donation_NP_tokens[Year] -= Config.TP.cols.R_wages_NP_tokens[:][Wn1].sum()
    self.pool_donation_NP_dollars[Year] -= Config.TP.cols.R_wages_NP_dollars[:][Wn1].sum()
    self.P_donation_NP_tokens[Year] += Config.TP.cols.R_wages_NP_tokens[:][Wn1].sum()
    self.P_donation_NP_dollars[Year] += Config.TP.cols.R_wages_NP_dollars[:][Wn1].sum()
    
    if (self.pool_donation_NP_tokens[Year] < 0) or (self.pool_donation_NP_dollars[Year] < 0):
      
      Config.logRoot.debug("\n   *** negative donation pool:  {0:,.9g} T, {1:,.9g} D ***\n".format(
        np.round(self.pool_donation_NP_tokens[Year],0).item(), \
        np.round(self.pool_donation_NP_dollars[Year],0).item()))
      
      #MiscFx.errorCode(1000)
      #raise MiscFx.ParameterError 


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def nurtureExisting(self, Year):
    """
    
    CBFS makes nurture payments to some NIWF and unemployed members. As funds are available, the set
    of supported members expands. Each supported member receives support based on the two Wage Options: 
    (1) income target schedule, or (2) incentive bonus on existing base wage.  
    
    """


    caseNumber = 1
    caseTitle = "Yr " + str(Year).zfill(2) + ", nurture exist. unemp., Case 1"
    searchString = "((membership==1) & (work_status==3))"
    newWorkStatus = 3
    pool_tokens = self.pool_nurture_tokens
    pool_dollars = self.pool_nurture_dollars
    person_tokens = Config.TP.cols.R_CBFS_nurture_tokens
    person_dollars = Config.TP.cols.R_CBFS_nurture_dollars
    paid_tokens = self.P_nurture_tokens
    paid_dollars = self.P_nurture_dollars
    jobCostMult = 1.
    jobsCreated = None
    self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
      person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)


    caseNumber = 2
    caseTitle = "Yr " + str(Year).zfill(2) + ", nurture exist. NIWF, Case 2"
    searchString = "((membership==1) & (work_status==1))"
    newWorkStatus = 1
    pool_tokens = self.pool_nurture_tokens
    pool_dollars = self.pool_nurture_dollars
    person_tokens = Config.TP.cols.R_CBFS_nurture_tokens
    person_dollars = Config.TP.cols.R_CBFS_nurture_dollars
    paid_tokens = self.P_nurture_tokens
    paid_dollars = self.P_nurture_dollars
    jobCostMult = 1.
    jobsCreated = None
    self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
      person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)
          
    # checks
    W102 = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (wage_option>0)")
    W102b = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (job_loss==1) & (job_gain==0)")
    W102d = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (R_postCBFS_total < base_wage) & (wage_option==2) & (job_loss!=1)")
    W102e = Config.TP.getWhereList("((membership==0) | (work_status==0) | (work_status==2)) " + \
      "& (R_tokens>0)")
    W102f = Config.TP.getWhereList("(wage_option==0) & (R_tokens>0)")

    assert np.all(Config.TP.cols.R_tokens[:][W102] > 0)
    assert np.all(Config.TP.cols.R_gov_support_dollars[:][W102b] > 0)
    assert W102d.size == 0 
    assert W102e.size == 0 
    assert W102f.size == 0 


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def nurtureNew(self, Year):
    """
    
    Expand the set of supported members.  Nurture payments made here (on first round) will later be 
    added back to pools for any unemployed, supported members who later obtain a job in current year.
    
    """

    caseNumber = 3
    caseTitle = "Yr " + str(Year).zfill(2) + ", nurture new unemp., Case 3"
    searchString = "((membership==1) & (work_status==2))"
    newWorkStatus = 3
    pool_tokens = self.pool_nurture_tokens
    pool_dollars = self.pool_nurture_dollars
    person_tokens = Config.TP.cols.R_CBFS_nurture_tokens
    person_dollars = Config.TP.cols.R_CBFS_nurture_dollars
    paid_tokens = self.P_nurture_tokens
    paid_dollars = self.P_nurture_dollars
    jobCostMult = 1.
    jobsCreated = self.engagements_created_nurture
    self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
      person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)


    caseNumber = 4
    caseTitle = "Yr " + str(Year).zfill(2) + ", nurture new NIWF, Case 4"
    searchString = "((membership==1) & (work_status==0))"
    newWorkStatus = 1
    pool_tokens = self.pool_nurture_tokens
    pool_dollars = self.pool_nurture_dollars
    person_tokens = Config.TP.cols.R_CBFS_nurture_tokens
    person_dollars = Config.TP.cols.R_CBFS_nurture_dollars
    paid_tokens = self.P_nurture_tokens
    paid_dollars = self.P_nurture_dollars
    jobCostMult = 1.
    jobsCreated = self.engagements_created_nurture
    self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
      person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

    # checks
    W102 = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (wage_option>0)")
    W102b = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (job_loss==1) & (job_gain==0)")
    W102d = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (R_postCBFS_total < base_wage) & (wage_option==2) & (job_loss!=1)")
    W102e = Config.TP.getWhereList("((membership==0) | (work_status==0) | (work_status==2)) " + \
      "& (R_tokens>0)")
    W102f = Config.TP.getWhereList("(wage_option==0) & (R_tokens>0)")

    assert np.all(Config.TP.cols.R_tokens[:][W102] > 0)
    assert np.all(Config.TP.cols.R_gov_support_dollars[:][W102b] > 0)
    assert W102d.size == 0 
    assert W102e.size == 0 
    assert W102f.size == 0 
    

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def fundJobs(self, Year, omitLoans=False, onlyLoans=False):
    """
    
    Fund organizations with remaining CBFS lending, subsidy, and donation funds. Assume that 
    Config.fraction_funding_job_creation of funds are used for job creation, with the remainder used to 
    fund operational costs.  The cost of each new for-profit job is Config.income_target_total x 
    Config.job_cost_multiplier. The multiplier for new nonprofit jobs is the same. LFNJs are offered to 
    unemployed first, then to employed.  This could reflect the situation where an employed person shifts
    to a newly created job, and an unemployed person takes the job that was vacated.  However, job offers
    to unemployed stop when the LEDDA structural unemployment level is reached.
    
    There are six cases for different types of funding:
      1 & 2: NP donation and loans
      3 & 4: SB subsidies and loans 
      5 & 6: PB subsidies and loans 
    Each case has two subcases: a) offering job to unemployed, and b) offering job to employed.  Thus in
    total there are 12 case/subcase combinations. Plus 4 from nurtureNew(self, Year) gives a total
    of 16 case/subcase combinations.
    
    """
    
    # subtract funds for operational costs from pool and record payments --------------
    
    # donations
    operations_tokens = self.pool_donation_NP_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_donation_NP_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_donation_NP_tokens[Year] -= operations_tokens
    self.pool_donation_NP_dollars[Year] -= operations_dollars
    self.P_donation_NP_tokens[Year] += operations_tokens
    self.P_donation_NP_dollars[Year] += operations_dollars  
    
    # lending, NP
    operations_tokens = self.pool_loan_NP_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_loan_NP_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_loan_NP_tokens[Year] -= operations_tokens
    self.pool_loan_NP_dollars[Year] -= operations_dollars
    self.P_loan_NP_tokens[Year] += operations_tokens
    self.P_loan_NP_dollars[Year] += operations_dollars     

    # lending, SB
    operations_tokens = self.pool_loan_SB_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_loan_SB_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_loan_SB_tokens[Year] -= operations_tokens
    self.pool_loan_SB_dollars[Year] -= operations_dollars
    self.P_loan_SB_tokens[Year] += operations_tokens
    self.P_loan_SB_dollars[Year] += operations_dollars    

    # lending, PB
    operations_tokens = self.pool_loan_PB_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_loan_PB_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_loan_PB_tokens[Year] -= operations_tokens
    self.pool_loan_PB_dollars[Year] -= operations_dollars
    self.P_loan_PB_tokens[Year] += operations_tokens
    self.P_loan_PB_dollars[Year] += operations_dollars       

    # subsidy, SB
    operations_tokens = self.pool_subsidy_SB_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_subsidy_SB_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_subsidy_SB_tokens[Year] -= operations_tokens
    self.pool_subsidy_SB_dollars[Year] -= operations_dollars
    self.P_subsidy_SB_tokens[Year] += operations_tokens
    self.P_subsidy_SB_dollars[Year] += operations_dollars    

    # subsidy, PB
    operations_tokens = self.pool_subsidy_PB_tokens[Year] * (1 - Config.fraction_funding_job_creation)
    operations_dollars = self.pool_subsidy_PB_dollars[Year] * (1 - Config.fraction_funding_job_creation)
    
    self.pool_subsidy_PB_tokens[Year] -= operations_tokens
    self.pool_subsidy_PB_dollars[Year] -= operations_dollars
    self.P_subsidy_PB_tokens[Year] += operations_tokens
    self.P_subsidy_PB_dollars[Year] += operations_dollars    
    
    # Call functions for job creation in random order, so that no one account (e.g., NP donation) has
    # continual first advantage on hiring from unemployment pool.
    
    Ran = np.random.permutation(6)
    for ran in Ran:
      if (ran == 0) and (onlyLoans == False):
        caseNumber = 5
        caseTitle = "Yr " + str(Year).zfill(2) + ", new NP donation jobs, unemp., Case 5"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 6
        pool_tokens = self.pool_donation_NP_tokens
        pool_dollars = self.pool_donation_NP_dollars
        person_tokens = Config.TP.cols.R_wages_NP_tokens
        person_dollars = Config.TP.cols.R_wages_NP_dollars
        paid_tokens = self.P_donation_NP_tokens
        paid_dollars = self.P_donation_NP_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_NP
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 6
        caseTitle = "Yr " + str(Year).zfill(2) + ", new NP donation jobs, emp., Case 6"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 6
        pool_tokens = self.pool_donation_NP_tokens
        pool_dollars = self.pool_donation_NP_dollars
        person_tokens = Config.TP.cols.R_wages_NP_tokens
        person_dollars = Config.TP.cols.R_wages_NP_dollars
        paid_tokens = self.P_donation_NP_tokens
        paid_dollars = self.P_donation_NP_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_NP
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

      if (ran == 1) and (omitLoans == False):
        caseNumber = 7
        caseTitle = "Yr " + str(Year).zfill(2) + ", new NP loan jobs, unemp., Case 7"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 6
        pool_tokens = self.pool_loan_NP_tokens
        pool_dollars = self.pool_loan_NP_dollars
        person_tokens = Config.TP.cols.R_wages_NP_tokens
        person_dollars = Config.TP.cols.R_wages_NP_dollars
        paid_tokens = self.P_loan_NP_tokens
        paid_dollars = self.P_loan_NP_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_NP
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 8
        caseTitle = "Yr " + str(Year).zfill(2) + ", new NP loan jobs, emp., Case 8"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 6
        pool_tokens = self.pool_loan_NP_tokens
        pool_dollars = self.pool_loan_NP_dollars
        person_tokens = Config.TP.cols.R_wages_NP_tokens
        person_dollars = Config.TP.cols.R_wages_NP_dollars
        paid_tokens = self.P_loan_NP_tokens
        paid_dollars = self.P_loan_NP_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_NP
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

      if (ran == 2) and (onlyLoans == False):
        caseNumber = 9
        caseTitle = "Yr " + str(Year).zfill(2) + ", new SB subsidy jobs, unemp., Case 9"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 7
        pool_tokens = self.pool_subsidy_SB_tokens
        pool_dollars = self.pool_subsidy_SB_dollars
        person_tokens = Config.TP.cols.R_wages_SB_tokens
        person_dollars = Config.TP.cols.R_wages_SB_dollars
        paid_tokens = self.P_subsidy_SB_tokens
        paid_dollars = self.P_subsidy_SB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_SB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 10
        caseTitle = "Yr " + str(Year).zfill(2) + ", new SB subsidy jobs, emp., Case 10"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 7
        pool_tokens = self.pool_subsidy_SB_tokens
        pool_dollars = self.pool_subsidy_SB_dollars
        person_tokens = Config.TP.cols.R_wages_SB_tokens
        person_dollars = Config.TP.cols.R_wages_SB_dollars
        paid_tokens = self.P_subsidy_SB_tokens
        paid_dollars = self.P_subsidy_SB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_SB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

      if (ran == 3) and (omitLoans == False):
        caseNumber = 11
        caseTitle = "Yr " + str(Year).zfill(2) + ", new SB loan jobs, unemp., Case 11"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 7
        pool_tokens = self.pool_loan_SB_tokens
        pool_dollars = self.pool_loan_SB_dollars
        person_tokens = Config.TP.cols.R_wages_SB_tokens
        person_dollars = Config.TP.cols.R_wages_SB_dollars
        paid_tokens = self.P_loan_SB_tokens
        paid_dollars = self.P_loan_SB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_SB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 12
        caseTitle = "Yr " + str(Year).zfill(2) + ", new SB loan jobs, emp., Case 12"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 7
        pool_tokens = self.pool_loan_SB_tokens
        pool_dollars = self.pool_loan_SB_dollars
        person_tokens = Config.TP.cols.R_wages_SB_tokens
        person_dollars = Config.TP.cols.R_wages_SB_dollars
        paid_tokens = self.P_loan_SB_tokens
        paid_dollars = self.P_loan_SB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_SB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

      if (ran == 4) and (onlyLoans == False):
        caseNumber = 13
        caseTitle = "Yr " + str(Year).zfill(2) + ", new PB subsidy jobs, unemp., Case 13"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 8
        pool_tokens = self.pool_subsidy_PB_tokens
        pool_dollars = self.pool_subsidy_PB_dollars
        person_tokens = Config.TP.cols.R_wages_PB_tokens
        person_dollars = Config.TP.cols.R_wages_PB_dollars
        paid_tokens = self.P_subsidy_PB_tokens
        paid_dollars = self.P_subsidy_PB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_PB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 14
        caseTitle = "Yr " + str(Year).zfill(2) + ", new PB subsidy jobs, emp., Case 14"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 8
        pool_tokens = self.pool_subsidy_PB_tokens
        pool_dollars = self.pool_subsidy_PB_dollars
        person_tokens = Config.TP.cols.R_wages_PB_tokens
        person_dollars = Config.TP.cols.R_wages_PB_dollars
        paid_tokens = self.P_subsidy_PB_tokens
        paid_dollars = self.P_subsidy_PB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_PB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)


      if (ran == 5) and (omitLoans == False):
        caseNumber = 15
        caseTitle = "Yr " + str(Year).zfill(2) + ", new PB loan jobs, unemp., Case 15"
        searchString = "((membership==1) & ((work_status==2) | (work_status==3)))"
        newWorkStatus = 8
        pool_tokens = self.pool_loan_PB_tokens
        pool_dollars = self.pool_loan_PB_dollars
        person_tokens = Config.TP.cols.R_wages_PB_tokens
        person_dollars = Config.TP.cols.R_wages_PB_dollars
        paid_tokens = self.P_loan_PB_tokens
        paid_dollars = self.P_loan_PB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_PB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

        caseNumber = 16
        caseTitle = "Yr " + str(Year).zfill(2) + ", new PB loan jobs, emp., Case 16"
        searchString = "((membership==1) & (work_status>=4) & (job_gain==0))"
        newWorkStatus = 8
        pool_tokens = self.pool_loan_PB_tokens
        pool_dollars = self.pool_loan_PB_dollars
        person_tokens = Config.TP.cols.R_wages_PB_tokens
        person_dollars = Config.TP.cols.R_wages_PB_dollars
        paid_tokens = self.P_loan_PB_tokens
        paid_dollars = self.P_loan_PB_dollars
        jobCostMult = Config.job_cost_multiplier
        jobsCreated = self.jobs_created_PB
        self.caseFunding(caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
        person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year)

    # checks
    W102 = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (wage_option>0)")
    W102b = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (job_loss==1) & (job_gain==0)")
    W102d = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (R_postCBFS_total < base_wage) & (wage_option==2) & (job_loss!=1)")
    W102e = Config.TP.getWhereList("((membership==0) | (work_status==0) | (work_status==2)) " + \
      "& (R_tokens>0)")
    W102f = Config.TP.getWhereList("(wage_option==0) & (R_tokens>0)")
    W102g = Config.TP.getWhereList("(R_postCBFS_tokens>0) & (R_tokens==0)")

    assert np.all(Config.TP.cols.R_tokens[:][W102] > 0)
    assert np.all(Config.TP.cols.R_gov_support_dollars[:][W102b] > 0)
    assert W102d.size == 0 
    assert W102e.size == 0 
    assert W102f.size == 0  
    assert W102g.size == 0   
         
                      
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def caseFunding(self, caseNumber, caseTitle, searchString, newWorkStatus, pool_tokens, pool_dollars, \
      person_tokens, person_dollars, paid_tokens, paid_dollars, jobCostMult, jobsCreated, Year):
    """
    
    Code used for all 16 cases to fund jobs.  Accounting is complicated by the fact that families, and 
    not individuals, choose Wage Options.  Thus, if one person has a job, for example, and the other is 
    offered one, a new Wage Option is chosen that could affect incomes of both persons.  The function
    getFamilyData(...) is used to collect Persons, BaseWage, etc. for both members of all affected 
    families.  It results in numerous nx2 arrays, where the first column pertains to person 1 and the 
    second to person 2.  Loops occur based on these arrays.
    
    """


    if (pool_tokens[Year] <= 0) or (pool_dollars[Year] <= 0):
      Config.logRoot.debug("\n   *** negative or zero pool, caseNumber = {0:d} ***\n".format(caseNumber))
      return

    Config.logRoot.debug("\n***** {0:s} *****".format(caseTitle))
        
    P0 = Config.TP.getWhereList(searchString)
    if caseNumber in [1,2]: 
      loopSize = P0.size
    else:
      # give everyone at least three chances, on average, to accept a job or nurture engagement (assuming
      # funds do not run dry).  This avoids endless loops.
      loopSize = P0.size * 3
    
    for outerLoop in range(loopSize):
      
      P0 = Config.TP.getWhereList(searchString)
      if P0.size==0:
        Config.logRoot.debug("  *** no persons match the search string ***")
        return         
      
      # do funding one person at a time, except for cases 1 and 2
      if caseNumber not in [1,2]:
        np.random.shuffle(P0)
        P0 = np.array([P0[0]])

      if caseNumber in [1,2,3,4,5,7,9,11,13,15]:
        assert np.all(Config.TP.cols.R_gov_support_dollars[:][P0] > 0)

      if caseNumber in [6,8,10,12,14,16]:
        assert np.all(Config.TP.cols.R_gov_support_dollars[:][P0] == 0)
      
      if caseNumber in [1,2]:
        assert np.allclose(Config.TP.cols.R_tokens[:][P0], Config.TP.cols.R_CBFS_nurture_tokens[:][P0])
        assert np.allclose(
          Config.TP.cols.R_dollars[:][P0], Config.TP.cols.R_CBFS_nurture_dollars[:][P0] + \
          Config.TP.cols.R_gov_support_dollars[:][P0])

      if caseNumber in [3,4]:
        assert np.allclose(Config.TP.cols.R_tokens[:][P0], 0)
        assert np.allclose(Config.TP.cols.R_dollars[:][P0], Config.TP.cols.R_gov_support_dollars[:][P0])      
      
      # Persons, etc. size 1x2 if caseNumber not in [1,2]
      Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0 = \
        Config.Persons.getFamilyData(P0) 

      if caseNumber in [1,2]:
        # set base wage to gov support level for nurture if person lost job this year without job gain
        jobLoss = Config.TP.getWhereList("(work_status==3) & (job_loss==1) & (job_gain==0)")
        p0_test = np.in1d(Persons[:,0], jobLoss, assume_unique=True)
        BaseWage[p0_test,0] = Config.Gov.support_dollars_mean
        p1_test = np.in1d(Persons[:,1], jobLoss, assume_unique=True)
        BaseWage[p1_test,1] = Config.Gov.support_dollars_mean
        
        Wages_Tokens, Wages_Dollars, Wage_Option, R_PostCBFS, Income_Increase = \
          Config.Ledda.wageOptions(self, Persons, BaseWage, WorkStatus, Membership, JobLoss, Year)   

      searchString20 = searchString.replace('membership', 'Membership[:,0]')
      searchString20 = searchString20.replace('work_status', 'WorkStatus[:,0]')
      searchString20 = searchString20.replace('job_gain', 'JobGain[:,0]')
      searchString21 = searchString20.replace('[:,0]', '[:,1]')

      searchString20 = "Wp0 = np.where(" + searchString20 + ")[0]"
      searchString21 = "Wp1 = np.where(" + searchString21 + ")[0]"
      exec(searchString20)
      exec(searchString21)

      # Wp*.size == many for caseNumber in [1,2], otherwise size == 1
      # [Wp0, Wp1] are row numbers for persons 1 and 2 in Persons, BaseWage, etc. arrays.  Thus, ii is
      # a row number, and jj is a column number (in [0,1]).
      for jj, Range in enumerate([Wp0, Wp1]):
        for ii in Range: 

          if caseNumber > 2:
            if (pool_tokens[Year] < (jobCostMult * Config.income_target_tokens[Year])) or \
              (pool_dollars[Year] < (jobCostMult * Config.income_target_dollars[Year])):
              Config.logRoot.debug("  *** pool has run dry ***")
              return

          if caseNumber in [5,7,9,11,13,15]:
            LEDDA_work_force = Config.TP.getWhereList("(work_status >= 2) & (membership==1)").size
            LEDDA_unemployed = Config.TP.getWhereList("((work_status==2) | (work_status==3)) & \
              (membership==1)").size
            urate = LEDDA_unemployed / float(LEDDA_work_force)
            if urate <= Config.LEDDA_structural_unemployment:
              Config.logRoot.debug("  *** structural unemployment level reached ***")
              return

          # no new jobs for NP (beyond peak level) once growth period is finished
          if (caseNumber in [5,6,7,8]) and (Year > Config.burn_in_period + Config.growth_period):
            W578 = Config.TP.getWhereList("(work_status==5) | (work_status==7) | (work_status==8)")
            Wnp = Config.TP.getWhereList("(work_status==4) | (work_status==6)")
            WF_total = float(W578.size + Wnp.size)
            fraction_NP = Wnp.size / WF_total
            if fraction_NP > Config.Org.fraction_WF_NP[Config.burn_in_period + Config.growth_period]:
              Config.logRoot.debug("\n   *** reached post-growth NP fraction of work force ***\n")
              return
    
          # rowID1 and rowID2 correspond to rows in Persons table.
          rowID1 = Persons[ii,jj]   # initial person in family
          kk = (jj+1)%2             # column for other person in family
          rowID2 = Persons[ii,kk]   # other person in family

          if caseNumber not in [1,2]:
            # Set WS temporarily to newWorkStatus for the one (or first) person in the family who is 
            # unemployed.  Failing to do so would result in benefits for the family being set to zero in 
            # Ledda.wageOptions(). 
            WorkStatus_old = WorkStatus[ii,jj]
            WorkStatus[ii,jj] = newWorkStatus 
 
            # set base wage to gov support level for nurture if person lost job this year without job 
            # gain
            jobLoss = Config.TP.getWhereList("(work_status==3) & (job_loss==1) & (job_gain==0)")
            p0_test = np.in1d(Persons[:,0], jobLoss, assume_unique=True)
            BaseWage[p0_test,0] = Config.Gov.support_dollars_mean
            p1_test = np.in1d(Persons[:,1], jobLoss, assume_unique=True)
            BaseWage[p1_test,1] = Config.Gov.support_dollars_mean
            
            # offer new wage for jobs for unemployed
            if caseNumber in [5,7,9,11,13,15]:
              # Make copy and set base wage at max(Year 0 base wage, gov support level).  If the wage
              # is set below the government support level, then in later years, after any government
              # support is given, if both persons choose option 2 they will see a reduction in family
              # income (they would have been better off with government support). 
              BaseWage_old = BaseWage[ii,jj]
              BaseWage[ii,jj] = max(BaseWage0[ii,jj], Config.Gov.support_dollars_mean)

            Wages_Tokens, Wages_Dollars, Wage_Option, R_PostCBFS, Income_Increase = \
              Config.Ledda.wageOptions(self, Persons, BaseWage, WorkStatus, Membership, JobLoss, Year)  
          

          # Offer jobs/nurture engagements one by one. Jobs can be rejected if there is no income 
          # increase

          if (Income_Increase[ii] == False) and (caseNumber not in [1,2]):
            Config.logRoot.debug(
              ("\n    *** job rejected. BaseWage new= ({0:,.9g}, {1:,.9g}), old= " +  \
              "({2:,.9g}, {3:,.9g}), Option= ({4:d}, {5:d}) ***").format(
               np.round(BaseWage[ii][jj],0).item(), 
               np.round(BaseWage[ii][kk],0).item(), 
               np.round(Config.TP.cols.base_wage[rowID1],0).item(), 
               np.round(Config.TP.cols.base_wage[rowID2],0).item(), 
               Wage_Option[ii][jj], 
               Wage_Option[ii][kk]))
            
            Config.logRoot.debug(("    old_option = ({0:,d}, {1:,d}), new postCBFS= " + \
              "({2:,.9g}, {3:,.9g}), old-postCBFS= ({4:,.9g}, {5:,.9g})\n").format(
               Config.TP_old.cols.wage_option[:][rowID1],
               Config.TP_old.cols.wage_option[:][rowID2],
               np.round(R_PostCBFS[ii][jj],0).item(), 
               np.round(R_PostCBFS[ii][kk],0).item(), 
               np.round(Config.TP_old.cols.R_postCBFS_total[:][rowID1],0).item(), 
               np.round(Config.TP_old.cols.R_postCBFS_total[:][rowID2],0).item()))            
            
            WorkStatus[ii,jj] = WorkStatus_old
            if caseNumber in [5,7,9,11,13,15]:
              BaseWage[ii,jj] = BaseWage_old
            continue
          
          if caseNumber > 2:
            if (jobCostMult * Wages_Tokens[ii][jj] > pool_tokens[Year]) or \
              (jobCostMult * Wages_Dollars[ii][jj]  > pool_dollars[Year]):
              
              WorkStatus[ii,jj] = WorkStatus_old
              if caseNumber in [5,7,9,11,13,15]:
                BaseWage[ii,jj] = BaseWage_old
                          
              Config.logRoot.debug("    *** not enough funds for this offer ***")
              # there might be other, lower paying jobs that could be offered
              continue        
          
          # remove old wage         
          if caseNumber in [6,8,10,12,14,16]:
              # test income sources and zero out current income based on old WS
              ws1 = Config.TP.cols.work_status[rowID1]
              if (ws1 == 4) or (ws1 == 6):
                assert np.allclose(Config.TP.cols.R_tokens[rowID1], \
                  Config.TP.cols.R_wages_NP_tokens[rowID1])
                assert np.allclose(Config.TP.cols.R_dollars[rowID1], \
                  Config.TP.cols.R_wages_NP_dollars[rowID1])
                Config.TP.cols.R_wages_NP_tokens[rowID1] = 0
                Config.TP.cols.R_wages_NP_dollars[rowID1] = 0
              
              if (ws1 == 5) or (ws1 == 7):
                assert np.allclose(Config.TP.cols.R_tokens[rowID1], \
                  Config.TP.cols.R_wages_SB_tokens[rowID1])
                assert np.allclose(Config.TP.cols.R_dollars[rowID1], \
                  Config.TP.cols.R_wages_SB_dollars[rowID1])
                Config.TP.cols.R_wages_SB_tokens[rowID1] = 0
                Config.TP.cols.R_wages_SB_dollars[rowID1] = 0
              
              if (ws1 == 8):
                assert np.allclose(Config.TP.cols.R_tokens[rowID1], \
                  Config.TP.cols.R_wages_PB_tokens[rowID1])
                assert np.allclose(Config.TP.cols.R_dollars[rowID1], \
                  Config.TP.cols.R_wages_PB_dollars[rowID1])
                Config.TP.cols.R_wages_PB_tokens[rowID1] = 0
                Config.TP.cols.R_wages_PB_dollars[rowID1] = 0

          # set new wage
          person_tokens[rowID1] = Wages_Tokens[ii][jj]
          
          if caseNumber in [1,2,3,4]:
            person_dollars[rowID1] = \
              max(0, Wages_Dollars[ii][jj] - Config.TP.cols.R_gov_support_dollars[rowID1])
          else:
            # set gov support to zero
            Config.TP.cols.R_gov_support_dollars[rowID1] = 0
            person_dollars[rowID1] = Wages_Dollars[ii][jj]

          Config.TP.cols.wage_option[rowID1] = Wage_Option[ii][jj]
          Config.TP.cols.work_status[rowID1] = newWorkStatus
          
          if caseNumber in [5,7,9,11,13,15]:
            # Only change base wage if unemployed if offered new job.  
            Config.TP.cols.base_wage[rowID1] = BaseWage[ii][jj]
          
          if caseNumber >=5:
            Config.TP.cols.number_job_gains[rowID1] += 1
            Config.TP.cols.job_gain[rowID1] = 1
          
          if jobsCreated is not None:
            jobsCreated[Year] += 1
            
          Config.TP.cols.R_postCBFS_total[rowID1] = R_PostCBFS[ii][jj]

          # make updates for other person in family pair ---------------------------------------
          if Config.TP.cols.wage_option[rowID2] != 0:
            
            Config.TP.cols.wage_option[rowID2] = Wage_Option[ii][kk]
            Config.TP.cols.R_postCBFS_total[rowID2] = R_PostCBFS[ii][kk]

            ws2 = WorkStatus[ii][kk]
            
            if (ws2 == 1) or (ws2 == 3):
              change_support_tokens = Wages_Tokens[ii][kk] - Config.TP.cols.R_CBFS_nurture_tokens[rowID2]
              new_support_dollars = \
                max(0, Wages_Dollars[ii][kk] - Config.TP.cols.R_gov_support_dollars[rowID2])
              change_support_dollars = \
                new_support_dollars - Config.TP.cols.R_CBFS_nurture_dollars[rowID2]
              
              if (np.allclose(change_support_tokens, 0, atol=.01)==False) or \
                (np.allclose(change_support_dollars, 0, atol=.01)==False):
                
                Config.logRoot.debug(("\nsubtracted {0:,.9g} T and {1:,.9g} D from nurture pools. " + \
                  "Balance is {2:,.9g} T and {3:,.9g} D").format(
                  np.round(change_support_tokens,0).item(), 
                  np.round(change_support_dollars,0).item(),
                  np.round(self.pool_nurture_tokens[Year],0).item(),
                  np.round(self.pool_nurture_dollars[Year],0).item()))
                
                Config.logRoot.debug(("  BaseWage new= ({0:,.9g}, {1:,.9g}), old= " +  \
                  "({2:,.9g}, {3:,.9g}), Option= ({4:d}, {5:d}),  caseNum= {4:d} ***").format(
                  np.round(BaseWage[ii][jj],0).item(), 
                  np.round(BaseWage[ii][kk],0).item(), 
                  np.round(Config.TP.cols.base_wage[rowID1],0).item(), 
                  np.round(Config.TP.cols.base_wage[rowID2],0).item(), 
                  Wage_Option[ii][jj], 
                  Wage_Option[ii][kk], caseNumber))               

                Config.logRoot.debug(("  tokens new= {0:,.9g}, old= " +  \
                  "{1:,.9g}, dollars new= {2:,.9g}, old=  {3:,.9g} ***\n").format(
                  np.round(Wages_Tokens[ii][kk],0).item(), 
                  np.round(Config.TP.cols.R_CBFS_nurture_tokens[rowID2],0).item(), 
                  np.round(Wages_Dollars[ii][kk],0).item(), 
                  np.round(Config.TP.cols.R_CBFS_nurture_dollars[rowID2],0).item()))  
              
              if caseNumber not in [1,2]:
                # Adjust pool for change in nurture support and record payments, for person 2.  
                self.pool_nurture_tokens[Year] -= change_support_tokens
                self.pool_nurture_dollars[Year] -= change_support_dollars
                self.P_nurture_tokens[Year] += change_support_tokens
                self.P_nurture_dollars[Year] += change_support_dollars

              Config.TP.cols.R_CBFS_nurture_tokens[rowID2] = Wages_Tokens[ii][kk]
              Config.TP.cols.R_CBFS_nurture_dollars[rowID2] = new_support_dollars

            elif (ws2 == 4) or (ws2 == 6):
              change_support_tokens = Wages_Tokens[ii][kk] - Config.TP.cols.R_wages_NP_tokens[rowID2]
              change_support_dollars = Wages_Dollars[ii][kk] - Config.TP.cols.R_wages_NP_dollars[rowID2]

              if (np.allclose(change_support_tokens, 0, atol=.01)==False) or \
                (np.allclose(change_support_dollars, 0, atol=.01)==False):
                
                Config.logRoot.debug(("\nsubtracted {0:,.9g} T and {1:,.9g} D from NP pools. " + \
                  "Balance is {2:,.9g} T and {3:,.9g} D,  caseNum= {4:d}").format(
                  np.round(change_support_tokens,0).item(), 
                  np.round(change_support_dollars,0).item(),
                  np.round(self.pool_donation_NP_tokens[Year],0).item(),
                  np.round(self.pool_donation_NP_dollars[Year],0).item(), caseNumber))
                
                Config.logRoot.debug(("  BaseWage new= ({0:,.9g}, {1:,.9g}), old= " +  \
                  "({2:,.9g}, {3:,.9g}), Option= ({4:d}, {5:d}) ***").format(
                  np.round(BaseWage[ii][jj],0).item(), 
                  np.round(BaseWage[ii][kk],0).item(), 
                  np.round(Config.TP.cols.base_wage[rowID1],0).item(), 
                  np.round(Config.TP.cols.base_wage[rowID2],0).item(), 
                  Wage_Option[ii][jj], 
                  Wage_Option[ii][kk]))               

                Config.logRoot.debug(("  tokens new= {0:,.9g}, old= " +  \
                  "{1:,.9g}, dollars new= {2:,.9g}, old=  {3:,.9g} ***\n").format(
                  np.round(Wages_Tokens[ii][kk],0).item(), 
                  np.round(Config.TP.cols.R_wages_NP_tokens[rowID2],0).item(), 
                  np.round(Wages_Dollars[ii][kk],0).item(), 
                  np.round(Config.TP.cols.R_wages_NP_dollars[rowID2],0).item()))      

              if (ws2 == 6):
                if caseNumber >-10:
                  # Adjust pool for change in donation_NP support and record payments, for person 2.  
                  self.pool_donation_NP_tokens[Year] -= change_support_tokens
                  self.pool_donation_NP_dollars[Year] -= change_support_dollars
                  self.P_donation_NP_tokens[Year] += change_support_tokens
                  self.P_donation_NP_dollars[Year] += change_support_dollars
                    
              Config.TP.cols.R_wages_NP_tokens[rowID2] = Wages_Tokens[ii][kk]
              Config.TP.cols.R_wages_NP_dollars[rowID2] = Wages_Dollars[ii][kk]

            # Adjustments of pools for other WS are not needed, as organizations pay wages later in the 
            # year and wages for these jobs are not covered by the CBFS.
            elif (ws2 == 5) or (ws2==7):
              Config.TP.cols.R_wages_SB_tokens[rowID2] = Wages_Tokens[ii][kk]
              Config.TP.cols.R_wages_SB_dollars[rowID2] = Wages_Dollars[ii][kk]
            
            elif (ws2 == 8):
              Config.TP.cols.R_wages_PB_tokens[rowID2] = Wages_Tokens[ii][kk]
              Config.TP.cols.R_wages_PB_dollars[rowID2] = Wages_Dollars[ii][kk]
            
            else:
              assert False

          if caseNumber in [5,7,9,11,13,15]:
            # add back to pool any nurture support given, and subtract from recorded payment
            self.pool_nurture_tokens[Year] += Config.TP.cols.R_CBFS_nurture_tokens[rowID1]
            self.pool_nurture_dollars[Year] += Config.TP.cols.R_CBFS_nurture_dollars[rowID1]
            self.P_nurture_tokens[Year] -= Config.TP.cols.R_CBFS_nurture_tokens[rowID1]
            self.P_nurture_dollars[Year] -= Config.TP.cols.R_CBFS_nurture_dollars[rowID1]          
            
            # update persons table to remove nurture support
            Config.TP.cols.R_CBFS_nurture_tokens[rowID1] = 0
            Config.TP.cols.R_CBFS_nurture_dollars[rowID1] = 0
          
          # update Persons table
          for row in [rowID1, rowID2]:
            Config.TP.cols.R_tokens[row] = Config.TP.cols.R_wages_SB_tokens[row] + \
              Config.TP.cols.R_wages_PB_tokens[row] + Config.TP.cols.R_wages_NP_tokens[row] + \
              Config.TP.cols.R_CBFS_nurture_tokens[row] 
            
            Config.TP.cols.R_dollars[row] = Config.TP.cols.R_wages_SB_dollars[row] + \
              Config.TP.cols.R_wages_PB_dollars[row] + Config.TP.cols.R_wages_NP_dollars[row] + \
              Config.TP.cols.R_CBFS_nurture_dollars[row] + Config.TP.cols.R_gov_support_dollars[row] 
            
            Config.TP.cols.R_total[row] = Config.TP.cols.R_tokens[row] + Config.TP.cols.R_dollars[row]

          # adjust pool and record payments, for person 1
          pool_tokens[Year] -= jobCostMult * person_tokens[rowID1]
          pool_dollars[Year] -= jobCostMult * person_dollars[rowID1]
          
          paid_tokens[Year] += jobCostMult * person_tokens[rowID1]
          paid_dollars[Year] += jobCostMult * person_dollars[rowID1]   

          if (paid_tokens[Year] > 0):
            Config.logRoot.debug((caseTitle + ": T{0:>10,.4G}, ${1:>10,.4G}, TS pool= {2:>4.3F}," + \
              "  TS paid= {3:>4.3F}").format(
              pool_tokens[Year], 
              pool_dollars[Year], 
              pool_tokens[Year] / \
              (pool_tokens[Year] + pool_dollars[Year]), 
              paid_tokens[Year] / \
              (paid_tokens[Year] + paid_dollars[Year])))
          
      if caseNumber <= 2:
        # loop runs only once, because all Persons are handled as a group
        break

    Wii = Config.TP.getWhereList("(wage_option > 0)")
    assert np.all(Config.TP.cols.work_status[:][Wii] != 0)
    assert np.all(Config.TP.cols.work_status[:][Wii] != 2)
    assert np.all(Config.TP.cols.membership[:][Wii] == 1)

                  

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizePayments(self, Year):
    """
    
    Summarize CBFS payments for tokens, dollars, and tokens + dollars.
    
    """
    
    self.P_tokens[Year] = self.P_loan_SB_tokens[Year] + self.P_loan_PB_tokens[Year] + \
      self.P_loan_NP_tokens[Year] + self.P_subsidy_SB_tokens[Year] + self.P_subsidy_PB_tokens[Year] + \
      self.P_nurture_tokens[Year] + self.P_donation_NP_tokens[Year]

    self.P_dollars[Year] = self.P_loan_SB_dollars[Year] + self.P_loan_PB_dollars[Year] + \
      self.P_loan_NP_dollars[Year] + self.P_subsidy_SB_dollars[Year] + \
      self.P_subsidy_PB_dollars[Year] + self.P_nurture_dollars[Year] + \
      self.P_donation_NP_dollars[Year]
    
    self.P_total[Year] = self.P_tokens[Year] + self.P_dollars[Year]
    
    if self.P_total[Year] != 0:
      self.P_token_share_CBFS[Year] = self.P_tokens[Year] / self.P_total[Year]

      self.nurture_fraction_P[Year] = self.P_nurture_dollars[Year] / self.R_nurture_dollars[Year]
    
    # loan totals
    self.P_loan_tokens[Year] = self.P_loan_SB_tokens[Year] + self.P_loan_PB_tokens[Year] + \
      self.P_loan_NP_tokens[Year]
    self.P_loan_dollars[Year] = self.P_loan_SB_dollars[Year] + self.P_loan_PB_dollars[Year] + \
      self.P_loan_NP_dollars[Year]
    self.P_loan_total[Year] = self.P_loan_tokens[Year] + self.P_loan_dollars[Year]

    self.loan_outstd_tokens[Year] = self.P_loan_tokens.sum() - self.R_loan_prin_tokens.sum()
    self.loan_outstd_dollars[Year] = self.P_loan_dollars.sum() - self.R_loan_prin_dollars.sum()
    self.loan_outstd_total[Year] = self.loan_outstd_tokens[Year] + self.loan_outstd_dollars[Year]

    # pools
    self.pool_loan_tokens[Year] = self.pool_loan_SB_tokens[Year] + self.pool_loan_PB_tokens[Year] + \
      self.pool_loan_NP_tokens[Year]
    
    self.pool_loan_dollars[Year] = self.pool_loan_SB_dollars[Year] + self.pool_loan_PB_dollars[Year] + \
      self.pool_loan_NP_dollars[Year]
    
    self.pool_loan_total[Year] = self.pool_loan_tokens[Year] + self.pool_loan_dollars[Year]

    self.pool_tokens[Year] = self.pool_loan_tokens[Year]  + self.pool_subsidy_SB_tokens[Year] + \
      self.pool_subsidy_PB_tokens[Year] + self.pool_nurture_tokens[Year] + \
      self.pool_donation_NP_tokens[Year] 
    
    self.pool_dollars[Year] = self.pool_loan_dollars[Year] + self.pool_subsidy_SB_dollars[Year] + \
      self.pool_subsidy_PB_dollars[Year] + self.pool_nurture_dollars[Year] + \
      self.pool_donation_NP_dollars[Year]    

    self.pool_total[Year] = self.pool_tokens[Year] + self.pool_dollars[Year]
    
    if self.pool_dollars[Year] > 0:
      self.pool_token_share[Year] = self.pool_tokens[Year] / \
        (self.pool_tokens[Year] + self.pool_dollars[Year])

    if self.P_loan_SB_tokens[Year] > 0:
      self.P_TS_loan_SB[Year] = self.P_loan_SB_tokens[Year] / \
        (self.P_loan_SB_tokens[Year] + self.P_loan_SB_dollars[Year])

    if self.P_loan_PB_tokens[Year] > 0:      
      self.P_TS_loan_PB[Year] = self.P_loan_PB_tokens[Year] / \
        (self.P_loan_PB_tokens[Year] + self.P_loan_PB_dollars[Year]) 

    if self.P_loan_NP_tokens[Year] > 0:      
      self.P_TS_loan_NP[Year] = self.P_loan_NP_tokens[Year] / \
        (self.P_loan_NP_tokens[Year] + self.P_loan_NP_dollars[Year])

    if self.P_subsidy_SB_tokens[Year] > 0:      
      self.P_TS_subsidy_SB[Year] = self.P_subsidy_SB_tokens[Year] / \
        (self.P_subsidy_SB_tokens[Year] + self.P_subsidy_SB_dollars[Year])

    if self.P_subsidy_PB_tokens[Year] > 0:      
      self.P_TS_subsidy_PB[Year] = self.P_subsidy_PB_tokens[Year] / \
        (self.P_subsidy_PB_tokens[Year] + self.P_subsidy_PB_dollars[Year])

    if self.P_donation_NP_tokens[Year] > 0:       
      self.P_TS_donation_NP[Year] = self.P_donation_NP_tokens[Year] / \
        (self.P_donation_NP_tokens[Year] + self.P_donation_NP_dollars[Year])
      
    if self.P_nurture_tokens[Year] > 0:
      self.P_TS_nurture[Year] = self.P_nurture_tokens[Year] / \
        (self.P_nurture_tokens[Year] + self.P_nurture_dollars[Year])

    # checks on sums
    assert np.allclose(self.R_tokens[Year], self.P_tokens[Year] + \
      (self.pool_tokens[Year] - self.pool_tokens[Year-1]), atol=1)
      
    assert np.allclose(self.R_dollars[Year], self.P_dollars[Year] + \
      (self.pool_dollars[Year] - self.pool_dollars[Year-1]), atol=1)
      
    assert np.allclose((self.R_tokens.sum() - self.P_tokens.sum()), self.pool_tokens[Year], atol=.01)     
    assert np.allclose((self.R_dollars.sum() - self.P_dollars.sum()), self.pool_dollars[Year], atol=.01)      
    assert np.allclose((self.R_total.sum() - self.P_total.sum()), self.pool_total[Year], atol=.01)    
    
    # Checks for loans using previous year TP contributions. Use TP_old.
    persons_loan_tokens_old = Config.TP_old.cols.P_CBFS_loan_SB_tokens[:].sum() + \
      Config.TP_old.cols.P_CBFS_loan_PB_tokens[:].sum() + \
      Config.TP_old.cols.P_CBFS_loan_NP_tokens[:].sum()
    delta_pool_loan_tokens = self.pool_loan_tokens[Year] - self.pool_loan_tokens[Year-1]
    delta_outstd_tokens = self.loan_outstd_tokens[Year] - self.loan_outstd_tokens[Year-1]
    assert np.allclose(delta_pool_loan_tokens, persons_loan_tokens_old - self.P_loan_tokens[Year] + \
      self.R_loan_prin_tokens[Year], atol=.01)
    assert np.allclose(delta_pool_loan_tokens, persons_loan_tokens_old - delta_outstd_tokens, atol=.01)

    persons_loan_dollars_old = Config.TP_old.cols.P_CBFS_loan_SB_dollars[:].sum() + \
      Config.TP_old.cols.P_CBFS_loan_PB_dollars[:].sum() + \
      Config.TP_old.cols.P_CBFS_loan_NP_dollars[:].sum()
    delta_pool_loan_dollars = self.pool_loan_dollars[Year] - self.pool_loan_dollars[Year-1]
    delta_outstd_dollars = self.loan_outstd_dollars[Year] - self.loan_outstd_dollars[Year-1]
    assert np.allclose(delta_pool_loan_dollars, persons_loan_dollars_old - self.P_loan_dollars[Year] + \
      self.R_loan_prin_dollars[Year], atol=.01)
    assert np.allclose(
      delta_pool_loan_dollars, persons_loan_dollars_old - delta_outstd_dollars, atol=.01)
    
    # full pool
    person_tokens_old = Config.TP_old.cols.P_CBFS_tokens[:].sum()
    delta_pool_tokens = self.pool_tokens[Year] - self.pool_tokens[Year-1]
    assert np.allclose(delta_pool_tokens, person_tokens_old - self.P_tokens[Year] + \
      self.R_loan_prin_tokens[Year], atol=.01)

    person_dollars_old = Config.TP_old.cols.P_CBFS_dollars[:].sum()
    delta_pool_dollars = self.pool_dollars[Year] - self.pool_dollars[Year-1]
    assert np.allclose(delta_pool_dollars, person_dollars_old - self.P_dollars[Year] + \
      self.R_loan_prin_dollars[Year], atol=.01)
    
    
    # checks on pool sums using Persons object
    assert np.allclose(self.pool_loan_tokens[Year], Config.Persons.P_CBFS_loan_tokens.sum() - 
      self.P_loan_tokens.sum() + self.R_loan_prin_tokens.sum(), atol=.01)
    assert np.allclose(self.pool_loan_dollars[Year], Config.Persons.P_CBFS_loan_dollars.sum() - \
      self.P_loan_dollars.sum() + self.R_loan_prin_dollars.sum(), atol=.01)
    assert np.allclose(self.pool_loan_total[Year], Config.Persons.P_CBFS_loan_total.sum() - \
      self.P_loan_total.sum() + self.R_loan_prin_total.sum(), atol=.01)
      

      
