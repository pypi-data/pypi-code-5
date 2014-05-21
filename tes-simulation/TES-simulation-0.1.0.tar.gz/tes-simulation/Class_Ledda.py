
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os
import tables as tb
from scipy import stats


sys.path.append('./')
import Config, MiscFx

np.seterr(all='raise', divide='raise', over='raise', under='raise', invalid='raise')


# ===========================================================================================
# LEDDA class
# ===========================================================================================


class LEDDA(object):
  """
  
  Class for LEDDA object.  Explanations of some variable names are given below (see Initialize.getHDF5() 
  and Config for more information). 
  
  rate_nurture                  = The fraction of members who are unemployed or NIWF that receive LEEDA 
                                    support (via nurture funds).
  rate_with_tokens              = Fraction of members who receive tokens.  A person can be a member and
                                    not receive tokens.
  job_loss                      = the number of jobs lost in a year
  saturation_LFNJ_job           = the fraction of all employed individuals who have LFNJs
  saturation_LFNJ_income        = the fraction of all income of employed individuals that is received by
                                    persons with LFNJs.
  job_loss_mean                 = The mean number of LFNJs lost over the previous five years to 
                                    present.  Persons who hold LFNJs can experience job loss.  
  dollar_loss_inflation         = The dollar loss in CBFS savings (loan accounts) due to dollar 
                                    inflation.  
  *_plus_savings_mean           = Mean of family incomes + savings, where savings is accumulated over 
                                    all years.
  postCBFS_*                    = post-CBFS, pre-tax income
  
  *threshold*                   = The person or family income threshold above which persons will not
                                    join a LEDDA.  In real life, persons from every income level might
                                    join.  
  *wage_option*                 = The wage options: (1) income based on targets, and (2) base income plus
                                    an incentive.  wage_option_working_mean is the mean wage option for
                                    employed members.  
  option_1_ratio                = The fraction of those who receive tokens who also choose wage option 1.
  option_1_fraction_allowed     = The fraction of would-be Option 1 choices allowed.  In the early years,
                                    some members are foced to choose Option 2 in order to reduce the
                                    dollar deficit that organizations experience.
  option_1_sum                  = The sum of all CBFS contributions for Option 1.  This might fall from
                                  year to year due to reduced CBFS loan contributions as people reach
                                  the loan target.
  option_1_nurture_sum          = The sum of all CBFS nurture contributions for Option 1.  This should
                                  not decrease from year to year.
  rate_participation_measured   = The actual participation rate, vs the target set in Config.  The two
                                    might differ late in the simulation period.
  *_CBFS_contrib                = contributions to CBFS by members
  *_CBFS_contrib_income_ratio   = Ratio of CBFS contributions to total income, for those who make 
                                  contributions.
  incentive                     = The amount of the incentive for wage Option 2.  It starts low and then
                                    rises to a maximum over a period of years.   
  """


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def __init__(self):
    self.Title = "LEDDA"
    self.threshold_for_membership_family = float(Config.threshold_for_membership_family)
    self.TSI_target_option_1 = Config.TSI_target  
    self.income_target_total = Config.income_target_total
    self.income_target_tokens = Config.income_target_tokens  
    self.income_target_dollars = Config.income_target_dollars  
    self.option_1_fraction_allowed = Config.option_1_fraction_allowed
    self.rate_participation = Config.rate_participation
    self.incentive = Config.incentive

    # =====================================================================
    # Setup arrays to hold data
    # =====================================================================    
            
    for Type in ['job_loss', 'number_members_new', 'number_members_total']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'i'))

    for Type in ['rate_unemployment', 'rate_NIWF', 'rate_nurture', 'rate_with_tokens',
      'saturation_LFNJ_job', 'saturation_LFNJ_income', 'rate_participation_measured',
      'job_loss_mean', 
      'dollar_loss_inflation',
      'share_income_token', 'share_spending_token',
      
      'post_CBFS_family_income_tokens_mean', 'post_CBFS_family_income_dollars_mean',
      'post_CBFS_family_income_total_mean', 'post_CBFS_family_income_tokens_plus_savings_mean',
      'post_CBFS_family_income_dollars_plus_savings_mean',
      'post_CBFS_family_income_total_plus_savings_mean',
      
      'R_tokens', 'R_dollars', 'R_total',
      'R_postCBFS_mean', 'base_wage_mean', 'wage_option_mean', 'wage_option_working_mean',
      
      'option_1_sum', 'option_1_nurture_sum', 'option_1_ratio',
      
      'mean_CBFS_contrib', 'mean_CBFS_contrib_income_ratio']:
      self.__dict__.__setitem__(Type, np.zeros((Config.simulation_period),'d'))


    # =====================================================================
    # Setup groups for graphing (all variables in group are shown on the same graph)
    # =====================================================================    
    
    self.graphGroup = {}
    self.graphGroup['saturation'] = ['saturation_LFNJ_job', 'saturation_LFNJ_income']
    self.graphGroup['dollar+loss'] = ['dollar_loss_inflation']
    self.graphGroup['share'] = ['share_income_token', 'share_spending_token', 'TSI_target_option_1']
    
    self.graphGroup['family+token'] = ['post_CBFS_family_income_tokens_mean', 
      'post_CBFS_family_income_tokens_plus_savings_mean']
    self.graphGroup['family+dollar'] = ['post_CBFS_family_income_dollars_mean', 
      'post_CBFS_family_income_dollars_plus_savings_mean']    
    self.graphGroup['family+total'] = ['post_CBFS_family_income_total_mean', 
      'post_CBFS_family_income_total_plus_savings_mean']
          
    self.graphGroup['R+total'] = ['R_tokens', 'R_dollars', 'R_total']
    
    self.graphGroup['income+mean'] = ['R_postCBFS_mean', 'base_wage_mean']
    self.graphGroup['income+target'] = ['income_target_tokens', 'income_target_dollars', 
      'income_target_total']

    self.graphGroup['option+mean'] = ['wage_option_mean', 'wage_option_working_mean']
    
    self.graphGroup['option1+fraction'] = ['option_1_fraction_allowed', 'option_1_ratio']
    self.graphGroup['option1+sum'] = ['option_1_sum', 'option_1_nurture_sum']
    
    self.graphGroup['participation'] = ['rate_participation', 'rate_participation_measured',
    'rate_nurture', 'rate_NIWF', 'rate_with_tokens']
      

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def addMembers(self, Year):

    """
    
    Initialize LEDDA membership in Year = Config.burn_in_period - 1.  Assume persons join only if family 
    income is less than about the 90th percentile of family income in the county. In a real LEDDA, 
    persons from any income bracket might join. 
    
    In subsequent years, add members according to the schedule set in Config.  New members who are 
    unemployed or NIWF might have to wait some time before they receive LEDDA support (via CBFS nurture 
    funds).  New members who are employed (or self-employed) arrange for receipt of tokens through their 
    employers.  These members (and all other employed members) will choose a wage option in 
    Org.raiseWages().  
    
    """
    
    threshold_family = self.threshold_for_membership_family
    persons_below_threshold = Config.Persons.checkFamilyIncome(Year, threshold_family, Membership=0)
    all_below_threshold = Config.Persons.checkFamilyIncome(Year, threshold_family)
    all_above_threshold = np.setdiff1d(range(Config.adult_county_population), all_below_threshold, \
      assume_unique=True)
    
    assert Config.TP.cols.membership[:].sum() == all_below_threshold.size - persons_below_threshold.size
    assert Config.Persons.checkFamilyIncome(Year, threshold_family, Membership=1).size == \
      Config.TP.cols.membership[:].sum()
    
    
    np.random.shuffle(persons_below_threshold)
    
    desired = int(round(self.rate_participation[Year] * \
      Config.adult_county_population)) - Config.TP.cols.membership[:].sum()    
    
    Range = persons_below_threshold[0:desired]
    for row in Config.TP.itersequence(Range):
      row['membership'] = 1
      row.update()


    self.number_members_new[Year] = Range.size
    self.number_members_total[Year] = Config.TP.cols.membership[:].sum()  
    
    assert np.allclose(self.number_members_new.sum(), self.number_members_total[Year])
    
    if Year == (Config.burn_in_period - 1):
      #  print stats on initial members
      
      Config.logRoot.info("""
      
      # =====================================================================
      # Initialize LEDDA membership, token share of income is zero
      # ===================================================================== 
      
      """)

      W1 = Config.TP.getWhereList("(membership==1)")
      ave_income_member = Config.TP.cols.R_total[:][W1].mean()
      
      Config.logRoot.info("mean income, member = ${0:,.9g}".format(np.round(ave_income_member,0).item()))
      
      Config.logRoot.info("  percentile of member income= {0:,.4g}".format(
        stats.percentileofscore(Config.TP.cols.R_total[:][W1], ave_income_member)))
      
      Config.logRoot.info("  percentile of county income= {0:,.4g}\n".format(
        stats.percentileofscore(Config.TP.cols.R_total[:], ave_income_member)))
      
      Config.logRoot.info("total income, members = ${0:,.9g}".format(
        np.round(Config.TP.cols.R_total[:][W1].sum(),0).item()))

      W2 = Config.TP.getWhereList("(membership==1) & (work_status >=4)")
      W2c = Config.TP.getWhereList("(work_status >=4)")
      ave_income_working_member = Config.TP.cols.R_total[:][W2].mean()
      
      Config.logRoot.info("mean income, working, county = ${0:,.9g}".format(
        np.round(Config.TP.cols.R_total[:][W2c].mean(),0).item()))
      
      Config.logRoot.info("mean income, working, member = ${0:,.9g}".format(
        np.round(ave_income_working_member,0).item()))
      
      Config.logRoot.info("  percentile of member income= {0:,.4g}".format(
        stats.percentileofscore(Config.TP.cols.R_total[:][W1], ave_income_working_member)))
      
      Config.logRoot.info("  percentile of county income= {0:,.4g}\n".format(
        stats.percentileofscore(Config.TP.cols.R_total[:], ave_income_working_member)))
      

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def loseJobs(self, Year):
    """
    
    Account for job loss for members who hold LFNJs.  Config.risk_job_loss should be set to a value
    that results in about one job loss every five years, on average.
    
    """    
    
    # Do job loss. Only lose jobs for those who did not gain a job in the previous year.
    We1 = Config.TP_old.getWhereList("(work_status >= 6) & (membership==1) & (job_gain==0)")
    np.random.shuffle(We1)    

    job_loss = int(round(We1.size* Config.risk_job_loss))
    Range = We1[0: job_loss]
    self.job_loss[Year] = Range.size
    
    for idd in Range:
      ws = Config.TP.cols.work_status[idd]
      if (ws == 4) or (ws==6):
        Config.TP.cols.R_wages_NP_tokens[idd] = 0
        Config.TP.cols.R_wages_NP_dollars[idd] = 0 
      
      if (ws == 5) or (ws==7):
        Config.TP.cols.R_wages_SB_tokens[idd] = 0
        Config.TP.cols.R_wages_SB_dollars[idd] = 0 
      
      if (ws == 8):
        Config.TP.cols.R_wages_PB_tokens[idd] = 0
        Config.TP.cols.R_wages_PB_dollars[idd] = 0 

      Config.TP.cols.work_status[idd] = 3
      Config.TP.cols.R_gov_support_dollars[idd] = Config.Gov.support_dollars_mean
      Config.TP.cols.base_wage[idd] = Config.Gov.support_dollars_mean
      Config.TP.cols.number_job_losses[idd] += 1
      Config.TP.cols.job_loss[idd] = 1
                  
      assert Config.TP.cols.R_gov_support_dollars[idd] > 0

      # update Persons table
      Config.TP.cols.R_tokens[idd] = Config.TP.cols.R_wages_SB_tokens[idd] + \
        Config.TP.cols.R_wages_PB_tokens[idd] + Config.TP.cols.R_wages_NP_tokens[idd] + \
        Config.TP.cols.R_CBFS_nurture_tokens[idd] 
      
      Config.TP.cols.R_dollars[idd] = Config.TP.cols.R_wages_SB_dollars[idd] + \
        Config.TP.cols.R_wages_PB_dollars[idd] + Config.TP.cols.R_wages_NP_dollars[idd] + \
        Config.TP.cols.R_CBFS_nurture_dollars[idd] + Config.TP.cols.R_gov_support_dollars[idd] 
      
      Config.TP.cols.R_total[idd] = Config.TP.cols.R_tokens[idd] + Config.TP.cols.R_dollars[idd]

            
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def wageOptions(self, Obj, Persons, BaseWage, WorkStatus, Membership, JobLoss, Year, \
    makePayments=False):
    """
    
    Every year, members who receive tokens (employed and LEDDA-supported members) choose one of two Wage
    Options:
      1)  A wage determined by the income target, as specified in Config.
      2)  A wage determined by their base wage plus an incentive, paid in tokens.  The incentive is 
            specified in Config.  
    
    Option 2 is designed to provide a financial gain for every person who joins a LEDDA and receives 
    tokens, regardless of how high their incomes might be.
    
    Calculating the post-CBFS income for the two wage options is complicated by the fact that different
    accounts within the CBFS (nurture_tokens, for example) might receive too many or too few tokens in a 
    year, relative to amount of dollar contributions.  Thus, the CBFS might experience a surplus of 
    unused dollars or tokens at the end of a year.  To remedy this, any surplus of tokens or dollars 
    remaining in CBFS accounts at the end of the year is used up.  (See CBFS.makePayments().)  Also, the
    token share of contributions calculated here is increased slightly over the token share of income so 
    that the contributions made in a year match the token share of income for the following year (when 
    the funds are used).  Lastly, a discount on the dollar share of contributions is provided to account 
    for government contributions in dollars to unemployed and NIWF persons.  Because of the latter 
    adjustment, the post-CBFS income for persons who choose Option 2 might go down slightly from one year
    to the next (say, about 15 dollars + tokens).  The fraction of a LEDDA-supported income that stems 
    from government assistance falls as incomes rise.
    
    A flag is set in Config that allows individuals to make wage option choices, or forces every 
    individual to choose Option 2.  Forcing every individual to choose Option 1 would result in large 
    decreases in post-CBFS income for those who have a high base wage.  Further, the parameter 
    option_1_fraction_allowed, also set in Config, limits the fraction of Option 1 choices in the early
    years of the simulation.  This is to reduce the deficit of dollars that organizations might otherwise
    experience in the early years, when the token share of income is low.
    
    The option makePayments is used to make final payments to the CBFS at the end of each year.  
    
    """

    if Persons.ndim == 1:
      Persons = Persons.reshape(-1,2)
      BaseWage = BaseWage.reshape(-1,2)
      WorkStatus = WorkStatus.reshape(-1,2)
      Membership = Membership.reshape(-1,2)
      JobLoss = JobLoss.reshape(-1,2)
    
    # determine if savings target is met, and calculate fraction of total lending for each type
    Savings = np.column_stack((Config.TP.cols.save_total[:][Persons[:,0]], \
      Config.TP.cols.save_total[:][Persons[:,1]]))
    SavingsMissing = np.maximum(0, Config.earmark_lending_target - Savings) 
    
    EM_lending_total = Config.earmark_lending_SB + Config.earmark_lending_PB + \
      Config.earmark_lending_NP
    if EM_lending_total > 0:
      EM_lending_fraction_SB = Config.earmark_lending_SB / EM_lending_total
      EM_lending_fraction_PB = Config.earmark_lending_PB / EM_lending_total
      EM_lending_fraction_NP = Config.earmark_lending_NP / EM_lending_total
    else:
      EM_lending_fraction_SB = EM_lending_fraction_PB = EM_lending_fraction_NP = 0

    # ------------------------------------------------------------------------------
    # Option 1: base wages on target, both persons choose Option 1
    # ------------------------------------------------------------------------------ 
    
    income_target_tokens_1 = Config.income_target_tokens[Year] * np.ones((Savings.shape[0], 2), 'd')
    income_target_dollars_1 = Config.income_target_dollars[Year] * np.ones((Savings.shape[0], 2), 'd')
    income_target_total_1 = income_target_tokens_1 + income_target_dollars_1

    # lending earmarks (zero if full savings target has been reached)
    EM_Loan_SB_1 = np.minimum((Config.earmark_lending_SB * income_target_total_1), \
      SavingsMissing * EM_lending_fraction_SB)
    EM_Loan_PB_1 = np.minimum((Config.earmark_lending_PB * income_target_total_1), \
      SavingsMissing * EM_lending_fraction_PB)      
    EM_Loan_NP_1 = np.minimum((Config.earmark_lending_NP * income_target_total_1), \
      SavingsMissing * EM_lending_fraction_NP)      

    # non-lending earmarks
    EM_Subsidy_SB_1 = Config.earmark_subsidy_SB * income_target_total_1 
    EM_Subsidy_PB_1 = Config.earmark_subsidy_PB * income_target_total_1 
    EM_Nurture_1 = Config.earmark_nurture * income_target_total_1 
    EM_Donation_NP_1 = Config.earmark_donation_NP * income_target_total_1 

    # remove any benefits and contributions for those who do not receive tokens
    W02 = np.where(((WorkStatus==0) | (WorkStatus==2)) | (Membership==0))  # mx2 array
    income_target_tokens_1[W02] = 0
    income_target_dollars_1[W02] = BaseWage[W02]
    income_target_total_1[W02] = BaseWage[W02]
    
    EM_Loan_SB_1[W02] = EM_Loan_PB_1[W02] = EM_Loan_NP_1[W02] = EM_Subsidy_SB_1[W02] = \
      EM_Subsidy_PB_1[W02] = EM_Nurture_1[W02] = EM_Donation_NP_1[W02] = 0

    # sum of total contributions
    EM_all_1 = EM_Loan_SB_1 + EM_Loan_PB_1 + EM_Loan_NP_1 + EM_Subsidy_SB_1 + EM_Subsidy_PB_1 + \
      EM_Nurture_1 + EM_Donation_NP_1
    
    # get token/dollar split of contributions
    option = 1
    EM_Loan_SB_Tokens_1, EM_Loan_PB_Tokens_1, EM_Loan_NP_Tokens_1, EM_Subsidy_SB_Tokens_1, \
      EM_Subsidy_PB_Tokens_1, EM_Donation_NP_Tokens_1, EM_Nurture_Tokens_1, \
      EM_Loan_SB_Dollars_1, EM_Loan_PB_Dollars_1, EM_Loan_NP_Dollars_1, EM_Subsidy_SB_Dollars_1, \
      EM_Subsidy_PB_Dollars_1, EM_Donation_NP_Dollars_1, EM_Nurture_Dollars_1 = \
      self.initialTokenDollarContributions(EM_Loan_SB_1, EM_Loan_PB_1, EM_Loan_NP_1, \
      EM_Subsidy_SB_1, EM_Subsidy_PB_1, EM_Donation_NP_1, EM_Nurture_1, income_target_tokens_1, \
      income_target_total_1, BaseWage, option, Year)
    
    # post-CBFS family income
    P_CBFS_Tokens_1 = EM_Loan_SB_Tokens_1 + \
      EM_Loan_PB_Tokens_1 + EM_Loan_NP_Tokens_1 + \
      EM_Subsidy_SB_Tokens_1 + EM_Subsidy_PB_Tokens_1 + \
      EM_Nurture_Tokens_1 + EM_Donation_NP_Tokens_1  

    P_CBFS_Dollars_1 = EM_Loan_SB_Dollars_1 + \
      EM_Loan_PB_Dollars_1 + EM_Loan_NP_Dollars_1 + \
      EM_Subsidy_SB_Dollars_1 + EM_Subsidy_PB_Dollars_1 + \
      EM_Nurture_Dollars_1 + EM_Donation_NP_Dollars_1  

    assert np.all(P_CBFS_Tokens_1 + P_CBFS_Dollars_1 <= EM_all_1 + .01)    
    
    R_postCBFS_1 = income_target_total_1 - P_CBFS_Tokens_1 - P_CBFS_Dollars_1      
    assert np.all(R_postCBFS_1 > 0)


    # ------------------------------------------------------------------------------
    # option 2: base wages on incentive (paid 100% in tokens)
    # ------------------------------------------------------------------------------ 

    # Check that TSI for an individual is less than some maximum. In early years, set the maximum lower
    # than in later years.  Here, maximum is based on individual income, but it could also be based
    # on family income.
    max_fraction = (Config.TSI_max + self.share_income_token[Year-1]) / 2.
    max_tokens = BaseWage * max_fraction / (1. - max_fraction)
    
    income_target_tokens_2 = np.minimum(max_tokens, Config.incentive[Year])  # == adjusted incentive 
    income_target_dollars_2 = BaseWage 
    income_target_total_2 =  income_target_tokens_2 + income_target_dollars_2
    assert np.all(income_target_tokens_2 / income_target_total_2 <= max_fraction + .0001)
    
    # lending earmarks 
    EM_Loan_SB_2 = np.minimum((Config.earmark_lending_SB * income_target_tokens_2), \
      SavingsMissing * EM_lending_fraction_SB)
    EM_Loan_PB_2 = np.minimum((Config.earmark_lending_PB * income_target_tokens_2), \
      SavingsMissing * EM_lending_fraction_PB)      
    EM_Loan_NP_2 = np.minimum((Config.earmark_lending_NP * income_target_tokens_2), \
      SavingsMissing * EM_lending_fraction_NP)         

    # non-lending earmarks
    EM_Subsidy_SB_2 = Config.earmark_subsidy_SB * income_target_tokens_2
    EM_Subsidy_PB_2 = Config.earmark_subsidy_PB * income_target_tokens_2
    EM_Nurture_2 = Config.earmark_nurture * income_target_tokens_2
    EM_Donation_NP_2 = Config.earmark_donation_NP * income_target_tokens_2

    # remove any benefits and contributions for those who do not receive tokens
    income_target_tokens_2[W02] = 0
    income_target_dollars_2[W02] = BaseWage[W02]
    income_target_total_2[W02] = BaseWage[W02]

    EM_Loan_SB_2[W02] = EM_Loan_PB_2[W02] = EM_Loan_NP_2[W02] = EM_Subsidy_SB_2[W02] = \
      EM_Subsidy_PB_2[W02] = EM_Nurture_2[W02] = EM_Donation_NP_2[W02] = 0

    # sum of total contributions
    EM_all_2 = EM_Loan_SB_2 + EM_Loan_PB_2 + EM_Loan_NP_2 + EM_Subsidy_SB_2 + EM_Subsidy_PB_2 + \
      EM_Nurture_2 + EM_Donation_NP_2
    assert np.all(income_target_total_2 - EM_all_2 >= BaseWage)

    # get token/dollar split of contributions
    option = 2
    EM_Loan_SB_Tokens_2, EM_Loan_PB_Tokens_2, EM_Loan_NP_Tokens_2, EM_Subsidy_SB_Tokens_2, \
      EM_Subsidy_PB_Tokens_2, EM_Donation_NP_Tokens_2, EM_Nurture_Tokens_2, \
      EM_Loan_SB_Dollars_2, EM_Loan_PB_Dollars_2, EM_Loan_NP_Dollars_2, EM_Subsidy_SB_Dollars_2, \
      EM_Subsidy_PB_Dollars_2, EM_Donation_NP_Dollars_2, EM_Nurture_Dollars_2 = \
      self.initialTokenDollarContributions(EM_Loan_SB_2, EM_Loan_PB_2, EM_Loan_NP_2, \
      EM_Subsidy_SB_2, EM_Subsidy_PB_2, EM_Donation_NP_2, EM_Nurture_2, income_target_tokens_2, \
      income_target_total_2, BaseWage, option, Year)

    # post-CBFS income
    P_CBFS_Tokens_2 = EM_Loan_SB_Tokens_2 + \
      EM_Loan_PB_Tokens_2 + EM_Loan_NP_Tokens_2 + \
      EM_Subsidy_SB_Tokens_2 + EM_Subsidy_PB_Tokens_2 + \
      EM_Nurture_Tokens_2 + EM_Donation_NP_Tokens_2  

    P_CBFS_Dollars_2 = EM_Loan_SB_Dollars_2 + \
      EM_Loan_PB_Dollars_2 + EM_Loan_NP_Dollars_2 + \
      EM_Subsidy_SB_Dollars_2 + EM_Subsidy_PB_Dollars_2 + \
      EM_Nurture_Dollars_2 + EM_Donation_NP_Dollars_2  

    assert np.all(P_CBFS_Tokens_2 + P_CBFS_Dollars_2 <= EM_all_2 + .01)
    
    R_postCBFS_2 = income_target_total_2 - P_CBFS_Tokens_2 - P_CBFS_Dollars_2   
    assert np.all(R_postCBFS_2 > 0)  
    assert np.all(R_postCBFS_2 >= BaseWage)  

    
    # ------------------------------------------------------------------------------
    # choose wage option
    # ------------------------------------------------------------------------------ 

    Families = Config.TP.cols.fid[:][Persons[:,0]]
    
    # If makePayments==True, use wage_selector as saved in TP table, or else the wage_selector for some 
    # individuals, switched below from Option 1 to Option 2, will not match the incentive in the TP
    # table, and post-CBFS incomes stored in the TP table will not match those calculated here. 
    if makePayments==True:
      wage_selector = np.column_stack((Config.TP.cols.wage_option[:][Persons[:,0]], \
        Config.TP.cols.wage_option[:][Persons[:,1]]))
      Wn = np.where((wage_selector[:,0] != 0) & (wage_selector[:,1] != 0))[0]
      assert np.all(wage_selector[Wn,0] == wage_selector[Wn,1]) 
      wage_selector = np.maximum(wage_selector[:,0], wage_selector[:,1])  # use 1d array 
      assert np.all(wage_selector>0)

      # make sure that families with one token-earner choose Option 2
      uW02 = np.unique(W02[0])
      assert np.all(wage_selector[uW02] == 2)
    
    else:
      if Config.wageSelectorFlag == 2:
        # all individuals choose option 2
        wage_selector = 2 * np.ones((BaseWage.shape[0]),'i')

      elif Config.wageSelectorFlag == 0:
        # Allow families to choose most advantageous wage option.  However, employed persons who
        # once choose Option 1 must continue to choose Option 1 (see Cbfs.caseFunding()) and both persons
        # must choose Option 1 or both must choose Option 2.
        wage_selector = (R_postCBFS_2.sum(1) > R_postCBFS_1.sum(1))   # 1D array
        wage_selector = wage_selector.astype('i') + 1
        assert np.all(wage_selector>0)
                
        # make sure that single members choose Option 2
        uW02 = np.unique(W02[0])
        wage_selector[uW02] = 2

        # Allow only a fraction of desired Option 1 choices in early years.  This reduces the dollar
        # deficit experienced by organizations.  Give preference for Option 1 to those with lowest base 
        # wage.  Force the choice for the same set of families from year to year, or else incomes
        # for some individuals will fall or rise substantially from year to year.  
        if (Config.families_protected_from_Option2_force is None) and \
          (Config.option_1_fraction_allowed[Year] < 1):
          # choose initial set of families who will have forced selections
          id1 = np.where(wage_selector == 1)[0]
          order = np.argsort(BaseWage.sum(1)[id1])[::-1]
          new = id1[order]
          switch = new[0: int(round(id1.size * (1-Config.option_1_fraction_allowed[Year])))]
          wage_selector[switch] = 2
          Config.forced_option_2_families = Families[switch]
          
          Config.logRoot.debug("\nInitial number of families switched to Option 2 = {0:d}.\n".format(
            switch.size))
          
          Wns = np.where(wage_selector==1)[0]
          
          if Wns.size > 0:
            Config.families_protected_from_Option2_force = Families[Wns]
        
        elif Config.option_1_fraction_allowed[Year] < 1:
          # choose from those families who already have been forced, adding more when needed who are \
          # making their choice for the first time
          id1 = np.where(wage_selector == 1)[0]
          families_choosing_1 = Families[id1]
          protected = Config.families_protected_from_Option2_force
          
          # Remove any families that have chosen Option 1 in the past. 
          families_choosing_1 = np.setdiff1d(families_choosing_1, protected, 
            assume_unique=True)
          
          # order forced families by base wage
          familyBaseWage = np.zeros((families_choosing_1.size),'d')
          for ii, family in enumerate(families_choosing_1):
            W = np.where(Families==family)[0]
            familyBaseWage[ii] = BaseWage[W].sum() 
            
          order = np.argsort(familyBaseWage)[::-1]
          families_choosing_1 = families_choosing_1[order]
          
          switch = families_choosing_1[0: int(round(
            id1.size * (1-Config.option_1_fraction_allowed[Year])))]
          
          for ii, family in enumerate(switch):
            W = np.where(Families==family)[0]          
            wage_selector[W] = 2

          if switch.size > 0:
            W1 = Config.TF.getWhereList("membership ==1")
            Config.logRoot.debug(("\nNumber of families switched to Option 2= {0:d}.  Percent of " + \
              "member families protected= {1:.3g}\n").format(
              switch.size, 
              protected.size / float(W1.size)))
          
          Wns = np.where(wage_selector==1)[0]
          Config.families_protected_from_Option2_force = np.union1d(protected, Families[Wns])
      
      else:
        Config.logRoot.info("\nSet Config.wageSelectorFlag ==0 or ==2 and run simulation again.\n")
        sys.exit()  

      
    # ------------------------------------------------------------------------------
    # combine preliminary, basic results for both options in arrays
    # ------------------------------------------------------------------------------ 

    # set up arrays to hold basic results
    Wages_Tokens = np.zeros_like(BaseWage)
    Wages_Dollars = np.zeros_like(BaseWage)
    Wage_Option = np.zeros_like(BaseWage).astype('i')
    R_PostCBFS = np.zeros_like(BaseWage)

    # set incomes based on wage selector
    W1 = np.where(wage_selector == 1)[0]
    Wages_Tokens[W1] = income_target_tokens_1[W1]
    Wages_Dollars[W1] = income_target_dollars_1[W1] 
    Wage_Option[W1] = 1
    R_PostCBFS[W1] = R_postCBFS_1[W1]

    W2 = np.where(wage_selector == 2)[0]
    Wages_Tokens[W2] = income_target_tokens_2[W2] 
    Wages_Dollars[W2] = income_target_dollars_2[W2] 
    Wage_Option[W2] = 2
    R_PostCBFS[W2] = R_postCBFS_2[W2]
    
    Wages_Total = Wages_Tokens + Wages_Dollars
    
    if Year >= Config.burn_in_period:
      assert np.all(Wages_Tokens==0)==False
            
    W02b = np.where((WorkStatus!=0) & (WorkStatus!=2) & (Membership==1) & (Wage_Option==1))  # mx2 array
    assert np.all(Wages_Dollars[W02b] == Config.income_target_dollars[Year])
   
    # Determine if family income has increased, considering wage base used.  Allow for ~$25 loss to 
    # cover the case where a small income gain for one partner, who has a tiny base wage, does not 
    # compensate for a small income loss due to changes in factor_gov_support for the other partner, who 
    # has a high income and chooses Option 2. 
    postCBFS_old = np.column_stack((Config.TP_old.cols.R_postCBFS_total[:][Persons[:,0]], \
        Config.TP_old.cols.R_postCBFS_total[:][Persons[:,1]]))
    
    Income_Increase = (R_PostCBFS.sum(1) >= postCBFS_old.sum(1) - 25)  # 1d array

    if makePayments==True:
      # Check any decrease in family income.  
      BaseWage_old = np.column_stack((Config.TP_old.cols.base_wage[:][Persons[:,0]], \
          Config.TP_old.cols.base_wage[:][Persons[:,1]]))
      JL = JobLoss.sum(1)
      delta = R_PostCBFS.sum(1) - postCBFS_old.sum(1)
      
      Wloss = np.where((JL==0) & (delta < -60) & (BaseWage[:,0]>=BaseWage_old[:,0]) & \
        (BaseWage[:,1]>=BaseWage_old[:,1]))[0]
      
      if Wloss.size > 0:
        
        Config.logRoot.debug(("\nPost-CBFS family income loss, year-to-year, min= {0:,.9g}, " + \
          " size(loss > $50)= {1:,d}, mean loss= {2:,.9g}\n").format(
          np.round(delta[Wloss].min(),0).item(),
          Wloss.size,
          np.round(delta[Wloss].mean(),0).item()))
          
        BaseWage_0 = np.column_stack((Config.TP0.cols.base_wage[:][Persons[:,0]], \
          Config.TP0.cols.base_wage[:][Persons[:,1]]))
        # make sure that no loss is seen compared to orignal base wage (unless a person lost a job)
        assert np.all(R_PostCBFS[Wloss].sum(1) > BaseWage_0[Wloss].sum(1))
        
        assert Wloss.size == 0

    
    if makePayments==False:
      # R_PostCBFS is preliminary
      return Wages_Tokens, Wages_Dollars, Wage_Option, R_PostCBFS, Income_Increase
    
    else:
      # ------------------------------------------------------------------------------
      # setup token/dollar contribution arrays
      # ------------------------------------------------------------------------------ 

      # make arrays to hold contributions
      EM_Loan_SB_Tokens = np.zeros_like(BaseWage)
      EM_Loan_PB_Tokens = np.zeros_like(BaseWage)
      EM_Loan_NP_Tokens = np.zeros_like(BaseWage)
      EM_Subsidy_SB_Tokens = np.zeros_like(BaseWage)
      EM_Subsidy_PB_Tokens = np.zeros_like(BaseWage)
      EM_Nurture_Tokens = np.zeros_like(BaseWage)
      EM_Donation_NP_Tokens = np.zeros_like(BaseWage)  

      EM_Loan_SB_Dollars = np.zeros_like(BaseWage)
      EM_Loan_PB_Dollars = np.zeros_like(BaseWage)
      EM_Loan_NP_Dollars = np.zeros_like(BaseWage)
      EM_Subsidy_SB_Dollars = np.zeros_like(BaseWage)
      EM_Subsidy_PB_Dollars = np.zeros_like(BaseWage)
      EM_Nurture_Dollars = np.zeros_like(BaseWage)
      EM_Donation_NP_Dollars = np.zeros_like(BaseWage)  

      # option 1 selected
      W1 = np.where(wage_selector == 1)[0]
      EM_Loan_SB_Tokens[W1] = EM_Loan_SB_Tokens_1[W1]
      EM_Loan_PB_Tokens[W1] = EM_Loan_PB_Tokens_1[W1]
      EM_Loan_NP_Tokens[W1] = EM_Loan_NP_Tokens_1[W1]
      EM_Subsidy_SB_Tokens[W1] = EM_Subsidy_SB_Tokens_1[W1]
      EM_Subsidy_PB_Tokens[W1] = EM_Subsidy_PB_Tokens_1[W1]
      EM_Nurture_Tokens[W1] = EM_Nurture_Tokens_1[W1]
      EM_Donation_NP_Tokens[W1] = EM_Donation_NP_Tokens_1[W1]

      EM_Loan_SB_Dollars[W1] = EM_Loan_SB_Dollars_1[W1]
      EM_Loan_PB_Dollars[W1] = EM_Loan_PB_Dollars_1[W1]
      EM_Loan_NP_Dollars[W1] = EM_Loan_NP_Dollars_1[W1]
      EM_Subsidy_SB_Dollars[W1] = EM_Subsidy_SB_Dollars_1[W1]
      EM_Subsidy_PB_Dollars[W1] = EM_Subsidy_PB_Dollars_1[W1]
      EM_Nurture_Dollars[W1] = EM_Nurture_Dollars_1[W1]
      EM_Donation_NP_Dollars[W1] = EM_Donation_NP_Dollars_1[W1]

      # option 2 selected
      W2 = np.where(wage_selector == 2)[0]
      EM_Loan_SB_Tokens[W2] = EM_Loan_SB_Tokens_2[W2]
      EM_Loan_PB_Tokens[W2] = EM_Loan_PB_Tokens_2[W2]
      EM_Loan_NP_Tokens[W2] = EM_Loan_NP_Tokens_2[W2]
      EM_Subsidy_SB_Tokens[W2] = EM_Subsidy_SB_Tokens_2[W2]
      EM_Subsidy_PB_Tokens[W2] = EM_Subsidy_PB_Tokens_2[W2]
      EM_Nurture_Tokens[W2] = EM_Nurture_Tokens_2[W2]
      EM_Donation_NP_Tokens[W2] = EM_Donation_NP_Tokens_2[W2]

      EM_Loan_SB_Dollars[W2] = EM_Loan_SB_Dollars_2[W2]
      EM_Loan_PB_Dollars[W2] = EM_Loan_PB_Dollars_2[W2]
      EM_Loan_NP_Dollars[W2] = EM_Loan_NP_Dollars_2[W2]
      EM_Subsidy_SB_Dollars[W2] = EM_Subsidy_SB_Dollars_2[W2]
      EM_Subsidy_PB_Dollars[W2] = EM_Subsidy_PB_Dollars_2[W2]
      EM_Nurture_Dollars[W2] = EM_Nurture_Dollars_2[W2]
      EM_Donation_NP_Dollars[W2] = EM_Donation_NP_Dollars_2[W2]

      # ------------------------------------------------------------------------------
      # update Persons table 
      # ------------------------------------------------------------------------------ 

      # Save old version of R_postCBFS to make make sure that income & CBFS contributions calculated 
      # earlier in the year match with those made at the end of the year.
      Config.TP.cols.R_postCBFS_total_prelim[:] = Config.TP.cols.R_postCBFS_total[:]

      # update TP savings
      P_CBFS_lending_tokens = EM_Loan_SB_Tokens + \
        EM_Loan_PB_Tokens + EM_Loan_NP_Tokens
      
      P_CBFS_lending_dollars = EM_Loan_SB_Dollars + \
        EM_Loan_PB_Dollars + EM_Loan_NP_Dollars 

      Wp0 = np.where((WorkStatus[:,0] != 0) & (WorkStatus[:,0] != 2) & (Membership[:,0]== 1))[0]
      Wp1 = np.where((WorkStatus[:,1] != 0) & (WorkStatus[:,1] != 2) & (Membership[:,1]== 1))[0]

      for jj, Range in enumerate([Wp0, Wp1]): 
        for ii in Range:
          rowID = Persons[ii,jj]

          # CBFS raw, tokens
          Config.TP.cols.P_CBFS_loan_SB_tokens[rowID] = EM_Loan_SB_Tokens[ii][jj]
          Config.TP.cols.P_CBFS_loan_PB_tokens[rowID] = EM_Loan_PB_Tokens[ii][jj] 
          Config.TP.cols.P_CBFS_loan_NP_tokens[rowID] = EM_Loan_NP_Tokens[ii][jj] 
          Config.TP.cols.P_CBFS_subsidy_SB_tokens[rowID] = EM_Subsidy_SB_Tokens[ii][jj] 
          Config.TP.cols.P_CBFS_subsidy_PB_tokens[rowID] = EM_Subsidy_PB_Tokens[ii][jj] 
          Config.TP.cols.P_CBFS_donation_NP_tokens[rowID] = EM_Donation_NP_Tokens[ii][jj] 
          Config.TP.cols.P_CBFS_nurture_tokens[rowID] = EM_Nurture_Tokens[ii][jj]

          # CBFS raw, dollars
          Config.TP.cols.P_CBFS_loan_SB_dollars[rowID] = EM_Loan_SB_Dollars[ii][jj]
          Config.TP.cols.P_CBFS_loan_PB_dollars[rowID] = EM_Loan_PB_Dollars[ii][jj] 
          Config.TP.cols.P_CBFS_loan_NP_dollars[rowID] = EM_Loan_NP_Dollars[ii][jj]
          Config.TP.cols.P_CBFS_subsidy_SB_dollars[rowID] = EM_Subsidy_SB_Dollars[ii][jj]
          Config.TP.cols.P_CBFS_subsidy_PB_dollars[rowID] = EM_Subsidy_PB_Dollars[ii][jj]
          Config.TP.cols.P_CBFS_donation_NP_dollars[rowID] = EM_Donation_NP_Dollars[ii][jj]
          Config.TP.cols.P_CBFS_nurture_dollars[rowID] = EM_Nurture_Dollars[ii][jj]

          Config.TP.cols.P_CBFS_tokens[rowID] = EM_Loan_SB_Tokens[ii][jj] + \
            EM_Loan_PB_Tokens[ii][jj] + EM_Loan_NP_Tokens[ii][jj] + \
            EM_Subsidy_SB_Tokens[ii][jj] + EM_Subsidy_PB_Tokens[ii][jj] + \
            EM_Nurture_Tokens[ii][jj] + EM_Donation_NP_Tokens[ii][jj]  

          Config.TP.cols.P_CBFS_dollars[rowID] = EM_Loan_SB_Dollars[ii][jj] + \
            EM_Loan_PB_Dollars[ii][jj] + EM_Loan_NP_Dollars[ii][jj] + \
            EM_Subsidy_SB_Dollars[ii][jj] + EM_Subsidy_PB_Dollars[ii][jj] + \
            EM_Nurture_Dollars[ii][jj] + EM_Donation_NP_Dollars[ii][jj]  
            
          Config.TP.cols.P_CBFS_total[rowID] = Config.TP.cols.P_CBFS_tokens[rowID] + \
            Config.TP.cols.P_CBFS_dollars[rowID]        

          Config.TP.cols.R_postCBFS_tokens[rowID] = Config.TP.cols.R_tokens[rowID] - \
            Config.TP.cols.P_CBFS_tokens[rowID]
          Config.TP.cols.R_postCBFS_dollars[rowID] = Config.TP.cols.R_dollars[rowID] - \
            Config.TP.cols.P_CBFS_dollars[rowID]
          Config.TP.cols.R_postCBFS_total[rowID] = Config.TP.cols.R_total[rowID] - \
            Config.TP.cols.P_CBFS_total[rowID]

          # savings
          Config.TP.cols.save_tokens[rowID] += P_CBFS_lending_tokens[ii][jj]
          Config.TP.cols.save_dollars[rowID] += P_CBFS_lending_dollars[ii][jj]
          Config.TP.cols.save_total[rowID] = Config.TP.cols.save_tokens[rowID] + \
            Config.TP.cols.save_dollars[rowID]
          
      # account for savings loss due to dollar inflation
      Config.Ledda.dollar_loss_inflation[Year] = Config.TP.cols.save_dollars[:].sum() * \
        Config.rate_inflation_dollar
      Config.TP.cols.save_dollars[:] *= (1. - Config.rate_inflation_dollar)
      Config.TP.cols.save_total[:] = Config.TP.cols.save_tokens[:] + Config.TP.cols.save_dollars[:]

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

      assert np.all(Config.TP.cols.P_CBFS_loan_SB_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_loan_PB_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_loan_NP_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_subsidy_SB_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_subsidy_PB_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_donation_NP_tokens[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_nurture_tokens[:] >= 0)

      assert np.all(Config.TP.cols.P_CBFS_loan_SB_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_loan_PB_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_loan_NP_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_subsidy_SB_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_subsidy_PB_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_donation_NP_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_nurture_dollars[:] >= 0)

      assert np.all(Config.TP.cols.P_CBFS_tokens[:] >= 0)
      
      assert np.all(Config.TP.cols.P_CBFS_dollars[:] >= 0)
      assert np.all(Config.TP.cols.P_CBFS_tokens[:] >= 0)
      
      assert np.all(Config.TP.cols.R_postCBFS_tokens[:] >= 0)
      assert np.all(Config.TP.cols.R_postCBFS_dollars[:] >= 0)
      assert np.all(Config.TP.cols.R_postCBFS_total[:] >= Config.TP.cols.R_postCBFS_total_prelim[:] - .01)
      
      Wr = Config.TP.getWhereList("R_tokens >0")
      Wr0 = Config.TP_old.getWhereList("R_tokens >0")
      assert Wr.size >= Wr0.size
      Wr = Config.TP.getWhereList("(work_status==1) & (R_CBFS_nurture_tokens >0)")
      Wr0 = Config.TP_old.getWhereList("(work_status==1) & (R_CBFS_nurture_tokens >0)")
      assert Wr.size >= Wr0.size
      
      # ------------------------------------------------------------------------------
      # update Persons arrays
      # ------------------------------------------------------------------------------ 
      
      # CBFS raw, tokens
      Config.Persons.P_CBFS_loan_SB_tokens[Year] = Config.TP.cols.P_CBFS_loan_SB_tokens[:].sum() 
      Config.Persons.P_CBFS_loan_PB_tokens[Year] = Config.TP.cols.P_CBFS_loan_PB_tokens[:].sum() 
      Config.Persons.P_CBFS_loan_NP_tokens[Year] = Config.TP.cols.P_CBFS_loan_NP_tokens[:].sum() 
      Config.Persons.P_CBFS_subsidy_SB_tokens[Year] = Config.TP.cols.P_CBFS_subsidy_SB_tokens[:].sum() 
      Config.Persons.P_CBFS_subsidy_PB_tokens[Year] = Config.TP.cols.P_CBFS_subsidy_PB_tokens[:].sum() 
      Config.Persons.P_CBFS_donation_NP_tokens[Year] = Config.TP.cols.P_CBFS_donation_NP_tokens[:].sum() 
      Config.Persons.P_CBFS_nurture_tokens[Year] = Config.TP.cols.P_CBFS_nurture_tokens[:].sum() 

      # CBFS raw, dollars
      Config.Persons.P_CBFS_loan_SB_dollars[Year] = Config.TP.cols.P_CBFS_loan_SB_dollars[:].sum() 
      Config.Persons.P_CBFS_loan_PB_dollars[Year] = Config.TP.cols.P_CBFS_loan_PB_dollars[:].sum() 
      Config.Persons.P_CBFS_loan_NP_dollars[Year] = Config.TP.cols.P_CBFS_loan_NP_dollars[:].sum() 
      Config.Persons.P_CBFS_subsidy_SB_dollars[Year] = Config.TP.cols.P_CBFS_subsidy_SB_dollars[:].sum() 
      Config.Persons.P_CBFS_subsidy_PB_dollars[Year] = Config.TP.cols.P_CBFS_subsidy_PB_dollars[:].sum() 
      Config.Persons.P_CBFS_donation_NP_dollars[Year] = \
        Config.TP.cols.P_CBFS_donation_NP_dollars[:].sum() 
      Config.Persons.P_CBFS_nurture_dollars[Year] = Config.TP.cols.P_CBFS_nurture_dollars[:].sum() 

      Config.Persons.CBFS_save_tokens[Year] = Config.TP.cols.save_tokens[:].sum()
      Config.Persons.CBFS_save_dollars[Year] = Config.TP.cols.save_dollars[:].sum()
      Config.Persons.CBFS_save_total[Year] = Config.TP.cols.save_total[:].sum()

    
  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++    
  def initialTokenDollarContributions(self, EM_Loan_SB, EM_Loan_PB, EM_Loan_NP, EM_Subsidy_SB, \
    EM_Subsidy_PB, EM_Donation_NP, EM_Nurture, income_target_tokens, income_target_total, baseWage, \
    option, Year):
    """
    
    Estimate the token vs dollar contributions to the different CBFS accounts based on token shares of 
    income, with some adjustment.  The goal is to calculate an adjustment that produces the smallest 
    unused residual in each CBFS account at the end of the year.  For example, if too many dollars are
    contributed relative to tokens, then after new jobs or support are offered in the following year (at 
    some specified token/dollar ratio), an excess of dollars would remain in the account.  In general, 
    amount remaining in a CBFS account will depend on the income target and the token share of income, 
    which is affected by the percentage of individuals who choose wage Option 1 vs. Option 2, and, for 
    the nurture account, by the percent of income target provided by government assistance.  The latter 
    falls every year as incomes rise (and government assistance per person remains steady).
    
    Note that token shares of contributions is less volatile in the early years if the TSI in the 
    early years is made more smooth (such as by gradually increasing the incentive in the early years).  
    
    """
    
    assert type(EM_Loan_SB) == type( np.arange(1))
      
    # Set up arrays to hold token and dollar contributions.  These are all nx2 arrays.
    EM_Loan_SB_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Loan_PB_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Loan_NP_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Loan_SB_Dollars = np.zeros_like(EM_Loan_SB)
    EM_Loan_PB_Dollars = np.zeros_like(EM_Loan_SB)
    EM_Loan_NP_Dollars = np.zeros_like(EM_Loan_SB)
    
    EM_Subsidy_SB_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Subsidy_SB_Dollars = np.zeros_like(EM_Loan_SB)
    EM_Subsidy_PB_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Subsidy_PB_Dollars = np.zeros_like(EM_Loan_SB)
    EM_Nurture_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Nurture_Dollars = np.zeros_like(EM_Loan_SB)
    EM_Donation_NP_Tokens = np.zeros_like(EM_Loan_SB)
    EM_Donation_NP_Dollars = np.zeros_like(EM_Loan_SB)
    
    # Set the token share for each earmark for each individual at his or her TSI, with some reduction
    # to the dollar share so that: (1) token shares in next year's pools reflect next year's TSI, and (2) 
    # changes in the fraction of income paid by government assistance (for unemployed and NIWF members) 
    # is taken into account.
    
    TSI = income_target_tokens / income_target_total
    
    # the TS adjustment will not work well if only Option 2 is allowed (TSI will not follow target well)
    if Config.wageSelectorFlag == 2:
      TS = TSI.copy()
      DS = 1 - TS
    else:
      TS_next = Config.income_target_tokens[Year+1] / Config.income_target_total[Year+1]
      TS_now = Config.income_target_tokens[Year] / Config.income_target_total[Year]
      if TS_now==0:
        factor_growth = 1
      else:
        factor_growth = max(1, TS_next / TS_now)
      TS = np.zeros_like(TSI)

      if option == 1:
        TS = TSI * min(Config.limit_TS_contrib, factor_growth)  
      else:
        # Option 2:
        # Those with a low base wage should not contribute too high a share of tokens, or they will 
        # contribute more tokens than the receive. The break point is fixed at 15000 here, which is 
        # conservative if the incentive is not extreme.  It can be adjusted to ensure positive tokens, as 
        # can the multipliers used below (one of which is set in Config). If the multipliers  are too 
        # low, the token share of contributions will be too low to match the TSI of the next year, 
        # assuming that next year's TSI is higher than the current one. 

        Wl = np.where(baseWage < 15000)  # these are mx2 arrays
        Wh = np.where(baseWage >= 15000)
        
        TS[Wl] = TSI[Wl] * 1.0   # factor of 1.0 assures TS will match TSI in late simulation years
        
        TS[Wh] = TSI[Wh] * min(Config.limit_TS_contrib, factor_growth)  
      
      Config.Cbfs.factor_growth[Year] = factor_growth
      
    DS = 1 - TS  
    
    # A discount should be given for dollar nurture contributions or else the nurture fund will have
    # too many dollars (due to government assistance in dollars).  
    factor_gov_support = Config.Gov.support_dollars_mean / Config.income_target_dollars[Year+1]
    DS_nurture = DS * (1-factor_gov_support)
    
    # The following can be used for checking results.  
    if 1==2:
      DS_nurture = DS

    # use token shares to estimate token and dollar contributions for each CBFS account
    
    EM_Loan_SB_Tokens = EM_Loan_SB * TS
    EM_Loan_SB_Dollars = EM_Loan_SB * DS
    assert np.all(EM_Loan_SB_Tokens + EM_Loan_SB_Dollars <= EM_Loan_SB + .01)
          
    EM_Loan_PB_Tokens = EM_Loan_PB * TS
    EM_Loan_PB_Dollars = EM_Loan_PB * DS

    EM_Loan_NP_Tokens = EM_Loan_NP * TS
    EM_Loan_NP_Dollars = EM_Loan_NP * DS
    
    EM_Subsidy_SB_Tokens = EM_Subsidy_SB * TS
    EM_Subsidy_SB_Dollars = EM_Subsidy_SB * DS

    EM_Subsidy_PB_Tokens = EM_Subsidy_PB * TS
    EM_Subsidy_PB_Dollars = EM_Subsidy_PB * DS
          
    EM_Donation_NP_Tokens = EM_Donation_NP * TS 
    EM_Donation_NP_Dollars = EM_Donation_NP * DS
    
    EM_Nurture_Tokens = EM_Nurture * TS 
    EM_Nurture_Dollars = EM_Nurture * DS_nurture 
    assert np.all(EM_Nurture_Tokens + EM_Nurture_Dollars <= EM_Nurture + .01)
    
    # record DS
    W = np.where(TS > 0)  # this is size mx2
    if (W[0].size > 0) and (option==1):
      Config.Cbfs.DS_contrib[Year] = DS[W].mean()
      Config.Cbfs.DS_contrib_nurture[Year] = DS_nurture[W].mean()
      Config.Cbfs.TS_contrib[Year] = TS[W].mean()
    
    Config.Cbfs.factor_gov_support[Year] = factor_gov_support
    
    # checks
    EM_tokens = EM_Loan_SB_Tokens + EM_Loan_PB_Tokens + EM_Loan_NP_Tokens + EM_Subsidy_SB_Tokens + \
      EM_Subsidy_PB_Tokens + EM_Donation_NP_Tokens + EM_Nurture_Tokens    
    EM_dollars = EM_Loan_SB_Dollars + EM_Loan_PB_Dollars + EM_Loan_NP_Dollars + EM_Subsidy_SB_Dollars + \
      EM_Subsidy_PB_Dollars + EM_Donation_NP_Dollars + EM_Nurture_Dollars
    
    # check
    if np.all(EM_tokens <= income_target_tokens) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError     

    if np.all(EM_dollars <= (income_target_total - income_target_tokens)) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError    
    
    return EM_Loan_SB_Tokens, EM_Loan_PB_Tokens, EM_Loan_NP_Tokens, EM_Subsidy_SB_Tokens, \
      EM_Subsidy_PB_Tokens, EM_Donation_NP_Tokens, EM_Nurture_Tokens, \
      EM_Loan_SB_Dollars, EM_Loan_PB_Dollars, EM_Loan_NP_Dollars, EM_Subsidy_SB_Dollars, \
      EM_Subsidy_PB_Dollars, EM_Donation_NP_Dollars, EM_Nurture_Dollars


  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def updateLedda(self, Year):  
    """
    
    Update Ledda arrays at the end of the year.
    
    """      
    
    # income total
    W1 = Config.TP.getWhereList("membership==1")
    
    if W1.size ==0:
      return
      
    self.R_dollars[Year] = Config.TP.cols.R_dollars[:][W1].sum()
    self.R_tokens[Year] = Config.TP.cols.R_tokens[:][W1].sum()
    self.R_total[Year] = Config.TP.cols.R_total[:][W1].sum()
    
    # wage option, etc.  
    self.base_wage_mean[Year] = Config.TP.cols.base_wage[:][W1].mean()
    self.R_postCBFS_mean[Year] = Config.TP.cols.R_postCBFS_total[:][W1].mean()
    W14 = Config.TP.getWhereList("(membership==1) & (work_status >=4)")
    self.wage_option_working_mean[Year] = Config.TP.cols.wage_option[:][W14].mean()
    
    Wi = Config.TP.getWhereList("(membership==1) & (wage_option >0)")
    if Wi.size > 0:
      self.wage_option_mean[Year] = Config.TP.cols.wage_option[:][Wi].mean()
    
    # Mean number of LFNJs held over previous five years.
    childs = Config.HDF5.root._v_children.keys()
    childs = [name for name in childs if 'Person' in name]
    childs.sort()
    childs = childs[-5:] 
    W5 = Config.HDF5.root._f_getChild(childs[0]).getWhereList("(number_job_gains > 0)")
    if W5.size > 0:
      jobLoss = np.zeros((W5.size, 1),'d')
      for ic, c in enumerate(childs):
        jobLoss[:,0] += Config.HDF5.root._f_getChild(c).cols.job_loss[:][W5]
      self.job_loss_mean[Year] = jobLoss.mean()
      
    # post-CBFS family income
    W1 = Config.TF.getWhereList("membership==1")
    self.post_CBFS_family_income_tokens_mean[Year] = (Config.TF.cols.R_tokens[:][W1] - \
      Config.TF.cols.P_CBFS_tokens[:][W1]).mean()
    self.post_CBFS_family_income_dollars_mean[Year] = (Config.TF.cols.R_dollars[:][W1] - \
      Config.TF.cols.P_CBFS_dollars[:][W1]).mean()
    self.post_CBFS_family_income_total_mean[Year] = (Config.TF.cols.R_total[:][W1] - \
      Config.TF.cols.P_CBFS_total[:][W1]).mean()

    self.post_CBFS_family_income_tokens_plus_savings_mean[Year] = (Config.TF.cols.R_tokens[:][W1] - \
      Config.TF.cols.P_CBFS_tokens[:][W1] + Config.TF.cols.save_tokens[:][W1]).mean()
    self.post_CBFS_family_income_dollars_plus_savings_mean[Year] = (Config.TF.cols.R_dollars[:][W1] - \
      Config.TF.cols.P_CBFS_dollars[:][W1] + Config.TF.cols.save_dollars[:][W1]).mean()      
    self.post_CBFS_family_income_total_plus_savings_mean[Year] = (Config.TF.cols.R_total[:][W1] - \
      Config.TF.cols.P_CBFS_total[:][W1] + Config.TF.cols.save_total[:][W1]).mean()
    
    Wr = Config.TP.getWhereList("R_tokens > 0")
    if Wr.size > 0:
      
      # share spending
      self.share_spending_token[Year] = Config.TP.cols.P_spending_tokens[:][Wr].sum() / \
        (Config.TP.cols.P_spending_tokens[:][Wr].sum() + Config.TP.cols.P_spending_dollars[:][Wr].sum()) 

      # CBFS contributions
      self.mean_CBFS_contrib[Year] = Config.TP.cols.P_CBFS_total[:][Wr].mean() 
      self.mean_CBFS_contrib_income_ratio[Year] = \
        (Config.TP.cols.P_CBFS_total[:][Wr] / Config.TP.cols.R_total[:][Wr]).mean()
    
    # option 1
    Wi1 = Config.TP.getWhereList("wage_option==1")
    Wi2 = Config.TP.getWhereList("wage_option==2")
    if (Wi1.size >0) or (Wi2.size >0):
      self.option_1_ratio[Year] =  Wi1.size / float(Wi1.size + Wi2.size)  
      self.option_1_sum[Year] = Config.TP.cols.P_CBFS_total[:][Wi1].sum()  
      self.option_1_nurture_sum[Year] = Config.TP.cols.P_CBFS_nurture_tokens[:][Wi1].sum() + \
        Config.TP.cols.P_CBFS_nurture_dollars[:][Wi1].sum()
    

  # +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
  def updateUnemployment(self, Year):
    """
    
    Update unemployment information at the end of the year.
    
    """
    
    if Year == 0:
      Config.TP_old = Config.TP
      Config.TF_old = Config.TF
    else:
      # old TP and TF objects have already been set
      pass
    
    Config.County.number_employed[Year] = Config.TP.getWhereList("work_status >=4").size
    Config.County.number_unemployed[Year] = Config.TP.getWhereList("(work_status==2) | (work_status==3)").size
    
    assert np.allclose(Config.County.number_employed[Year] + Config.County.number_unemployed[Year], \
      Config.rate_labor_participation * Config.adult_county_population, atol=1)
            
    if Year >= Config.burn_in_period-1:
      Wu1 = Config.TP.getWhereList("((work_status==2) | (work_status==3)) & (membership==1)").size
      We41 = Config.TP.getWhereList("(work_status >=4) & (membership==1)").size
      self.rate_unemployment[Year] = Wu1/float(Wu1 + We41)

    Wu = Config.TP.getWhereList("((work_status==2) | (work_status==3))").size
    W4 = Config.TP.getWhereList("(work_status >=4)").size
    Config.County.rate_unemployment[Year] = Wu/float(Wu + W4)
    
    We = Config.TP.getWhereList("(work_status==1) | (work_status==3) | (work_status >=6)").size
    Config.County.rate_engagement[Year] = (We) /float(Config.adult_county_population)  
    
    W1 = Config.TP.getWhereList("(membership==1)").size
    if Year >= Config.burn_in_period -1:  
      Wn1 = Config.TP.getWhereList("((work_status==0) | (work_status==1)) & (membership==1)").size
      self.rate_NIWF[Year] = (Wn1) / float(W1)
      
      self.rate_participation_measured[Year] = W1 / float(Config.adult_county_population) 
      # rate nurture is the fraction of members who are unemployed or NIWF and who receive LEDDA 
      # support
      Ws = Config.TP.getWhereList("((work_status==1) | (work_status==3)) & (membership==1)").size
      Wa = Config.TP.getWhereList("(work_status <=3) & (membership==1)").size
      self.rate_nurture[Year] =  Ws / float(Wa)

      # rate nurture for county
      Ws = Config.TP.getWhereList("((work_status==1) | (work_status==3))").size
      Wa = Config.TP.getWhereList("(work_status <=3)").size
      Config.County.rate_nurture[Year] =  Ws / float(Wa)

    # calculate Ledda-funded new job (LFNJ) income and job saturation, fraction of total jobs/wages
    Work_Status = Config.TP.cols.work_status[:]
    Income_Total = Config.TP.cols.R_total[:]
    W4 = np.where((Work_Status>=4))[0]
    W6 = np.where((Work_Status >=6))[0]
    Ledda_saturation_LFNJ_income = Income_Total[W6].sum() / Income_Total[W4].sum()
    self.saturation_LFNJ_income[Year] = Ledda_saturation_LFNJ_income
    self.saturation_LFNJ_job[Year] = W6.size/float(W4.size)



