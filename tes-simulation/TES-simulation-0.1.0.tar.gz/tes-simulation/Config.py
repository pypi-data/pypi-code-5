
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os, logging

#sys.path.append('./')
#import Debug


params = {'text.fontsize': 12, 'legend.fontsize': 10, 'axes.labelsize':'medium'}
pylab.rcParams.update(params)

np.seterr(all='raise', divide='raise', over='raise', under='raise', invalid='raise')


# =====================================================================
# Abbreviations
# =====================================================================

"""

NIWF      = not in work force
WF        = work force
LFNJ      = LEDDA-funded new job
SB        = standard business
PB        = Principled Business
NP        = nonprofit
CBFS      = Crowd-Based Financial System
TP        = person's table (HDF5 data file)
TF        = family's table (HDF5 data file)
TSI       = token share of income
TS        = token share (of something)
DS        = dollar share (of something)
ROC       = rest of counties (i.e., all counties except the LEDDA county)
P_*       = paid
R_*       = received

"""


# =====================================================================
# Meta parameters
# =====================================================================

results_folder_name = "results_pop_10k"   # name for results folder
create_new_HDF5 = False                   # True to create new base HDF5 table, False to run simulation
make_annimations = True                   # make animations for some graphs?
preliminary_graphs_Option_1 = False       # make graphs of fraction Option 1 at start of simulation
make_graphs = True                        # make graphs each year
start_simulation_year = 0                 # can be used to extend a simulation that is already finished.


# Level of detail for the saved log file. Set to logging.INFO to reduce the size and speed execution,
# or logging.DEBUG for more detail.
logging_level_file = logging.DEBUG        
                                            
simulation_period = 32    # time period (years) for simulation
growth_period = 15        # years to achieve maximum TSI and maximum participation
burn_in_period = 3        # initial years to test steady state economy

if growth_period >= simulation_period:
  Config.logRoot.info("\n *** growth_period must be equal to or shorter than simulation_period ***\n")
  sys.exit()
  
if (make_graphs==False) and (make_annimations==True):
  Config.logRoot.info("\n *** make_animations must be False if make_graphs is false ***\n")
  sys.exit()

RF = None  # placeholder for results folder
PF = None  # placeholder for python file folder, where python modules are located


# =====================================================================
# County parameters
# =====================================================================

adult_county_population = int(1e4)  # adult population is about 0.77 * total county population
rate_labor_participation = .65      # county-wide labor participation rate
rate_unempoyment_initial = .07      # county-wide unemployment rate

# Income threshold used to sample (employed) vs (NIWF or unemployed) incomes from census data.  Set so
# that mean and median county incomes reflect values published by census.
census_employee_income_threshold = 10050

# inflation rate is used only to discount CBFS savings pool of dollars held by members
rate_inflation_dollar = .00           

# donation rate of dollar income post-CBFS to nonprofits, apart from CBFS
rate_dollar_donation = .02   

# the initial fraction of employed persons who work at nonprofits
fraction_nonprofits = .07    


# =====================================================================
# LEDDA non-income parameters
# =====================================================================

# LEDDA participation rate in years (burn_in_period - 2) and (burn_in_period - 1). 
rate_participation_initial = .05    

# the maximum percentile family income included in the target population
max_participation_percentile = .90

# linear growth of the LEDDA participation rate  
rate_participation = np.hstack(([0.]*(burn_in_period -1), 
  [rate_participation_initial], 
  np.linspace(rate_participation_initial, max_participation_percentile, growth_period), 
  [max_participation_percentile]*(simulation_period - growth_period - burn_in_period)))

# Fraction of CBFS funding (loans, etc.) that goes toward job creation.  The remainder goes toward
# operational costs.
fraction_funding_job_creation = .6

# Cost multiplier of target income to create one ~5-year job.  
# 1/fraction_funding_job_creation * job_cost_multiplier should equal about 3, which is about the national
# year-to-year change in business lending / change in labor force, accounting for inflation.
job_cost_multiplier = 2.    

# Structural unemployment level for LEDDA members.  It is assumed that zero unemployment cannot be
# achieved due to changes in technology, etc.
LEDDA_structural_unemployment = .01

# Risk of job loss in each year for LFNJs.  Loss of other jobs is implicit and not modeled.  The job
# loss risk should be set such that a member who has a LFNJ experiences a job loss about once every five
# years (typical within the national economy).
risk_job_loss = .05  


# =====================================================================
# LEDDA income parameters
# =====================================================================

# Family income threshold, used to limit membership.  Use info from Initialize.examineOption1().  This 
# might be based on the 90th percentile of family income.
threshold_for_membership_family = 101182.

# maximum token share of income at end of growth period
TSI_max = .35  

# Linear growth of the token share of income 
TSI_target = np.hstack(([0.] * (burn_in_period -1), \
  np.linspace(.0, TSI_max, growth_period+1), \
  [TSI_max]*(simulation_period - growth_period - burn_in_period)))         

# Incentive bonus for Wage Option 2
incentive_max = 3000.

# Number of year to transition to full incentive. The longer this period, the slower the growth and the 
# lower the (pre-trade-adjustment) dollar deficit seen by organizations in early years.
incentive_transition_yrs = 3 

# linear growth of the incentive for Wage Option 2
incentive = np.hstack(([0.] * (burn_in_period -1), 
  np.linspace(0, incentive_max, incentive_transition_yrs+1), 
  [incentive_max]*(simulation_period - incentive_transition_yrs - burn_in_period)))

# Flag for wage option choices: ==0 (individuals decide option), ==2 (all individuals choose option 2).
# Note that if flag is set to 2, and if the nurture (and possibly donation) earmarks are not zero, then
# at some point in time the nurture and donation funds are likely to be insufficient to provide for
# members who receive support (or work at LFNJ nonprofit positions).
wageSelectorFlag = 0


# Number of year to transition to full Option 1 choice (no forcing of Option 2). The longer this period, 
# the slower the growth and the lower the (pre-trade-adjustment) dollar deficit seen by organizations in 
# early years.
option1_transition_yrs = 5 

# Fraction of granted Option 1 wage selections in early years.  In general, it is best to slowly add 
# option 1 choices in the early years when the TSI is low.  Limiting Option 1 choices reduces the need 
# for dollars from outside counties, especially in the early years when the TSI is low.  
# Make sure wageSelectorFlag = 0 if this parameter is to have an affect.
option_1_fraction_allowed = np.hstack(([0.] * (burn_in_period), \
  np.linspace(0, 1, option1_transition_yrs), \
  [1.]*(simulation_period - option1_transition_yrs - burn_in_period)))

# Placeholders for set of familes who have their selection of Option 2 forced and who have chosen 
# Option 1 at least once.
#forced_option_2_families = None  
families_protected_from_Option2_force = None

# Income targets for Wage Option 1. Use info from  Initialize.examineOption1() to set income_target_end.
income_target_start = 25000.
income_target_end = 107239.

# linear growth of the income target
income_target_total = np.hstack(([income_target_start] * (burn_in_period -1),
  [income_target_start],
  np.linspace(income_target_start, income_target_end, growth_period),
  [income_target_end]*(simulation_period - growth_period - burn_in_period)))

income_target_tokens = income_target_total * TSI_target
income_target_dollars = income_target_total * (1-TSI_target)

assert income_target_total.size ==  simulation_period
assert incentive.size ==  simulation_period
assert option_1_fraction_allowed.size ==  simulation_period
assert TSI_target.size ==  simulation_period
assert rate_participation.size ==  simulation_period

  
# =====================================================================
# CBFS parameters
# =====================================================================

# Earmarks are in fraction of total income for Option 1, and fraction of token bonus for Option 2. After 
# earmark_lending_total is reached, in sum over time, a person makes no more contributions to the loan
# arm of the CBFS.  The exception is if a lending pool loss due to dollar inflation is accounted for. 
# Any earmark (or all) can be set to zero to examine different scenarios.  However, if jobs are created, 
# nurture earmarks must be adequate to cover support for LFNJ employees who loose jobs, and adequate to 
# cover any NIWF members who are given nurture support.  Also, if NP jobs are created, the donation_NP 
# earmark must be adequate to cover wages for LFNJ nonprofit employees.  The nurture earmark must be 
# roughly equal to the percent of NIWF and unemployed persons in the target population (families below 
# the 90th percentile of income).  This is about 40% NIWF and about 1% of WF unemployed, at end of the 
# simulation. Also, one would want all job-creating earmarks to be high enough so that after some 
# reasonable amount of time, a high percentage of jobs in the county are LFNJ.  Values commented out are 
# reasonable default values.

earmark_lending_SB = .01 #.01      
earmark_lending_PB = .02 #.02  
earmark_lending_NP = .01 #.01              
earmark_lending_target = 30000.  

earmark_subsidy_SB = .01 #.01
earmark_subsidy_PB = .02 #.02 
earmark_nurture = .39 #.39
earmark_donation_NP = .11 #.11 

earmark_nonlending_total = earmark_subsidy_SB + earmark_subsidy_PB + earmark_nurture + \
  earmark_donation_NP

# limit on multiplier for token share of CBFS contributions
limit_TS_contrib = 1.4 


# =====================================================================
# Federal government parameters
# =====================================================================

# Fractions of total income to set up initial tax parameters and funding levels.  These are set so that 
# government spending for NP and for-profits is roughly equal to actual government spending.
gov_subsidy_forprofit_fraction_total_income = .06
gov_grant_NP_fraction_total_income = .013
gov_contract_NP_fraction_total_income = .017
gov_contract_forprofit_fraction_total_income = .016
gov_standard_deduction = 2500


# =====================================================================
# Rest of counties parameters
# =====================================================================

# Fraction of organization revenues steming from sales to other counties.  This value remains fixed 
# and initially imports and exports are in balance.  Over time, organizations reduce the fraction of 
# revenue spent in other counties, and thereby keep more dollars in the local economy.  
fraction_Org_import_revenue = .7


# =====================================================================
# checks
# =====================================================================

if ((earmark_lending_SB > 0) or (earmark_lending_PB > 0) or (earmark_lending_NP > 0) or \
  (earmark_subsidy_SB > 0) or (earmark_subsidy_PB > 0) or (earmark_donation_NP > 0)) and \
  (earmark_nurture == 0):
  Config.logRoot.info("\n *** if any non-nurture earmarks are > 0, earmark_nurture must be > 0  to" + \
  " cover support for LFNJ unemployed. ***\n")
  sys.exit()  
  
  

