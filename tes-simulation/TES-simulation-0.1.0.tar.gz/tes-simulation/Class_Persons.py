
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
import cProfile, pstats, line_profiler, timeit
from scipy import stats


sys.path.append('./')
import Config, MiscFx


# ===========================================================================================
# PERSONS class
# ===========================================================================================


class PERSONS(object):
  """
  
  Class for the Persons object.  For explanations of variable names, see Initialize.getHDF5() and 
  Config.  The Persons object holds summary information obtained from the Person's table (TP). 

  """ 
  
   
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "Persons"
    
    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    

    # ----------------------- receipts of persons -----------------
    
    # ------------------- tokens --------------------------------
    # tokens, raw
    for Type in [
      'R_wages_SB_tokens', 'R_wages_PB_tokens', 'R_wages_NP_tokens', 
      'R_CBFS_nurture_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 

    # tokens, summaries
    for Type in [
      'R_wages_tokens', 'R_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 
      
    # ------------------- dollars -------------------------------
    # dollars, raw
    for Type in [
      'R_wages_SB_dollars', 'R_wages_PB_dollars', 'R_wages_NP_dollars',
      'R_CBFS_nurture_dollars',
      'R_gov_support_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 

    # dollars, summaries
    for Type in [      
      'R_wages_dollars', 'R_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 
      

    # ------------------- tokens + dollars ----------------------
    for Type in [   
      'R_wages_SB_total', 'R_wages_PB_total', 'R_wages_NP_total',   
      'R_wages_total',
      'R_CBFS_nurture_total',     
      'R_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))
       
    
    # ----------------------- payments of persons -----------------
    
    # ------------------- tokens --------------------------------
    # tokens, raw
    for Type in [
      'P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 'P_CBFS_loan_NP_tokens', 
      'P_CBFS_subsidy_SB_tokens', 'P_CBFS_subsidy_PB_tokens', 
      'P_CBFS_donation_NP_tokens', 'P_CBFS_nurture_tokens',
      'P_spending_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 
    
    # tokens, summaries
    for Type in [
      'P_CBFS_loan_tokens', 'P_CBFS_subsidy_tokens', 
      'P_CBFS_SB_tokens', 'P_CBFS_PB_tokens', 'P_CBFS_NP_tokens', 
      'P_CBFS_tokens',
      'P_tokens']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 


    # ------------------- dollars -------------------------------
    # CBFS dollars, raw
    for Type in [      
      'P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 'P_CBFS_loan_NP_dollars', 
      'P_CBFS_subsidy_SB_dollars', 'P_CBFS_subsidy_PB_dollars',
      'P_CBFS_donation_NP_dollars', 'P_CBFS_nurture_dollars',
      'P_spending_dollars',
      'P_gov_tax_dollars', 
      'P_donation_NP_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d')) 

    # dollars, summaries
    for Type in [      
      'P_CBFS_loan_dollars', 'P_CBFS_subsidy_dollars', 
      'P_CBFS_SB_dollars', 'P_CBFS_PB_dollars', 'P_CBFS_NP_dollars',       
      'P_CBFS_dollars',
      'P_dollars']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))   

    # ------------------- tokens + dollars ----------------------
    for Type in [
      'P_CBFS_loan_SB_total', 'P_CBFS_loan_PB_total', 'P_CBFS_loan_NP_total',
      'P_CBFS_loan_total', 'P_CBFS_subsidy_total', 'P_CBFS_nurture_total',  'P_CBFS_donation_NP_total',
      'P_CBFS_total',
      'P_spending_total', 
      'P_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))          

    # ----------------------- savings of persons and msc. ----------------
    for Type in [
      'CBFS_save_dollars', 'CBFS_save_tokens', 'CBFS_save_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))  


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
      
    self.graphGroup = {}
    self.graphGroup['R+wages+tokens'] = ['R_wages_SB_tokens', 'R_wages_PB_tokens', 'R_wages_NP_tokens',
      'R_CBFS_nurture_tokens', 'R_wages_tokens']
    self.graphGroup['R+wages+dollars'] = ['R_wages_SB_dollars', 'R_wages_PB_dollars', 
      'R_wages_NP_dollars', 'R_CBFS_nurture_dollars', 'R_gov_support_dollars', 'R_wages_dollars']
    self.graphGroup['R+total'] = ['R_tokens', 'R_dollars', 'R_total']
    self.graphGroup['R+wages+org'] = ['R_wages_SB_total', 'R_wages_PB_total', 'R_wages_NP_total',   
      'R_wages_total', 'R_CBFS_nurture_total']
    
    self.graphGroup['P+CBFS+tokens'] = ['P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 
      'P_CBFS_loan_NP_tokens', 'P_CBFS_subsidy_SB_tokens', 'P_CBFS_subsidy_PB_tokens', 
      'P_CBFS_donation_NP_tokens', 'P_CBFS_nurture_tokens']
    self.graphGroup['P+CBFS+dollars'] = ['P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 
      'P_CBFS_loan_NP_dollars', 'P_CBFS_subsidy_SB_dollars', 'P_CBFS_subsidy_PB_dollars', 
      'P_CBFS_donation_NP_dollars', 'P_CBFS_nurture_dollars']
    self.graphGroup['P+spending'] = ['P_spending_tokens', 'P_spending_dollars', 'P_spending_total', 
      'P_gov_tax_dollars', 'P_donation_NP_dollars']    
    self.graphGroup['P+CBFS+tokens+sum'] = ['P_CBFS_loan_tokens', 'P_CBFS_subsidy_tokens', 
      'P_CBFS_SB_tokens', 'P_CBFS_PB_tokens', 'P_CBFS_NP_tokens']
    self.graphGroup['P+CBFS+dollars+sum'] = ['P_CBFS_loan_dollars', 'P_CBFS_subsidy_dollars', 
      'P_CBFS_SB_dollars', 'P_CBFS_PB_dollars', 'P_CBFS_NP_dollars']
    self.graphGroup['P+total'] = ['P_tokens', 'P_dollars', 'P_total']
    self.graphGroup['P+CBFS+total'] = ['P_CBFS_tokens', 'P_CBFS_dollars', 'P_CBFS_total']
    self.graphGroup['P+CBFS+total+org'] = ['P_CBFS_loan_SB_total', 'P_CBFS_loan_PB_total', 
      'P_CBFS_loan_NP_total', 'P_CBFS_loan_total', 'P_CBFS_subsidy_total', 'P_CBFS_nurture_total',  
      'P_CBFS_donation_NP_total']
      
    self.graphGroup['save'] = ['CBFS_save_dollars', 'CBFS_save_tokens', 'CBFS_save_total'] 



  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizeReceipts(self, Year):
    """
    
    Summarize receipts for tokens, dollars, and tokens + dollars.
    
    """
    # ----------------------- receipts of persons -----------------------

    # update Persons table
    Config.TP.cols.R_tokens[:] = Config.TP.cols.R_wages_SB_tokens[:] + \
      Config.TP.cols.R_wages_PB_tokens[:] + Config.TP.cols.R_wages_NP_tokens[:] + \
      Config.TP.cols.R_CBFS_nurture_tokens[:] 
    
    Config.TP.cols.R_dollars[:] = Config.TP.cols.R_wages_SB_dollars[:] + \
      Config.TP.cols.R_wages_PB_dollars[:] + Config.TP.cols.R_wages_NP_dollars[:] + \
      Config.TP.cols.R_CBFS_nurture_dollars[:] + Config.TP.cols.R_gov_support_dollars[:] 
    
    Config.TP.cols.R_total[:] = Config.TP.cols.R_tokens[:] + Config.TP.cols.R_dollars[:]

    # Persons table
    R_tokens = np.zeros_like(Config.TP.cols.R_wages_SB_tokens[:])
    R_dollars = np.zeros_like(Config.TP.cols.R_wages_SB_tokens[:])
    for Type in [  
      'R_wages_SB_tokens', 'R_wages_PB_tokens', 'R_wages_NP_tokens',
      'R_CBFS_nurture_tokens', 
      'R_wages_SB_dollars', 'R_wages_PB_dollars', 'R_wages_NP_dollars', 
      'R_CBFS_nurture_dollars',
      'R_gov_support_dollars']:
      self.__dict__[Type][Year] = Config.TP.cols.__dict__[Type][:].sum()
      if 'tokens' in Type:
        R_tokens += Config.TP.cols.__dict__[Type][:]
      elif 'dollars' in Type:
        R_dollars += Config.TP.cols.__dict__[Type][:]
    R_total = R_tokens + R_dollars
    
    assert np.allclose(Config.TP.cols.R_tokens[:], R_tokens, atol=.01)
    assert np.allclose(Config.TP.cols.R_dollars[:], R_dollars, atol=.01)
    assert np.allclose(Config.TP.cols.R_total[:], R_total, atol=.01)
    
    # Persons object arrays
    self.R_wages_tokens[Year] = self.R_wages_SB_tokens[Year] + self.R_wages_PB_tokens[Year] + \
      self.R_wages_NP_tokens[Year]
    self.R_wages_dollars[Year] = self.R_wages_SB_dollars[Year] + self.R_wages_PB_dollars[Year] + \
      self.R_wages_NP_dollars[Year]
    
    self.R_tokens[Year] = self.R_wages_tokens[Year] + self.R_CBFS_nurture_tokens[Year]
    self.R_dollars[Year] = self.R_wages_dollars[Year] + self.R_CBFS_nurture_dollars[Year] + \
      self.R_gov_support_dollars[Year]
    
    self.R_wages_SB_total[Year] = self.R_wages_SB_tokens[Year] + self.R_wages_SB_dollars[Year]
    self.R_wages_PB_total[Year] = self.R_wages_PB_tokens[Year] + self.R_wages_PB_dollars[Year]
    self.R_wages_NP_total[Year] = self.R_wages_NP_tokens[Year] + self.R_wages_NP_dollars[Year]
    self.R_wages_total[Year] = self.R_wages_tokens[Year] + self.R_wages_dollars[Year]
    self.R_CBFS_nurture_total[Year] = self.R_CBFS_nurture_tokens[Year] + \
      self.R_CBFS_nurture_dollars[Year]
    
    self.R_total[Year] = self.R_tokens[Year] + self.R_dollars[Year]
    
    # checks
    assert np.allclose(Config.TP.cols.R_tokens[:].sum(), self.R_tokens[Year])
    assert np.allclose(Config.TP.cols.R_dollars[:].sum(), self.R_dollars[Year])
    assert np.allclose(Config.TP.cols.R_total[:].sum(), self.R_total[Year])
    
    assert np.allclose(self.R_wages_total[Year], self.R_wages_SB_total[Year] + \
      self.R_wages_PB_total[Year] + self.R_wages_NP_total[Year])
    assert np.allclose(self.R_total[Year], self.R_wages_total[Year] + self.R_CBFS_nurture_total[Year] + \
      self.R_gov_support_dollars[Year])
    
    # calculate new TSI
    W1 = Config.TP.getWhereList("R_tokens > 0")
    if W1.size > 0:
      #W1 = Config.TP.getWhereList("(membership==1)")
      Config.Ledda.share_income_token[Year] = Config.TP.cols.R_tokens[:][W1].sum() / \
        Config.TP.cols.R_total[:][W1].sum()

    assert np.all(Config.TP.cols.R_dollars[:] > 0)
    assert np.all(Config.TP.cols.R_tokens[:] >= 0)    


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def makePayments(self,Year):    
    """
    
    Make payments of tokens and dollars.  This function does not change Wage Option choices or income.  
    It only uses set incomes and Wage Option choices to calculate token and dollar CBFS payments.  
    
    """    
    # ----------------------- payments of persons -----------------
    
    # --------------------- CBFS payments -------------
    if Year >= Config.burn_in_period:

      P0 = Config.TP.getWhereList("(membership==1) & (work_status !=0) & (work_status !=2)")
      Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0 = self.getFamilyData(P0) 

      # set base wage to gov support level for nurture if person lost job this year without job gain
      jobLoss = Config.TP.getWhereList("(work_status==3) & (job_loss==1) & (job_gain==0)")
      p0_test = np.in1d(Persons[:,0], jobLoss, assume_unique=True)
      BaseWage[p0_test,0] = Config.Gov.support_dollars_mean
      p1_test = np.in1d(Persons[:,1], jobLoss, assume_unique=True)
      BaseWage[p1_test,1] = Config.Gov.support_dollars_mean

      # get new wages, etc.  Note makePayments flag=True
      Config.Ledda.wageOptions(self, Persons, BaseWage, WorkStatus, Membership, JobLoss, Year, \
        makePayments=True)

      # checks
      W102 = Config.TP.getWhereList("(membership==1) & (work_status!=0) & (work_status!=2) " + \
        "& (wage_option>0)")
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

    else:
      # no CBFS contributions
      Config.TP.cols.R_postCBFS_total[:] = Config.TP.cols.R_total[:]
      Config.TP.cols.R_postCBFS_total_prelim[:] = Config.TP.cols.R_postCBFS_total[:]
    
    # --------------------- non CBFS payments ---------


    # dollar donations to nonprofts (apart from CBFS)
    P_donation_NP_dollars = Config.TP.cols.R_dollars[:] * Config.rate_dollar_donation
    Config.TP.cols.P_donation_NP_dollars[:] = P_donation_NP_dollars
    
    assert np.all(Config.TP.cols.P_donation_NP_dollars[:] >= 0)

    # taxes
    donations = Config.TP.cols.P_CBFS_donation_NP_tokens[:] + \
      Config.TP.cols.P_CBFS_donation_NP_dollars[:] + \
      Config.TP.cols.P_CBFS_nurture_tokens[:] + Config.TP.cols.P_CBFS_nurture_dollars[:] + \
      Config.TP.cols.P_donation_NP_dollars[:]
    
    AGI = np.maximum(0, Config.TP.cols.R_total[:] - np.maximum(donations, Config.gov_standard_deduction))
    Config.TP.cols.P_gov_tax_dollars[:] = AGI * Config.Gov.tax_rate
    
    assert np.all(Config.TP.cols.P_gov_tax_dollars[:] >= 0)
    
    #spending, based on fraction of Org income that is SB, PB, NP spending  
    spending_tokens = Config.TP.cols.R_tokens[:] - Config.TP.cols.P_CBFS_tokens[:]
    spending_dollars = Config.TP.cols.R_dollars[:] - Config.TP.cols.P_CBFS_dollars[:] - \
      Config.TP.cols.P_gov_tax_dollars[:] - Config.TP.cols.P_donation_NP_dollars[:]   

    if Year == 0:
      Config.Org.R_gov_SB_dollars[Year] = Config.Gov.P_contract_forprofit_dollars_annual + \
        Config.Gov.P_subsidy_forprofit_dollars_annual
      Config.Org.R_gov_NP_dollars[Year] = Config.Gov.P_contract_NP_dollars_annual + \
        Config.Gov.P_grant_NP_dollars_annual      
    
    Config.TP.cols.P_spending_tokens[:] = spending_tokens 
    Config.TP.cols.P_spending_dollars[:] = spending_dollars 
    
    assert np.all(Config.TP.cols.P_spending_tokens[:] >= 0)
    assert np.all(Config.TP.cols.P_spending_dollars[:] >= 0)
    

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def summarizePayments(self, Year):    
    """
    
    Summarize payments for tokens, dollars, and tokens + dollars.
    
    """
    # ----------------------- payments of persons -----------------------
    
    Config.TP.cols.P_tokens[:] = Config.TP.cols.P_CBFS_tokens[:] + \
      Config.TP.cols.P_spending_tokens[:] 
    
    Config.TP.cols.P_dollars[:] = Config.TP.cols.P_CBFS_dollars[:] + \
      Config.TP.cols.P_spending_dollars[:] + Config.TP.cols.P_gov_tax_dollars[:] + \
      Config.TP.cols.P_donation_NP_dollars[:]   

    Config.TP.cols.P_total[:] = Config.TP.cols.P_tokens[:] + Config.TP.cols.P_dollars[:]
    
    assert np.allclose(Config.TP.cols.P_tokens[:].sum(), Config.TP.cols.R_tokens[:].sum())
    assert np.allclose(Config.TP.cols.P_dollars[:].sum(), Config.TP.cols.R_dollars[:].sum())
    assert np.allclose(Config.TP.cols.P_total[:].sum(), Config.TP.cols.R_total[:].sum())

    # donation dollars to NPs
    self.P_donation_NP_dollars[Year] = Config.TP.cols.P_donation_NP_dollars[:].sum() 
    
    # taxes
    self.P_gov_tax_dollars[Year] = Config.TP.cols.P_gov_tax_dollars[:].sum()  
    
    # CBFS summaries, tokens
    self.P_CBFS_loan_tokens[Year] = self.P_CBFS_loan_SB_tokens[Year] + \
      self.P_CBFS_loan_PB_tokens[Year] + self.P_CBFS_loan_NP_tokens[Year]
    self.P_CBFS_subsidy_tokens[Year] = self.P_CBFS_subsidy_SB_tokens[Year] + \
      self.P_CBFS_subsidy_PB_tokens[Year]
    self.P_CBFS_SB_tokens[Year] = self.P_CBFS_loan_SB_tokens[Year] + self.P_CBFS_subsidy_SB_tokens[Year]
    self.P_CBFS_PB_tokens[Year] = self.P_CBFS_loan_PB_tokens[Year] + self.P_CBFS_subsidy_PB_tokens[Year]
    self.P_CBFS_NP_tokens[Year] = self.P_CBFS_loan_NP_tokens[Year] + self.P_CBFS_donation_NP_tokens[Year]
    self.P_CBFS_tokens[Year] = self.P_CBFS_SB_tokens[Year] + self.P_CBFS_PB_tokens[Year] + \
      self.P_CBFS_NP_tokens[Year] +  self.P_CBFS_nurture_tokens[Year]

    # CBFS summaries, dollars
    self.P_CBFS_loan_dollars[Year] = self.P_CBFS_loan_SB_dollars[Year] + \
      self.P_CBFS_loan_PB_dollars[Year] + self.P_CBFS_loan_NP_dollars[Year]
    self.P_CBFS_subsidy_dollars[Year] = self.P_CBFS_subsidy_SB_dollars[Year] + \
      self.P_CBFS_subsidy_PB_dollars[Year]
    self.P_CBFS_SB_dollars[Year] =  self.P_CBFS_loan_SB_dollars[Year] + \
      self.P_CBFS_subsidy_SB_dollars[Year]
    self.P_CBFS_PB_dollars[Year] = self.P_CBFS_loan_PB_dollars[Year] + \
      self.P_CBFS_subsidy_PB_dollars[Year]
    self.P_CBFS_NP_dollars[Year] = self.P_CBFS_loan_NP_dollars[Year] + \
      self.P_CBFS_donation_NP_dollars[Year]
    self.P_CBFS_dollars[Year] = self.P_CBFS_SB_dollars[Year] + self.P_CBFS_PB_dollars[Year] + \
      self.P_CBFS_NP_dollars[Year] +  self.P_CBFS_nurture_dollars[Year]

    # CBFS summaries, total
    self.P_CBFS_loan_SB_total[Year] = self.P_CBFS_SB_tokens[Year] + self.P_CBFS_SB_dollars[Year]
    self.P_CBFS_loan_PB_total[Year] = self.P_CBFS_PB_tokens[Year] + self.P_CBFS_PB_dollars[Year]
    self.P_CBFS_loan_NP_total[Year] = self.P_CBFS_NP_tokens[Year] + self.P_CBFS_NP_dollars[Year]
    self.P_CBFS_loan_total[Year] = self.P_CBFS_loan_tokens[Year] + self.P_CBFS_loan_dollars[Year]
    self.P_CBFS_subsidy_total[Year] = self.P_CBFS_subsidy_tokens[Year] + \
      self.P_CBFS_subsidy_dollars[Year]
    self.P_CBFS_nurture_total[Year] = self.P_CBFS_nurture_tokens[Year] + \
      self.P_CBFS_nurture_dollars[Year]
    self.P_CBFS_donation_NP_total[Year] = self.P_CBFS_donation_NP_tokens[Year] + \
      self.P_CBFS_donation_NP_dollars[Year]
    self.P_CBFS_total[Year] = self.P_CBFS_tokens[Year] + self.P_CBFS_dollars[Year]

    # spending, raw
    self.P_spending_tokens[Year] = Config.TP.cols.P_spending_tokens[:].sum() 
    self.P_spending_dollars[Year] = Config.TP.cols.P_spending_dollars[:].sum() 

    # summaries, tokens      
    self.P_tokens[Year] = self.P_spending_tokens[Year] + self.P_CBFS_tokens[Year]
    
    # summaries, dollars
    self.P_dollars[Year] = self.P_spending_dollars[Year] + self.P_CBFS_dollars[Year] + \
      self.P_donation_NP_dollars[Year] + self.P_gov_tax_dollars[Year]
    
    # totals
    self.P_spending_total[Year] = self.P_spending_tokens[Year] + self.P_spending_dollars[Year]
    self.P_total[Year] = self.P_tokens[Year] + self.P_dollars[Year]
    
    # checks
    assert np.allclose(self.P_CBFS_tokens[Year], Config.TP.cols.P_CBFS_tokens[:].sum())
    assert np.allclose(self.P_CBFS_dollars[Year], Config.TP.cols.P_CBFS_dollars[:].sum())
    assert np.allclose(self.P_CBFS_total[Year], self.P_CBFS_loan_total[Year] + \
      self.P_CBFS_subsidy_total[Year] + self.P_CBFS_donation_NP_total[Year] + \
      self.P_CBFS_nurture_total[Year])
    
    assert np.allclose(self.P_total[Year], self.P_CBFS_total[Year] + self.P_spending_total[Year] + \
      self.P_gov_tax_dollars[Year] + self.P_donation_NP_dollars[Year])
    
    assert np.allclose(Config.TP.cols.P_tokens[:].sum(), self.P_tokens[Year], atol=1)
    assert np.allclose(Config.TP.cols.P_dollars[:].sum(), self.P_dollars[Year], atol=1)
    assert np.allclose(Config.TP.cols.P_total[:].sum(), self.P_total[Year], atol=1)
    
    assert np.allclose(self.P_total[Year], self.R_total[Year], atol=1)
    assert np.allclose(self.P_dollars[Year], self.R_dollars[Year], atol=1)
    assert np.allclose(self.P_tokens[Year], self.R_tokens[Year], atol=1)
    

      
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def updateFamily(self, Year, Persons=None):
    """
    
    Update the family's table (TF).
    
    """
    
    if Persons is None:
      # iterate over all families
      Iterator = Config.TF.iterrows()
    else:
      # get family IDs from Persons array and iterate over them
      if type(Persons) != type(np.array([4])):
        Iterator = np.array([Persons])
      Wp1 = Config.TP.getWhereList("R_tokens > 0")
      for person in Persons:
        Families.add(Config.family_dict[person])
      Families = list(Families)
      
    for rowF in Iterator:

      # pid's in persons table are the same as row numbers
      pid1 = rowF['person1']
      pid2 = rowF['person2']
      rowP1 = Config.TP[pid1]
      rowP2 = Config.TP[pid2]

      rowF['R_dollars'] = rowP1['R_dollars'] + rowP2['R_dollars']     
      rowF['R_tokens'] = rowP1['R_tokens'] + rowP2['R_tokens']     
      rowF['R_total'] = rowP1['R_total'] + rowP2['R_total']   

      rowF['P_CBFS_dollars'] = rowP1['P_CBFS_dollars'] + rowP2['P_CBFS_dollars']  
      rowF['P_CBFS_tokens'] = rowP1['P_CBFS_tokens'] + rowP2['P_CBFS_tokens']  
      rowF['P_CBFS_total'] = rowP1['P_CBFS_total'] + rowP2['P_CBFS_total'] 
      
      rowF['R_postCBFS_total'] = rowF['R_total'] - rowF['P_CBFS_total']

      rowF['save_dollars'] = rowP1['save_dollars'] + rowP2['save_dollars']  
      rowF['save_tokens'] = rowP1['save_tokens'] + rowP2['save_tokens']  
      rowF['save_total'] = rowP1['save_total'] + rowP2['save_total'] 
      
      rowF['membership'] = max(rowP1['membership'], rowP2['membership'])
      rowF['job_gain'] = max(rowP1['job_gain'], rowP2['job_gain'])
      rowF['job_loss'] = max(rowP1['job_loss'], rowP2['job_loss'])
      rowF['wage_option'] = max(rowP1['wage_option'], rowP2['wage_option'])
      
      if (rowP1['wage_option'] > 0) and (rowP2['wage_option'] > 0):
        assert rowP1['wage_option'] == rowP2['wage_option']
      
      rowF.update()
          

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def checkFamilyIncome(self, Year, threshold_family, Membership=None, Idd=None):
    """
    
    Select membership applicants from the population that fall below a specifed threshold for family
    income.  Use income data for Year 0 when selecting applicants.  In a real LEDDA, individuals from 
    families of any income level might join.
    
    """
    
    TF0 = Config.HDF5.root._f_getChild('Families_00')
             
    Wc = TF0.getWhereList("(R_total < " +str(threshold_family)+ ")")
    person1 = TF0.cols.person1[:][Wc]
    person2 = TF0.cols.person2[:][Wc]
    persons = np.hstack((person1, person2))
      
    if Membership is not None:
      W0 = Config.TP.getWhereList("membership==" +str(Membership))  
      inarray = np.in1d(persons, W0)
      persons = persons[inarray==True]
      np.random.shuffle(persons)
    
    if Idd is not None:
      return Idd in persons
    else:
      return persons


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def getFamilyData(self, P0):
    """
    
    Collect data for both persons in family for use in determining wage options.
    
    """  
    baseWage_P0 = Config.TP.cols.base_wage[:][P0]
    baseWage0_P0 = Config.TP0.cols.base_wage[:][P0]
    workStatus_P0 = Config.TP.cols.work_status[:][P0]
    membership_P0 = Config.TP.cols.membership[:][P0]
    jobGain_P0 = Config.TP.cols.job_gain[:][P0]
    jobLoss_P0 = Config.TP.cols.job_loss[:][P0]

    P1 = np.zeros_like(P0)    
    baseWage_P1 = np.zeros_like(baseWage_P0)
    baseWage0_P1 = np.zeros_like(baseWage_P0)
    workStatus_P1 = np.zeros_like(membership_P0)
    membership_P1 = np.zeros_like(membership_P0)
    jobGain_P1 = np.zeros_like(membership_P0)
    jobLoss_P1 = np.zeros_like(membership_P0)
    
    # find marriage partners
    for i, idd in enumerate(P0):
      P1[i] = Config.TP.cols.partner[idd]    
      baseWage_P1[i] = Config.TP.cols.base_wage[P1[i]]
      baseWage0_P1[i] = Config.TP0.cols.base_wage[P1[i]]
      workStatus_P1[i] = Config.TP.cols.work_status[P1[i]] 
      membership_P1[i] = Config.TP.cols.membership[P1[i]]
      jobGain_P1[i] = Config.TP.cols.job_gain[P1[i]]    
      jobLoss_P1[i] = Config.TP.cols.job_loss[P1[i]]    

    Persons = np.column_stack((P0,P1))
    BaseWage = np.column_stack((baseWage_P0, baseWage_P1))
    BaseWage0 = np.column_stack((baseWage0_P0, baseWage0_P1))
    WorkStatus = np.column_stack((workStatus_P0, workStatus_P1))
    Membership = np.column_stack((membership_P0, membership_P1))
    JobGain = np.column_stack((jobGain_P0, jobGain_P1))
    JobLoss = np.column_stack((jobLoss_P0, jobLoss_P1))
        
    # remove duplicate families
    A = np.sort(Persons,1)
    _, uID = np.unique(A.view([('',A.dtype)]*A.shape[1]), return_index=True)

    Persons = Persons[uID]
    BaseWage = BaseWage[uID]
    BaseWage0 = BaseWage0[uID]
    WorkStatus = WorkStatus[uID]
    Membership = Membership[uID] 
    JobGain = JobGain[uID]
    JobLoss = JobLoss[uID]

    # randomly choose first and second person
    switch = np.random.randint(0,2,JobGain.shape[0])  
    S = np.where(switch==1)    
    
    Persons[S] = Persons[S,::-1].squeeze()
    BaseWage[S] = BaseWage[S,::-1].squeeze()
    BaseWage0[S] = BaseWage0[S,::-1].squeeze()
    WorkStatus[S] = WorkStatus[S,::-1].squeeze()
    Membership[S] = Membership[S,::-1].squeeze()
    JobGain[S] = JobGain[S,::-1].squeeze()  
    JobLoss[S] = JobLoss[S,::-1].squeeze()  
    
    return Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0


    


