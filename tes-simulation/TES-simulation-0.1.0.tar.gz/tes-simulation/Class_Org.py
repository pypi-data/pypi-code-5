
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# ORGANIZATIONS class
# ===========================================================================================


class ORGANIZATIONS(object):
  """
  
  Class for the Organizations object.  Some information is subset for NPs, SBs, and PBs.  Explanations of
  some variable names are given below (see Initialize.getHDF5() and Config for more information).  
  
  created_tokens                = The annual amount of tokens created to pay expenses (wages and loan 
                                    principal).
  deficit_dollars               = The dollar deficit that would be seen if dollars were not obtained 
                                    through alteration of trade balance with other counties or some other
                                    means (increased bank lending, increased velocity of currency, 
                                    increased grants or other forms of government spending, etc.).  In 
                                    the simulation, any deficit is eliminated via alteration of the trade
                                    balance.  The trade adjustment is intended to equalize the per capita
                                    dollar supply among counties, rather than provide the LEDDA county 
                                    with a relative abundance.  At the end of the simulation, when no
                                    new tokens are created and mean family income for LEDDA members has 
                                    approached the national mean, the trade adjustment should make up 
                                    only for greater govenment spending in non-LEDDA counties. 
  share_LEDDA_receipts_token    = The share of organization receipts that occur as tokens vs dollars.
  dollar_token_deficit_ratio    = The ratio between the volume of token creation and the dollar deficit 
                                    of organizations (dollar deficit prior to trade adjustment). 
  wage_increase_*_cumulative    = The total, cumulative increase in wages paid.
  import_dollar_revenue         = The amount of dollars imported via trade (sales to outside counties).
  export_dollar_revenue         = The amount of dollars exported via trade (purchases from outside 
                                    counties.
  import_fraction_receipts      = Import of dollar revenue as a fraction of total receipts.  This is held
                                  fixed in the simulation.
  export_fraction_receipts      = Export of dollar revenue as a fraction of total receipts. This is 
                                    allowed to vary in order to eliminate any dollar deficit.
  import_export_ratio           = The ratio between import_fraction_receipts and export_fraction_receipts
  fraction_WF_*                 = These variables pertain to the fraction of the work force is employed 
                                    by SBs, PBs, and NPs.  
  ratio_R_NP_CBFS_P_NP_ws6      = The ratio of NP donation funds that organizations received from the 
                                    CBFS to the total NP wages that organizations pay to employees.
  deficit_fraction_LEDDA_dollar_receipts  = The dollar deficit as a fraction of receipts of LEDDA 
                                              organizations.  Organizations are not divided into LEDDA 
                                              and non-LEDDA, so the fraction of organizations that are
                                              LEDDA members is estimated from the fraction of persons
                                              in the county who receive tokens.
  fraction_outstd_loans_wage_increase     = The ratio of annual change in outstanding balance of CBFS 
                                              loans owed by organizations to the annual change in 
                                              total wages.  This variable gives some indication of the 
                                              volume of CBFS lending relative to the total need for 
                                              lending. It can be compared to a similar ratio for the 
                                              national dollar economy.


  """

  
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "Org"

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    
    
    # ----------------------- unspent currency and misc. -----
    for Type in [
      'created_tokens', 'deficit_dollars', 
      'share_LEDDA_receipts_token', 'dollar_token_deficit_ratio',
      'wage_increase_tokens_cumulative', 'wage_increase_dollars_cumulative', 
      'wage_increase_total_cumulative', 'import_dollar_revenue', 'export_dollar_revenue',
      'import_fraction_receipts', 'export_fraction_receipts', 'import_export_ratio',
      'deficit_fraction_LEDDA_dollar_receipts', 'fraction_outstd_loans_wage_increase',
      'ratio_R_NP_CBFS_P_NP_ws6',
      'fraction_WF_SB', 'fraction_WF_PB', 'fraction_WF_NP']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))
      

    # ----------------------- receipts of organizations -----------------------

    # ------------------- tokens -------------------
    # tokens, raw
    for Type in [
      'R_CBFS_loan_SB_tokens', 'R_CBFS_loan_PB_tokens', 'R_CBFS_loan_NP_tokens', 
      'R_CBFS_subsidy_SB_tokens', 'R_CBFS_subsidy_PB_tokens',
      'R_CBFS_donation_NP_tokens',
      'R_spending_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  

    # tokens, summaries
    for Type in [
      'R_CBFS_loan_tokens', 'R_CBFS_subsidy_tokens', 
      'R_CBFS_SB_tokens', 'R_CBFS_PB_tokens', 'R_CBFS_NP_tokens',
      'R_CBFS_tokens',
      'R_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))   

    # ------------------- dollars -------------------
    # dollars, raw
    for Type in [
      'R_CBFS_loan_SB_dollars', 'R_CBFS_loan_PB_dollars', 'R_CBFS_loan_NP_dollars', 
      'R_CBFS_subsidy_SB_dollars', 'R_CBFS_subsidy_PB_dollars',         
      'R_CBFS_donation_NP_dollars', 
      'R_spending_dollars', 
      'R_donation_NP_dollars',
      'R_gov_contract_SB_dollars', 'R_gov_contract_PB_dollars', 'R_gov_contract_NP_dollars',
      'R_gov_subsidy_SB_dollars', 'R_gov_subsidy_PB_dollars', 
      'R_gov_grant_NP_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))   

    # dollars, summaries
    for Type in [      
      'R_CBFS_loan_dollars', 'R_CBFS_subsidy_dollars', 
      'R_CBFS_SB_dollars', 'R_CBFS_PB_dollars', 'R_CBFS_NP_dollars',
      'R_CBFS_dollars',
      'R_SB_dollars', 'R_PB_dollars', 'R_NP_dollars', 
      'R_gov_contract_dollars', 'R_gov_subsidy_dollars', 
      'R_gov_SB_dollars', 'R_gov_PB_dollars', 'R_gov_NP_dollars', 
      'R_gov_dollars',
      'R_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  
      
    # ------------------- tokens + dollars -------------------
    for Type in [           
      'R_CBFS_loan_SB_total', 'R_CBFS_loan_PB_total', 'R_CBFS_loan_NP_total',
      'R_CBFS_donation_NP_total', 'R_CBFS_subsidy_total', 'R_CBFS_loan_total',   
      'R_CBFS_total', 
      'R_spending_total', 
      'R_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  
        

    # ----------------------- payments of organizations -----------------------
    
    # ------------------- tokens -------------------
    # tokens, raw
    for Type in [
      'P_wages_SB_tokens', 'P_wages_PB_tokens', 'P_wages_NP_tokens', 
      'P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 'P_CBFS_loan_NP_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  
      
    # tokens, summaries
    for Type in [
      'P_wages_tokens', 'P_CBFS_loan_tokens', 
      'P_SB_tokens', 'P_PB_tokens', 'P_NP_tokens', 
      'P_tokens']: 
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  

    # ------------------- dollars -------------------
    # dollars, raw
    for Type in [
      'P_wages_SB_dollars', 'P_wages_PB_dollars', 'P_wages_NP_dollars',
      'P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 'P_CBFS_loan_NP_dollars']: 
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  
       
    # dollars, summaries
    for Type in [    
       'P_wages_dollars', 'P_CBFS_loan_dollars', 
       'P_SB_dollars', 'P_PB_dollars', 'P_NP_dollars', 
       'P_dollars']: 
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  
      
    # ------------------- tokens + dollars -------------------
    for Type in [
      'P_wages_SB_total', 'P_wages_PB_total', 'P_wages_NP_total',
      'P_wages_total', 
      'P_CBFS_loan_SB_total', 'P_CBFS_loan_PB_total', 'P_CBFS_loan_NP_total',
      'P_CBFS_loan_total',       
      'P_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))

    
    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
    
    self.graphGroup = {}
      
    self.graphGroup['R+CBFS+tokens+raw'] = ['R_CBFS_loan_SB_tokens', 'R_CBFS_loan_PB_tokens', 
      'R_CBFS_loan_NP_tokens', 'R_CBFS_subsidy_SB_tokens', 'R_CBFS_subsidy_PB_tokens', 
      'R_CBFS_donation_NP_tokens']
    self.graphGroup['R+CBFS+token+type'] = ['R_CBFS_loan_tokens', 'R_CBFS_subsidy_tokens', 
      'R_CBFS_SB_tokens', 'R_CBFS_PB_tokens', 'R_CBFS_NP_tokens', 'R_CBFS_tokens']

    self.graphGroup['R+CBFS+dollars+raw'] = ['R_CBFS_loan_SB_dollars', 'R_CBFS_loan_PB_dollars', 
      'R_CBFS_loan_NP_dollars', 'R_CBFS_subsidy_SB_dollars', 'R_CBFS_subsidy_PB_dollars', 
      'R_CBFS_donation_NP_dollars']
    self.graphGroup['R+CBFS+dollars+type'] = ['R_CBFS_loan_dollars', 'R_CBFS_subsidy_dollars', 
      'R_CBFS_SB_dollars', 'R_CBFS_PB_dollars', 'R_CBFS_NP_dollars', 'R_CBFS_dollars']
    self.graphGroup['R+org+dollars'] = ['R_SB_dollars', 'R_PB_dollars', 'R_NP_dollars']    

    self.graphGroup['R+gov'] = ['R_gov_contract_SB_dollars', 'R_gov_contract_PB_dollars', 
      'R_gov_contract_NP_dollars', 'R_gov_subsidy_SB_dollars', 'R_gov_subsidy_PB_dollars', 
      'R_gov_grant_NP_dollars', 'R_gov_dollars']
    self.graphGroup['R+gov+org'] = ['R_gov_SB_dollars', 'R_gov_PB_dollars', 'R_gov_NP_dollars'] 
    self.graphGroup['R+gov+sum'] = ['R_gov_contract_dollars', 'R_gov_subsidy_dollars']
      
    self.graphGroup['R+CBFS+total'] = ['R_CBFS_loan_SB_total', 'R_CBFS_loan_PB_total', 
      'R_CBFS_loan_NP_total', 'R_CBFS_donation_NP_total', 'R_CBFS_subsidy_total', 'R_CBFS_loan_total',   
      'R_CBFS_total']
    self.graphGroup['spending'] = ['R_spending_tokens', 'R_spending_dollars', 'R_spending_total']
    self.graphGroup['R+total'] = ['R_tokens', 'R_dollars', 'R_total']

    self.graphGroup['P+wages+tokens+org'] = ['P_wages_SB_tokens', 'P_wages_PB_tokens', 'P_wages_NP_tokens']
    self.graphGroup['P+wages+dollars+org'] = ['P_wages_SB_dollars', 'P_wages_PB_dollars', 
      'P_wages_NP_dollars']    
    
    self.graphGroup['P+CBFS+tokens'] = ['P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 
      'P_CBFS_loan_NP_tokens', 'P_CBFS_loan_tokens']
    self.graphGroup['P+CBFS+dollars'] = ['P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 
      'P_CBFS_loan_NP_dollars', 'P_CBFS_loan_dollars' ]
    self.graphGroup['P+wages+total'] = ['P_wages_tokens', 'P_wages_dollars', 'P_wages_total']

    self.graphGroup['P+CBFS+total'] = ['P_CBFS_loan_SB_total', 'P_CBFS_loan_PB_total', 
      'P_CBFS_loan_NP_total', 'P_CBFS_loan_total'] 

    self.graphGroup['P+token+sum+org'] = ['P_SB_tokens', 'P_PB_tokens', 'P_NP_tokens']
    self.graphGroup['P+dollar+sum+org'] = ['P_SB_dollars', 'P_PB_dollars', 'P_NP_dollars']  
    self.graphGroup['P+total'] = ['P_tokens', 'P_dollars', 'P_total']  
    self.graphGroup['P+wages+total+org'] = ['P_wages_SB_total', 'P_wages_PB_total', 'P_wages_NP_total']

    self.graphGroup['wage+increase'] = ['wage_increase_tokens_cumulative', 
      'wage_increase_dollars_cumulative', 'wage_increase_total_cumulative']
      
    self.graphGroup['import+export+revenue'] = ['import_dollar_revenue', 'export_dollar_revenue']
    self.graphGroup['import+export+fraction'] = ['import_fraction_receipts', 'export_fraction_receipts']
    self.graphGroup['created+deficit'] = ['created_tokens', 'deficit_dollars']
    
    self.graphGroup['fraction+WF'] = ['fraction_WF_SB', 'fraction_WF_PB', 'fraction_WF_NP']

      
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def raiseWages(self, Year):

    """
    
    Raise wages according to income target schedule (Wage Option 1) or token bonus (Wage Option 2). Base 
    wage does not change.
    
    """
    
    P0 = Config.TP.getWhereList("(membership==1) & (work_status >= 4)")
    Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0 = \
      Config.Persons.getFamilyData(P0) 

    # get new wages, etc.
    Wages_Tokens, Wages_Dollars, Wage_Option, R_PostCBFS, Income_Increase = \
      Config.Ledda.wageOptions(self, Persons, BaseWage, WorkStatus, Membership, JobLoss, Year)

    Wp0 = np.where((Membership[:,0] == 1) & (WorkStatus[:,0]>=4))[0]
    Wp1 = np.where((Membership[:,1] == 1) & (WorkStatus[:,1]>=4))[0]
    
    # Wp*.size == many 
    # [Wp0, Wp1] are row numbers for persons 1 and 2 in Persons, BaseWage, etc. arrays.  Thus, ii is
    # a row number, and jj is a column number (in [0,1]).    
    for jj, Range in enumerate([Wp0, Wp1]):
      for ii in Range: 
        
        # rowID1 and rowID2 correspond to rows in Persons table.
        rowID1 = Persons[ii,jj]   # initial person in family
        kk = (jj+1)%2             # column for other person in family
        rowID2 = Persons[ii,kk]   # other person in family
        
        ws1 = WorkStatus[ii][jj]
        ws2 = WorkStatus[ii][kk]

        # set new data for person 1
        if (ws1 == 4) or (ws1 == 6): 
          person_tokens = Config.TP.cols.R_wages_NP_tokens
          person_dollars = Config.TP.cols.R_wages_NP_dollars
        if (ws1 == 5) or (ws1 == 7):
          person_tokens = Config.TP.cols.R_wages_SB_tokens
          person_dollars = Config.TP.cols.R_wages_SB_dollars          
        if (ws1 == 8):
          person_tokens = Config.TP.cols.R_wages_PB_tokens
          person_dollars = Config.TP.cols.R_wages_PB_dollars
        
        person_tokens[rowID1] = Wages_Tokens[ii][jj]
        person_dollars[rowID1] = Wages_Dollars[ii][jj]
        Config.TP.cols.wage_option[rowID1] = Wage_Option[ii][jj]
        Config.TP.cols.R_postCBFS_total[rowID1] = R_PostCBFS[ii][jj]

        # set new data for person 2
        if Config.TP.cols.wage_option[rowID2] != 0:
          if (ws2 == 1) or (ws2 == 3): 
            person_tokens = Config.TP.cols.R_CBFS_nurture_tokens
            person_dollars = Config.TP.cols.R_CBFS_nurture_dollars          
          if (ws2 == 4) or (ws2 == 6): 
            person_tokens = Config.TP.cols.R_wages_NP_tokens
            person_dollars = Config.TP.cols.R_wages_NP_dollars
          if (ws2 == 5) or (ws2 == 7):
            person_tokens = Config.TP.cols.R_wages_SB_tokens
            person_dollars = Config.TP.cols.R_wages_SB_dollars          
          if (ws2 == 8):
            person_tokens = Config.TP.cols.R_wages_PB_tokens
            person_dollars = Config.TP.cols.R_wages_PB_dollars          
 
          person_tokens[rowID2] = Wages_Tokens[ii][kk]
          person_dollars[rowID2] = Wages_Dollars[ii][kk]
          Config.TP.cols.wage_option[rowID2] = Wage_Option[ii][kk]
          Config.TP.cols.R_postCBFS_total[rowID2] = R_PostCBFS[ii][kk]
          
        # update Persons table
        for row in [rowID1, rowID2]:
          Config.TP.cols.R_tokens[row] = Config.TP.cols.R_wages_SB_tokens[row] + \
            Config.TP.cols.R_wages_PB_tokens[row] + Config.TP.cols.R_wages_NP_tokens[row] + \
            Config.TP.cols.R_CBFS_nurture_tokens[row] 
          
          Config.TP.cols.R_dollars[row] = Config.TP.cols.R_wages_SB_dollars[row] + \
            Config.TP.cols.R_wages_PB_dollars[row] + Config.TP.cols.R_wages_NP_dollars[row] + \
            Config.TP.cols.R_CBFS_nurture_dollars[row] + Config.TP.cols.R_gov_support_dollars[row] 
          
          Config.TP.cols.R_total[row] = Config.TP.cols.R_tokens[row] + Config.TP.cols.R_dollars[row]

    # checks
    W102 = Config.TP.getWhereList("(membership==1) & (work_status >=4) & (wage_option>0)")
    W102b = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
      "& (job_loss==1) & (job_gain==0)")
    W102d = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + 
      "& (R_postCBFS_total < base_wage) & (wage_option==2) & (job_loss!=1)")
    W102e = Config.TP.getWhereList("((membership==0) | (work_status==0) | (work_status==2)) " + \
      "& (R_tokens>0)")
    W102f = Config.TP.getWhereList("(wage_option==0) & (R_tokens>0)")

    assert np.all(Config.TP.cols.R_tokens[:][W102] > 0)
    assert np.all(Config.TP.cols.R_gov_support_dollars[:][W102b] > 0)
    assert W102d.size == 0 
    assert W102e.size == 0 
    assert W102f.size == 0 


    Wii = Config.TP.getWhereList("(wage_option > 0)")
    assert np.all(Config.TP.cols.work_status[:][Wii] != 0)
    assert np.all(Config.TP.cols.work_status[:][Wii] != 2)
    assert np.all(Config.TP.cols.membership[:][Wii] == 1)

    Config.logRoot.info("\n***** Wage Increase (in Org.raiseWages()):")
    
    Config.logRoot.info("  increase in SB tokens = {0:,.9g}".format(
      np.round((Config.TP.cols.R_wages_SB_tokens[:].sum() - \
      Config.TP_old.cols.R_wages_SB_tokens[:].sum()),0).item())) 
    
    Config.logRoot.info("  increase in SB dollars = {0:,.9g}".format(
      np.round((Config.TP.cols.R_wages_SB_dollars[:].sum() - \
      Config.TP_old.cols.R_wages_SB_dollars[:].sum()),0).item()))

    Config.logRoot.info("\n  increase in PB tokens = {0:,.9g}".format(
      np.round((Config.TP.cols.R_wages_PB_tokens[:].sum() - \
      Config.TP_old.cols.R_wages_PB_tokens[:].sum()),0).item()))         
    
    Config.logRoot.info("  increase in PB dollars = {0:,.9g}".format(
      np.round((Config.TP.cols.R_wages_PB_dollars[:].sum() - \
      Config.TP_old.cols.R_wages_PB_dollars[:].sum()),0).item()))

    Config.logRoot.info("\n  increase in NP tokens = {0:,.9g}".format(
      np.round((Config.TP.cols.R_wages_NP_tokens[:].sum() - \
      Config.TP_old.cols.R_wages_NP_tokens[:].sum()),0).item()))       
    
    Config.logRoot.info("  increase in NP dollars = {0:,.9g}\n".format(
      np.round((Config.TP.cols.R_wages_NP_dollars[:].sum() - \
      Config.TP_old.cols.R_wages_NP_dollars[:].sum()),0).item()))
    


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizeReceipts(self, Year):
    """
    
    Summarize receipts for tokens, dollars, and tokens + dollars.  Receipts from rest of counties
    is not included here.  These receipts are handled in summarizePayments()
    
    """
    # ----------------------- receipts of organizations -----------------------
    
    # raw
    # receive CBFS funding from current year
    self.R_CBFS_loan_SB_tokens[Year] = Config.Cbfs.P_loan_SB_tokens[Year]
    self.R_CBFS_loan_PB_tokens[Year] = Config.Cbfs.P_loan_PB_tokens[Year]
    self.R_CBFS_loan_NP_tokens[Year] = Config.Cbfs.P_loan_NP_tokens[Year]
    
    self.R_CBFS_subsidy_SB_tokens[Year] = Config.Cbfs.P_subsidy_SB_tokens[Year]
    self.R_CBFS_subsidy_PB_tokens[Year] = Config.Cbfs.P_subsidy_PB_tokens[Year]
    self.R_CBFS_donation_NP_tokens[Year] = Config.Cbfs.P_donation_NP_tokens[Year]

    self.R_CBFS_loan_SB_dollars[Year] = Config.Cbfs.P_loan_SB_dollars[Year]
    self.R_CBFS_loan_PB_dollars[Year] = Config.Cbfs.P_loan_PB_dollars[Year]
    self.R_CBFS_loan_NP_dollars[Year] = Config.Cbfs.P_loan_NP_dollars[Year]
    
    self.R_CBFS_subsidy_SB_dollars[Year] = Config.Cbfs.P_subsidy_SB_dollars[Year]
    self.R_CBFS_subsidy_PB_dollars[Year] = Config.Cbfs.P_subsidy_PB_dollars[Year]
    self.R_CBFS_donation_NP_dollars[Year] = Config.Cbfs.P_donation_NP_dollars[Year]

    # receive Person spending and dollar donation funds (not CBFS) from previous year
    self.R_spending_tokens[Year] = Config.Persons.P_spending_tokens[Year-1]
    self.R_spending_dollars[Year] = Config.Persons.P_spending_dollars[Year-1]
    self.R_donation_NP_dollars[Year] = Config.Persons.P_donation_NP_dollars[Year-1]
    
    # receive gov funds from current year
    self.R_gov_contract_SB_dollars[Year] = Config.Gov.P_contract_SB_dollars[Year]
    self.R_gov_contract_PB_dollars[Year] = Config.Gov.P_contract_PB_dollars[Year]
    self.R_gov_contract_NP_dollars[Year] = Config.Gov.P_contract_NP_dollars[Year]
    self.R_gov_subsidy_SB_dollars[Year] = Config.Gov.P_subsidy_SB_dollars[Year]
    self.R_gov_subsidy_PB_dollars[Year] = Config.Gov.P_subsidy_PB_dollars[Year]
    self.R_gov_grant_NP_dollars[Year] = Config.Gov.P_grant_NP_dollars[Year]
    
    # summaries, tokens
    self.R_CBFS_loan_tokens[Year] = self.R_CBFS_loan_SB_tokens[Year] + \
      self.R_CBFS_loan_PB_tokens[Year] + self.R_CBFS_loan_NP_tokens[Year]
    
    self.R_CBFS_subsidy_tokens[Year] = self.R_CBFS_subsidy_SB_tokens[Year] + \
      self.R_CBFS_subsidy_PB_tokens[Year]
    
    self.R_CBFS_SB_tokens[Year] = self.R_CBFS_loan_SB_tokens[Year] + self.R_CBFS_subsidy_SB_tokens[Year]
    self.R_CBFS_PB_tokens[Year] = self.R_CBFS_loan_PB_tokens[Year] + self.R_CBFS_subsidy_PB_tokens[Year]
    self.R_CBFS_NP_tokens[Year] = self.R_CBFS_loan_NP_tokens[Year] + self.R_CBFS_donation_NP_tokens[Year]
    self.R_CBFS_tokens[Year] = self.R_CBFS_SB_tokens[Year] + self.R_CBFS_PB_tokens[Year] + \
      self.R_CBFS_NP_tokens[Year]
    
    self.R_tokens[Year] = self.R_CBFS_tokens[Year] + self.R_spending_tokens[Year]

    # summaries, dollars    
    self.R_CBFS_loan_dollars[Year] = self.R_CBFS_loan_SB_dollars[Year] + \
      self.R_CBFS_loan_PB_dollars[Year] + self.R_CBFS_loan_NP_dollars[Year]
    
    self.R_CBFS_subsidy_dollars[Year] = self.R_CBFS_subsidy_SB_dollars[Year] + \
      self.R_CBFS_subsidy_PB_dollars[Year]
    
    self.R_CBFS_SB_dollars[Year] = self.R_CBFS_loan_SB_dollars[Year] + \
      self.R_CBFS_subsidy_SB_dollars[Year]
    self.R_CBFS_PB_dollars[Year] = self.R_CBFS_loan_PB_dollars[Year] + \
      self.R_CBFS_subsidy_PB_dollars[Year]
    self.R_CBFS_NP_dollars[Year] = self.R_CBFS_loan_NP_dollars[Year] + \
      self.R_CBFS_donation_NP_dollars[Year]
    self.R_CBFS_dollars[Year] = self.R_CBFS_SB_dollars[Year] + self.R_CBFS_PB_dollars[Year] + \
      self.R_CBFS_NP_dollars[Year]
    
    self.R_gov_contract_dollars[Year] = self.R_gov_contract_SB_dollars[Year] + \
      self.R_gov_contract_PB_dollars[Year] + self.R_gov_contract_NP_dollars[Year]
    self.R_gov_subsidy_dollars[Year] = self.R_gov_subsidy_SB_dollars[Year] + \
      self.R_gov_subsidy_PB_dollars[Year]
    
    self.R_gov_SB_dollars[Year] = self.R_gov_contract_SB_dollars[Year] + \
      self.R_gov_subsidy_SB_dollars[Year]
    self.R_gov_PB_dollars[Year] = self.R_gov_contract_PB_dollars[Year] + \
      self.R_gov_subsidy_PB_dollars[Year]
    self.R_gov_NP_dollars[Year] = self.R_gov_contract_NP_dollars[Year] + \
      self.R_gov_grant_NP_dollars[Year]
    
    self.R_gov_dollars[Year] = self.R_gov_SB_dollars[Year] + self.R_gov_PB_dollars[Year] + \
      self.R_gov_NP_dollars[Year]

    # receipts by different types of organizations
    self.R_SB_dollars[Year] = self.R_CBFS_SB_dollars[Year] + \
      self.R_gov_contract_SB_dollars[Year] + self.R_gov_subsidy_SB_dollars[Year] 
    self.R_PB_dollars[Year] = self.R_CBFS_PB_dollars[Year] + \
      self.R_gov_contract_PB_dollars[Year] + self.R_gov_subsidy_PB_dollars[Year] 
    self.R_NP_dollars[Year] = self.R_CBFS_NP_dollars[Year] + \
      self.R_gov_contract_NP_dollars[Year] + self.R_gov_grant_NP_dollars[Year] + \
      self.R_donation_NP_dollars[Year] 
    
    self.R_dollars[Year] = self.R_CBFS_dollars[Year] + self.R_spending_dollars[Year] + \
      self.R_gov_dollars[Year] + self.R_donation_NP_dollars[Year] 

    # summaries, tokens + dollars
    self.R_CBFS_loan_SB_total[Year] = self.R_CBFS_loan_SB_tokens[Year] + \
      self.R_CBFS_loan_SB_dollars[Year]
    self.R_CBFS_loan_PB_total[Year] = self.R_CBFS_loan_PB_tokens[Year] + \
      self.R_CBFS_loan_PB_dollars[Year]
    self.R_CBFS_loan_NP_total[Year] = self.R_CBFS_loan_NP_tokens[Year] + \
      self.R_CBFS_loan_NP_dollars[Year]
    self.R_CBFS_loan_total[Year] = self.R_CBFS_loan_tokens[Year] + self.R_CBFS_loan_dollars[Year]
    
    self.R_CBFS_donation_NP_total[Year] = self.R_CBFS_donation_NP_tokens[Year] + \
      self.R_CBFS_donation_NP_dollars[Year]
    self.R_CBFS_subsidy_total[Year] = self.R_CBFS_subsidy_tokens[Year] + \
      self.R_CBFS_subsidy_dollars[Year]
    
    self.R_CBFS_total[Year] = self.R_CBFS_tokens[Year] + self.R_CBFS_dollars[Year]
    
    self.R_spending_total[Year] = self.R_spending_tokens[Year] + self.R_spending_dollars[Year]
    
    self.R_total[Year] = self.R_tokens[Year] + self.R_dollars[Year]
    
    assert np.allclose(self.R_total[Year], self.R_CBFS_loan_SB_total[Year] + \
      self.R_CBFS_loan_PB_total[Year] + self.R_CBFS_loan_NP_total[Year] + \
      self.R_CBFS_donation_NP_total[Year] + self.R_CBFS_subsidy_total[Year] + \
      self.R_spending_total[Year] + self.R_gov_dollars[Year] + self.R_donation_NP_dollars[Year])

      
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def makePayments(self,Year):    
    """
    
    Make payments of tokens and dollars. Income changes due to job loss, new hires, and revised wages 
    have already been accounted for in Org.raiseWages(), Ledda.loseJobs(), Cbfs.makePayments(). 
    Payback of CBFS loan principal assumes three-year average maturity and zero interest.
    
    """    
    
    # ----------------------- payments of organizations -----------------
    
    # pay loan principal, assume 3-year average loan maturity
    if Year > Config.burn_in_period:
      for i in [0, 1, 2]:
        self.P_CBFS_loan_SB_tokens[Year] += self.R_CBFS_loan_SB_tokens[Year-i] * 1./3
        self.P_CBFS_loan_PB_tokens[Year] += self.R_CBFS_loan_PB_tokens[Year-i] * 1./3
        self.P_CBFS_loan_NP_tokens[Year] += self.R_CBFS_loan_NP_tokens[Year-i] * 1./3
        
        self.P_CBFS_loan_SB_dollars[Year] += self.R_CBFS_loan_SB_dollars[Year-i] * 1./3
        self.P_CBFS_loan_PB_dollars[Year] += self.R_CBFS_loan_PB_dollars[Year-i] * 1./3
        self.P_CBFS_loan_NP_dollars[Year] += self.R_CBFS_loan_NP_dollars[Year-i] * 1./3
    
    # pay wages
    self.P_wages_SB_tokens[Year] = Config.TP.cols.R_wages_SB_tokens[:].sum()
    self.P_wages_PB_tokens[Year] = Config.TP.cols.R_wages_PB_tokens[:].sum()
    self.P_wages_NP_tokens[Year] = Config.TP.cols.R_wages_NP_tokens[:].sum()

    self.P_wages_SB_dollars[Year] = Config.TP.cols.R_wages_SB_dollars[:].sum()
    self.P_wages_PB_dollars[Year] = Config.TP.cols.R_wages_PB_dollars[:].sum()
    self.P_wages_NP_dollars[Year] = Config.TP.cols.R_wages_NP_dollars[:].sum()      

    # pay RoW handled in summarizePayments()
    

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizePayments(self, Year):    
    """
    
    Summarize payments for tokens, dollars, and tokens + dollars.
    
    """
    
    # ----------------------- payments of organizations -----------------------
    # tokens
    self.P_wages_tokens[Year] = self.P_wages_SB_tokens[Year] + self.P_wages_PB_tokens[Year] + \
      self.P_wages_NP_tokens[Year]
    self.P_CBFS_loan_tokens[Year] = self.P_CBFS_loan_SB_tokens[Year] + \
      self.P_CBFS_loan_PB_tokens[Year] + self.P_CBFS_loan_NP_tokens[Year]

    self.P_SB_tokens[Year] = self.P_wages_SB_tokens[Year] + self.P_CBFS_loan_SB_tokens[Year]
    self.P_PB_tokens[Year] = self.P_wages_PB_tokens[Year] + self.P_CBFS_loan_PB_tokens[Year]
    self.P_NP_tokens[Year] = self.P_wages_NP_tokens[Year] + self.P_CBFS_loan_NP_tokens[Year]

    self.P_tokens[Year] = self.P_wages_tokens[Year] + self.P_CBFS_loan_tokens[Year]

    # dollars
    self.P_wages_dollars[Year] = self.P_wages_SB_dollars[Year] + self.P_wages_PB_dollars[Year] + \
      self.P_wages_NP_dollars[Year]
    self.P_CBFS_loan_dollars[Year] = self.P_CBFS_loan_SB_dollars[Year] + \
      self.P_CBFS_loan_PB_dollars[Year] + self.P_CBFS_loan_NP_dollars[Year]

    self.P_SB_dollars[Year] = self.P_wages_SB_dollars[Year] + self.P_CBFS_loan_SB_dollars[Year]
    self.P_PB_dollars[Year] = self.P_wages_PB_dollars[Year] + self.P_CBFS_loan_PB_dollars[Year]
    self.P_NP_dollars[Year] = self.P_wages_NP_dollars[Year] + self.P_CBFS_loan_NP_dollars[Year]

    self.P_dollars[Year] = self.P_wages_dollars[Year] + self.P_CBFS_loan_dollars[Year]
    
    # totals
    self.P_wages_SB_total[Year] = self.P_wages_SB_tokens[Year] + self.P_wages_SB_dollars[Year]
    self.P_wages_PB_total[Year] = self.P_wages_PB_tokens[Year] + self.P_wages_PB_dollars[Year]
    self.P_wages_NP_total[Year] = self.P_wages_NP_tokens[Year] + self.P_wages_NP_dollars[Year]
    self.P_wages_total[Year] = self.P_wages_SB_total[Year] + self.P_wages_PB_total[Year] + \
      self.P_wages_NP_total[Year]
    
    self.P_CBFS_loan_SB_total[Year] = self.P_CBFS_loan_SB_tokens[Year] + \
      self.P_CBFS_loan_SB_dollars[Year]
    self.P_CBFS_loan_PB_total[Year] = self.P_CBFS_loan_PB_tokens[Year] + \
      self.P_CBFS_loan_PB_dollars[Year]
    self.P_CBFS_loan_NP_total[Year] = self.P_CBFS_loan_NP_tokens[Year] + \
      self.P_CBFS_loan_NP_dollars[Year]
    
    self.P_CBFS_loan_total[Year] = self.P_CBFS_loan_SB_total[Year] + self.P_CBFS_loan_PB_total[Year] + \
      self.P_CBFS_loan_NP_total[Year]
    
    self.P_total[Year] = self.P_wages_total[Year] + self.P_CBFS_loan_total[Year]

    # cumulative wage increases
    if Year >=1:
      self.wage_increase_tokens_cumulative[Year] += \
        (self.P_wages_tokens[Year] - self.P_wages_tokens[1])
      self.wage_increase_dollars_cumulative[Year] += \
        (self.P_wages_dollars[Year] - self.P_wages_dollars[1])
      self.wage_increase_total_cumulative[Year] = \
        self.wage_increase_tokens_cumulative[Year] + self.wage_increase_dollars_cumulative[Year]
      
      delta_wages = self.wage_increase_total_cumulative[Year] - \
        self.wage_increase_total_cumulative[Year-1]
      if (delta_wages > 0) and (Year < Config.burn_in_period + Config.growth_period -1):
        delta_loans = Config.Cbfs.loan_outstd_total[Year] - Config.Cbfs.loan_outstd_total[Year-1]
        self.fraction_outstd_loans_wage_increase[Year] = delta_loans / delta_wages

    W6 = Config.TP.getWhereList("(membership==1) & (work_status==6)")
    P_NP_6 = Config.TP.cols.R_wages_NP_tokens[:][W6].sum() + \
      Config.TP.cols.R_wages_NP_dollars[:][W6].sum()
    if P_NP_6 > 0:
      self.ratio_R_NP_CBFS_P_NP_ws6[Year] =  (self.R_CBFS_donation_NP_tokens[Year] + \
        self.R_CBFS_donation_NP_dollars[Year]) / P_NP_6

    Wsb = Config.TP.getWhereList("(work_status==5) | (work_status==7)")
    Wpb = Config.TP.getWhereList("(work_status==8)")
    Wnp = Config.TP.getWhereList("(work_status==4) | (work_status==6)")
    WF_total = float(Wsb.size + Wpb.size + Wnp.size)
    self.fraction_WF_SB[Year] = Wsb.size / WF_total
    self.fraction_WF_PB[Year] = Wpb.size / WF_total
    self.fraction_WF_NP[Year] = Wnp.size / WF_total  
       
         
    # ----------------------------------------------------------------------------
    # Org deficit of tokens and dollars, and interaction with rest of counties
    # ----------------------------------------------------------------------------
    
    if Year > 1:
      # calc token deficit (created tokens)
      self.created_tokens[Year] = -self.R_tokens[Year] + self.P_tokens[Year]
      
      # calc dollar deficit, and balance it by altering rest of counties spending
      self.deficit_dollars[Year] = -self.R_dollars[Year] + self.P_dollars[Year]
      
      if ((self.created_tokens[Year] > 0) and 
        (Year <= (Config.burn_in_period + Config.growth_period-1))):
        self.dollar_token_deficit_ratio[Year] = \
          self.deficit_dollars[Year] / self.created_tokens[Year]
      
      # Adjust import/exports to balance dollar deficit. Orgs hold import rate of revenue (sales of 
      # products to other counties) steady while decreasing the export rate of revenue (purchase of 
      # outside products).  In a real setting, both would change.  Actual import/exports rates are not 
      # critical to the simulation, except to show conceptually that the trade balance can be adjusted. 
      self.import_dollar_revenue[Year] = Config.fraction_Org_import_revenue * self.R_dollars[Year]
      self.export_dollar_revenue[Year] = self.import_dollar_revenue[Year] - self.deficit_dollars[Year] 

      # adjust dollar receipts
      self.R_dollars[Year] += self.deficit_dollars[Year]
      assert np.allclose(self.R_dollars[Year], self.P_dollars[Year], atol=.01)

      self.import_fraction_receipts[Year] = Config.fraction_Org_import_revenue + 1e-6 # nudge for graph
      self.export_fraction_receipts[Year] = \
        self.export_dollar_revenue[Year] / (self.R_dollars[Year])
      self.import_export_ratio[Year] = \
        self.import_dollar_revenue[Year] / self.export_dollar_revenue[Year]

      # record Roc spending and payments
      Config.Roc.P_org_spending_dollars[Year] = self.import_dollar_revenue[Year]
      Config.Roc.R_org_spending_dollars[Year] = self.export_dollar_revenue[Year]
      
      assert self.import_dollar_revenue[Year] >= self.export_dollar_revenue[Year] - .01
      
      Config.Roc.pool_dollars[Year] = Config.Roc.pool_dollars[Year-1] + \
        Config.Roc.R_org_spending_dollars[Year] + Config.Roc.R_gov_spending_dollars[Year] - \
        Config.Roc.P_org_spending_dollars[Year]
      
      # Determine the fraction of revenue for LEDDA organizations that is made up of the trade balance. 
      # Calculate receipts of member organizations based on participation rate (or fraction of persons 
      # who receive tokens)
      
      Ww = Config.TP.getWhereList("R_tokens > 0").size
      Config.Ledda.rate_with_tokens[Year] = Ww/float(Config.adult_county_population)

      if Config.Ledda.rate_with_tokens[Year] !=0:
        # base receipts of member orgs on fraction who receive tokens:
        self.deficit_fraction_LEDDA_dollar_receipts[Year] = self.deficit_dollars[Year] / \
          (self.R_dollars[Year] * Config.Ledda.rate_with_tokens[Year])

        # calculate approximate token share of receipts for member organizations.  Base receipts of 
        # member organizations on fraction of persons who have tokens
        self.share_LEDDA_receipts_token[Year] = self.R_tokens[Year] / \
          (self.R_total[Year] * Config.Ledda.rate_with_tokens[Year])
        






 

