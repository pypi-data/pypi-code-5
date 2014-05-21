
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os, shutil, glob, logging
import tables as tb
from scipy import stats, interpolate
from scipy.interpolate import griddata


sys.path.append('./')
import Config, Class_Org, Class_Ledda, Class_Persons, Class_County, Class_Gov, Class_CBFS, MiscFx
import Class_Roc


# ===========================================================================================
# Functions called only once that initialize objects and tables at start of simulation
# ===========================================================================================


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def makeFolders():
  """
  
  Create any folders needed to hold results.  Any existing files in all subfolders of the results folder 
  are deleted each time the simulation is run.  An exception is files in the Option_1 folder, which 
  holds graphs related to Wage Option choices.  These are not deleted with each new simulation.  But 
  examineOption1(), which creates the files, should be re-run if certain parameters in Config change for
  a new simulation.  These parameters include earmarks, TSI_max, and incentive. 
  
  """
  
  PF = os.path.dirname(os.path.realpath(__file__)) # python file folder
  RF = ('./' + Config.results_folder_name).replace(' ', '_')  # results folder
  
  Config.PF = PF
  Config.RF = RF

  if (Config.start_simulation_year>0) and (os.path.exists(RF+'/data')==False):
    print "\nStart simulation at Year 0 if folders do not already exist\n"
    sys.exist()

  if (Config.start_simulation_year>0):
    return
    
  if (os.path.exists(RF+'/data')) and ((Config.create_new_HDF5==True) or 
    (Config.preliminary_graphs_Option_1==True)):
    Answer = raw_input("\n**** Data files in " + RF + \
      " are about to be overwritten.  Do you want to contiune (Y/N)?")
    if Answer != 'Y':
      sys.exit()  

  # create results folder to hold subfolders
  if os.path.exists(RF) == False:
    os.makedirs(RF)

  # Create subfolders for figures if they do not already exist. Delete any existing files.  Folder names 
  # are the same as object.Title names
  for f in [RF+'/figs', RF+'/data', RF+'/figs/CBFS', RF+'/figs/County', RF+'/figs/Gov', RF+'/figs/LEDDA', 
    RF+'/figs/Org', RF+'/figs/Persons', RF+'/figs/ROC', RF+'/figs/County/hist', RF+'/figs/County/plot', 
    RF+'/figs/County/scatter', RF+'/figs/LEDDA/hist', RF+'/figs/LEDDA/scatter', RF+'/figs/LEDDA/plot']:
    if os.path.exists(f) == False:
      os.makedirs(f)
    Ls = glob.glob(f + "/*.*")  
    for k in Ls:
      os.remove(k)

  for f in [RF+'/figs/County/annimations', RF+'/figs/LEDDA/annimations']:
    if os.path.exists(f) == False:  
      os.makedirs(f)  
    Ls = glob.glob(f + "/*.*")  
    for k in Ls:
      os.remove(k)

  if Config.preliminary_graphs_Option_1 == True:
    for f in [RF+'/figs/Option_1']:
      if os.path.exists(f) == False:  
        os.makedirs(f)  
      Ls = glob.glob(f + "/*.*")  
      for k in Ls:
        os.remove(k)



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def initializeObjects():
  """
  
  Initialize objects that hold data and initialize logger.
  
  """
  
  RF = Config.RF


  # make a copy of the Config file for later reference
  #shutil.copy('./Config.py', RF+'/data/Config.py')  
  
  # set up logger for general messages  -------------------------------------
  formatter = logging.Formatter('%(message)s')

  logRoot = logging.getLogger('general_logger')
  logRoot.setLevel(Config.logging_level_file)            
  
  if (Config.start_simulation_year>0):
    hdlr_1 = logging.FileHandler(RF+'/data/general_log.txt', mode='a')
  else:
    hdlr_1 = logging.FileHandler(RF+'/data/general_log.txt', mode='w')
  hdlr_1.setFormatter(formatter)
  logRoot.addHandler(hdlr_1)

  console = logging.StreamHandler()
  console.setLevel(logging.INFO)
  console.setFormatter(formatter)
  logRoot.addHandler(console)
  
  Config.logRoot = logRoot 
  Config.logRoot.info("\n***** \nRunning TES Simulation\nFolder:{0:s}\nDate: {1:s}\n*****\n".format(
    Config.results_folder_name,
    str(time.strftime("%c"))))

  if Config.create_new_HDF5 == True: 
    # set up logger for HDF5 creation messages  -------------------------------------
    logHDF5 = logging.getLogger('HDF5_logger')
    logHDF5.setLevel(Config.logging_level_file)
    
    hdlr_1 = logging.FileHandler(RF+'/HDF5_log.txt', mode='w')
    hdlr_1.setFormatter(formatter)
    logHDF5.addHandler(hdlr_1)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logHDF5.addHandler(console)
    
    Config.logHDF5 = logHDF5 

  if Config.preliminary_graphs_Option_1 == True:   
    # set up logger for examineOption1()  -------------------------------------
    logOpt1 = logging.getLogger('Opt1_logger')
    logOpt1.setLevel(logging.DEBUG)
    
    hdlr_1 = logging.FileHandler(RF+'/Opt1_log.txt', mode='w')
    hdlr_1.setFormatter(formatter)
    logOpt1.addHandler(hdlr_1)

    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    console.setFormatter(formatter)
    logOpt1.addHandler(console)
    
    Config.logOpt1 = logOpt1 
        
  # set up simulation objects  ------------------------------------- 
  
  if (Config.start_simulation_year>0):
    County, Persons, Ledda, Org, Gov, Roc, Cbfs = getOldObjects()
  
  else:
    County = Class_County.COUNTY()
    Ledda = Class_Ledda.LEDDA()
    Org = Class_Org.ORGANIZATIONS()
    Gov = Class_Gov.GOVERNMENT()
    Persons = Class_Persons.PERSONS()
    Cbfs = Class_CBFS.CBFS()
    Roc = Class_Roc.ROC()

  Config.County = County
  Config.Ledda = Ledda
  Config.Org = Org
  Config.Gov = Gov
  Config.Persons = Persons
  Config.Cbfs = Cbfs
  Config.Roc = Roc
  
  # initialize year 0
  if (Config.start_simulation_year==0):
    Config.County.number_employed[0] = int(round(Config.County.population * \
      Config.rate_labor_participation * (1-Config.rate_unempoyment_initial)))
    Config.County.number_unemployed[0] = int(round(Config.County.population * \
      Config.rate_labor_participation * Config.rate_unempoyment_initial))
    Config.County.number_NILF = int(round(Config.County.population * \
      (1-Config.rate_labor_participation)))
    Config.County.rate_unemployment[0] = Config.rate_unempoyment_initial  

    assert np.allclose(Config.adult_county_population, Config.County.number_employed[0] + \
      Config.County.number_unemployed[0] + Config.County.number_NILF)

  # create new pytables table or open old one
  getHDF5()

  # setup initial funds for government and organizations so they can make payments.
  setGovRates()

  # initialize some Ledda and county arrays
  if (Config.start_simulation_year==0):
    incomeP = Config.TP.cols.R_wages_NP_dollars[:] + Config.TP.cols.R_wages_SB_dollars[:] + \
      Config.TP.cols.R_gov_support_dollars[:]
    Config.County.R_dollars[0] = incomeP.sum()
    Config.County.R_total[0] = incomeP.sum()

  # print county information
  if (Config.start_simulation_year==0):
    countyInfo()
    
  # =====================================================================
  # Plot some Config parameters (these graphs are not part of the simulation proper)
  # =====================================================================

  # set 1==2 if these plots of income target etc. are not wanted.
  if 1==2:
    
    Years = range(0, min(Config.growth_period+5, Config.simulation_period))
    
    pylab.plot(Years, Config.income_target_tokens[Years]/1000., '--r',lw=2)
    pylab.plot(Years, Config.income_target_dollars[Years]/1000., '-.g',lw=2)
    pylab.plot(Years, Config.income_target_total[Years]/1000., 'b')
    pylab.plot(Years, Config.income_target_total[Years]/1000. * (1-.56), '-bv')
    pylab.grid(True)
    pylab.title("Income target, per person (wage option 1)")
    pylab.xlabel("Years")
    pylab.ylabel("Income, thousand tokens + dollars")
    pylab.legend(['tokens', 'dollars', 'total', 'approx. post-CBFS, total' ],loc=2)
    pylab.tight_layout() 
    pylab.savefig(RF+"/figs/LEDDA/target_income.png")
    pylab.close()

    pylab.plot(Years, Config.TSI_target[Years], 'b')
    if "share_gain_token" in Config.__dict__.keys():
      pylab.plot(Years, Config.share_gain_token[Years], 'r')
      pylab.legend(['token share of income', 'share_gain_token'],loc=2)
    pylab.grid(True)
    pylab.title("Token share of income (option 1)")
    pylab.xlabel("Years")
    pylab.ylabel("TSI")
    pylab.tight_layout() 
    pylab.savefig(RF+"/figs/LEDDA/target_TSI.png")
    pylab.close()
    
    if "sigmoid" in Config.__dict__.keys():
      pylab.plot(Config.sigmoid)
      pylab.title("Sigmoid function, token share of gain (option 1)")
      pylab.grid(True)
      pylab.tight_layout() 
      pylab.savefig(RF+"/figs/LEDDA/sigmoid.png")
      pylab.close()

  if Config.preliminary_graphs_Option_1 == True:
    examineOption1()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def getOldObjects():
  """
  
  Load old object from pickled files if simulation does not start in Year 0.  Add new elements
  to arrays as needed.
  
  """
  
  RF = Config.RF

  file1 = open(RF+"/data/results_County.pickle", "r") 
  County = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_Persons.pickle", "r") 
  Persons = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_Ledda.pickle", "r") 
  Ledda = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_Org.pickle", "r") 
  Org = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_Gov.pickle", "r") 
  Gov = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_ROC.pickle", "r") 
  Roc = cPickle.load(file1)
  file1.close()

  file1 = open(RF+"/data/results_CBFS.pickle", "r") 
  Cbfs = cPickle.load(file1)
  file1.close()
  
  old_size = Ledda.income_target_total.size
  new_size = Config.simulation_period
  
  for Obj in [County, Persons, Ledda, Org, Gov, Roc, Cbfs]:
    K = Obj.__dict__.keys()
    K.remove("Title")
    K.remove("graphGroup")
    K.sort()
    
    for k in K:
      v = Obj.__dict__[k]
      if v is None:
        continue
      
      if type(v) == type(np.array([1])):
        if v.size > 1:
          # add length to array
          Obj.__dict__[k] = np.hstack((v, [0]*(new_size - old_size)))
          Obj.__dict__[k] = Obj.__dict__[k][0:new_size]
  
  return County, Persons, Ledda, Org, Gov, Roc, Cbfs
  

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def examineOption1():
  """
  
  Plot graphs and print information regarding the percentage of people who will choose wage Option 1
  under different income targets.  These graphs can help the user determine a maximum income target
  that will result in, say, 90 percent of all families choosing Option 1.  If this maximum income target 
  is used in the simulation, and if only those families below the 90th percentile of base income join a 
  LEDDA, then 100 percent of families who join a LEDDA will eventually choose Option 1.  
  
  The code to determine post-CBFS family income is an abbreviated version of the code in 
  Ledda.wageOptions(); it only examines post-CBFS income at the end of the simulation, when, for example,
  the lending target has been reached for all members, and the token share of income is no longer 
  increasing.  
  
  To run this function after a simulation is finished and data saved, rename the existing results folder
  and then set Config.preliminary_graphs_Option_1=True and re-run script.  This way, saved data is not
  deleted. 
  
  """
  
  Config.logOpt1.info("\n*** Creating Option 1 graphs, Config.preliminary_graphs_Option_1==True ***\n")
  
  RF = Config.RF
    
  P0 = range(Config.adult_county_population)
  baseWage_P0 = Config.TP.cols.base_wage[:]
  workStatus_P0 = Config.TP.cols.work_status[:][P0]

  P1 = np.zeros_like(P0)    
  baseWage_P1 = np.zeros_like(baseWage_P0)
  workStatus_P1 = np.zeros_like(baseWage_P0)
  
  # find marriage partners
  for i, idd in enumerate(P0):
    P1[i] = Config.TP.cols.partner[idd]    
    baseWage_P1[i] = Config.TP.cols.base_wage[P1[i]]
    workStatus_P1[i] = Config.TP.cols.work_status[P1[i]] 

  Persons = np.column_stack((P0,P1))
  BaseWage = np.column_stack((baseWage_P0, baseWage_P1))
  WorkStatus = np.column_stack((workStatus_P0, workStatus_P1))
      
  # remove duplicate families
  A = np.sort(Persons,1)
  _, uID = np.unique(A.view([('',A.dtype)]*A.shape[1]), return_index=True)

  Persons = Persons[uID]
  BaseWage = BaseWage[uID]
  WorkStatus = WorkStatus[uID]

  switch = np.random.randint(0,2,Persons.shape[0])  
  S = np.where(switch==1)    
  Persons[S] = Persons[S,::-1].squeeze()
  BaseWage[S] = BaseWage[S,::-1].squeeze()
  WorkStatus[S] = WorkStatus[S,::-1].squeeze()

  # Set lower bound on base wage to mean government assistance level, as is done in the simulation. 
  Wm = np.where(BaseWage < Config.Gov.support_dollars_mean)
  BaseWage[Wm] = Config.Gov.support_dollars_mean  

  EM_all = Config.earmark_subsidy_SB + Config.earmark_subsidy_PB + Config.earmark_nurture + \
    Config.earmark_donation_NP
  
  Config.logOpt1.info("  total earmarks = {0:,.3g}, TSI_max = {1:,.3g}\n".format(EM_all, Config.TSI_max))
  
  Config.logOpt1.info("\n  ...testing sequence of income targets, please wait...\n")
  
  results = []
  for income_target_total in  np.arange(30000., 140000., 5000):
    
    income_target_tokens = income_target_total * Config.TSI_max
    income_target_dollars = income_target_total * (1- Config.TSI_max)

    # ------------------------------------------------------------------------------
    # option 1: base wages on target, both persons choose Option 1
    # ------------------------------------------------------------------------------ 
    
    income_target_tokens_1 = income_target_tokens *  np.ones_like(BaseWage)
    income_target_dollars_1 = income_target_dollars *  np.ones_like(BaseWage)
    income_target_total_1 = income_target_tokens_1 + income_target_dollars_1

    # non-lending earmarks
    EM_Subsidy_SB_1 = Config.earmark_subsidy_SB * income_target_total_1 
    EM_Subsidy_PB_1 = Config.earmark_subsidy_PB * income_target_total_1 
    EM_Nurture_1 = Config.earmark_nurture * income_target_total_1 
    EM_Donation_NP_1 = Config.earmark_donation_NP * income_target_total_1 

    EM_all_1 = EM_Subsidy_SB_1 + EM_Subsidy_PB_1 + EM_Nurture_1 + EM_Donation_NP_1

    # set up arrays to hold token and dollar contributions
    EM_Subsidy_SB_Tokens = np.zeros_like(BaseWage)
    EM_Subsidy_SB_Dollars = np.zeros_like(BaseWage)
    EM_Subsidy_PB_Tokens = np.zeros_like(BaseWage)
    EM_Subsidy_PB_Dollars = np.zeros_like(BaseWage)
    EM_Nurture_Tokens = np.zeros_like(BaseWage)
    EM_Nurture_Dollars = np.zeros_like(BaseWage)
    EM_Donation_NP_Tokens = np.zeros_like(BaseWage)
    EM_Donation_NP_Dollars = np.zeros_like(BaseWage)
    
    TSI = income_target_tokens_1 / income_target_total_1
    TS = TSI.copy()
    DS = 1 - TS  
    
    factor_gov_support = Config.Gov.support_dollars_mean / income_target_dollars
    DS_nurture = DS * (1-factor_gov_support)
    
    EM_Subsidy_SB_Tokens = EM_Subsidy_SB_1 * TS
    EM_Subsidy_SB_Dollars = EM_Subsidy_SB_1 * DS

    EM_Subsidy_PB_Tokens = EM_Subsidy_PB_1 * TS
    EM_Subsidy_PB_Dollars = EM_Subsidy_PB_1 * DS
          
    EM_Donation_NP_Tokens = EM_Donation_NP_1 * TS 
    EM_Donation_NP_Dollars = EM_Donation_NP_1 * DS
    
    EM_Nurture_Tokens = EM_Nurture_1 * TS 
    EM_Nurture_Dollars = EM_Nurture_1 * DS_nurture 
    assert np.all(EM_Nurture_Tokens + EM_Nurture_Dollars <= EM_Nurture_1 + .01)
    
    # checks
    EM_Tokens = EM_Subsidy_SB_Tokens + EM_Subsidy_PB_Tokens + EM_Donation_NP_Tokens + EM_Nurture_Tokens    
    EM_Dollars = EM_Subsidy_SB_Dollars + EM_Subsidy_PB_Dollars + EM_Donation_NP_Dollars + \
      EM_Nurture_Dollars
    
    if np.all(EM_Tokens < income_target_tokens_1) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError     

    if np.all(EM_Dollars < (income_target_total_1 - income_target_tokens_1)) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError    

    assert np.all(EM_Tokens + EM_Dollars <= EM_all_1)
    
    R_postCBFS_1 = income_target_total_1 - EM_Tokens - EM_Dollars      
    assert np.all(R_postCBFS_1 > 0)


    # ------------------------------------------------------------------------------
    # option 2: base wages on incentive (paid 100% in tokens), both persons choose Option 2
    # ------------------------------------------------------------------------------ 

    # check that TSI for individual is less than some maximum. In early years, set the maximum lower
    # than in later years.
    max_fraction = Config.TSI_max
    max_tokens = BaseWage * max_fraction / (1. - max_fraction)
    
    income_target_tokens_2 = np.minimum(max_tokens, Config.incentive[-1]) *  np.ones_like(BaseWage)
    income_target_dollars_2 = BaseWage 
    income_target_total_2 =  income_target_tokens_2 + income_target_dollars_2
    assert np.all(income_target_tokens_2 / income_target_total_2 <= max_fraction + .0001)
    
    # non-lending earmarks
    EM_Subsidy_SB_2 = Config.earmark_subsidy_SB * income_target_tokens_2
    EM_Subsidy_PB_2 = Config.earmark_subsidy_PB * income_target_tokens_2
    EM_Nurture_2 = Config.earmark_nurture * income_target_tokens_2
    EM_Donation_NP_2 = Config.earmark_donation_NP * income_target_tokens_2
    
    EM_all_2 = EM_Subsidy_SB_2 + EM_Subsidy_PB_2 + EM_Nurture_2 + EM_Donation_NP_2
    assert np.all(income_target_total_2 - EM_all_2 > BaseWage)

    # set up arrays to hold token and dollar contributions
    EM_Subsidy_SB_Tokens = np.zeros_like(BaseWage)
    EM_Subsidy_SB_Dollars = np.zeros_like(BaseWage)
    EM_Subsidy_PB_Tokens = np.zeros_like(BaseWage)
    EM_Subsidy_PB_Dollars = np.zeros_like(BaseWage)
    EM_Nurture_Tokens = np.zeros_like(BaseWage)
    EM_Nurture_Dollars = np.zeros_like(BaseWage)
    EM_Donation_NP_Tokens = np.zeros_like(BaseWage)
    EM_Donation_NP_Dollars = np.zeros_like(BaseWage)
    
    TSI = income_target_tokens_2 / income_target_total_2
    TS = TSI.copy()
    DS = 1 - TS  
    
    factor_gov_support = Config.Gov.support_dollars_mean / income_target_dollars
    DS_nurture = DS * (1-factor_gov_support)
    
    EM_Subsidy_SB_Tokens = EM_Subsidy_SB_2 * TS
    EM_Subsidy_SB_Dollars = EM_Subsidy_SB_2 * DS

    EM_Subsidy_PB_Tokens = EM_Subsidy_PB_2 * TS
    EM_Subsidy_PB_Dollars = EM_Subsidy_PB_2 * DS
          
    EM_Donation_NP_Tokens = EM_Donation_NP_2 * TS 
    EM_Donation_NP_Dollars = EM_Donation_NP_2 * DS
    
    EM_Nurture_Tokens = EM_Nurture_2 * TS 
    EM_Nurture_Dollars = EM_Nurture_2 * DS_nurture 
    assert np.all(EM_Nurture_Tokens + EM_Nurture_Dollars <= EM_Nurture_2 + .01)
    
    # checks
    EM_Tokens = EM_Subsidy_SB_Tokens + EM_Subsidy_PB_Tokens + EM_Donation_NP_Tokens + EM_Nurture_Tokens    
    EM_Dollars = EM_Subsidy_SB_Dollars + EM_Subsidy_PB_Dollars + EM_Donation_NP_Dollars + \
      EM_Nurture_Dollars
    
    if np.all(EM_Tokens < income_target_tokens_2) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError     

    if np.all(EM_Dollars < (income_target_total_2 - income_target_tokens_2)) == False:
      MiscFx.errorCode(1010)
      raise MiscFx.ParameterError    

    np.all(EM_Tokens + EM_Dollars <= EM_all_2)  
    
    R_postCBFS_2 = income_target_total_2 - EM_Tokens - EM_Dollars      
    assert np.all(R_postCBFS_2 > 0)

    assert np.all(R_postCBFS_2 > BaseWage)


    # ------------------------------------------------------------------------------
    # choose wage option
    # ------------------------------------------------------------------------------ 

    wage_selector = (R_postCBFS_2.sum(1) > R_postCBFS_1.sum(1))
    wage_selector = wage_selector.astype('i') + 1
    W1 = np.where(wage_selector==1)[0]
    W2 = np.where(wage_selector==2)[0]

    postCBFS_family_income = np.zeros_like(BaseWage)
    postCBFS_family_income[W1] = R_postCBFS_1[W1]
    postCBFS_family_income[W2] = R_postCBFS_2[W2]
    
    postCBFS_family_income = postCBFS_family_income.sum(1)

    
    # ------------------------------------------------------------------------------
    # plots for each income target
    # ------------------------------------------------------------------------------ 
    
    # save data in list
    fract_1 = W1.size / float(wage_selector.size)
    post_CBFS_family_income = np.unique(postCBFS_family_income[W1])[0]

    results.append([income_target_total/1000., postCBFS_family_income.mean()/1000., fract_1, 
      post_CBFS_family_income/1000.])
    
    # option 1
    W1 = np.where((BaseWage[:,0] < 140000) & (BaseWage[:,1] < 140000) & (wage_selector==1))[0]
    W2 = np.where((BaseWage[:,0] < 140000) & (BaseWage[:,1] < 140000) & (wage_selector==2))[0]
    D1 = (BaseWage/1000.)[W1]
    D2 = (BaseWage/1000.)[W2]
    pylab.scatter(D1[:,0], D1[:,1], c='b')
    pylab.scatter(D2[:,0], D2[:,1], c='r')
    pylab.title("Wage Option choices\nIncome target= " + str(int(income_target_total/1000.)) + 
      " thousand T&D")      
    pylab.legend(['Option 1', 'Option 2'])
    pylab.minorticks_on()
    pylab.grid(True, which='both')
    pylab.xlabel('Person 1 base income, thousand dollars')
    pylab.ylabel('Person 2 base income, thousand dollars')
    pylab.xlim([1,140])
    pylab.ylim([1,140])
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/Option_1/options_' + str(int(income_target_total/1000.)).zfill(3) + '.png')
    pylab.close()
 

    # income gain
    W = np.where((BaseWage[:,0] < 100000) & (BaseWage[:,1] < 100000))[0]
    D = np.column_stack((BaseWage/1000., postCBFS_family_income/1000. - BaseWage.sum(1)/1000.))[W]
    xi = np.linspace(0, D[:,0].max(),100)
    yi = np.linspace(0, D[:,1].max(),100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((D[:,0], D[:,1]), D[:,2], (xi, yi), method='cubic')
    
    CS= pylab.contour(xi,yi,zi, 10, linewidths=1, colors='k')
    pylab.contourf(xi,yi,zi, 10, cmap=pylab.cm.jet)
    pylab.clabel(CS, inline=1, fontsize=10, fmt='%3.0f')
    pylab.title("Post-CBFS family income gain, thousand T&D\nIncome target= " + 
      str(int(income_target_total/1000.)) + " thousand T&D")
    pylab.minorticks_on()
    pylab.grid(True, which='both')
    pylab.xlabel('Person 1 base income, thousand dollars')
    pylab.ylabel('Person 2 base income, thousand dollars')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/Option_1/postCBFS_family_income_gain_' + \
      str(income_target_total/1000.).zfill(3) + '.png')
    pylab.close()

    
    # income
    W = np.where((BaseWage[:,0] < 140000) & (BaseWage[:,1] < 140000))[0]
    D = np.column_stack((BaseWage/1000., postCBFS_family_income/1000.))[W]
    xi = np.linspace(0, D[:,0].max(),100)
    yi = np.linspace(0, D[:,1].max(),100)
    xi, yi = np.meshgrid(xi, yi)
    zi = griddata((D[:,0], D[:,1]), D[:,2], (xi, yi), method='cubic')
    
    CS= pylab.contour(xi,yi,zi, 20, linewidths=1, colors='k')
    pylab.contourf(xi,yi,zi, 20, cmap=pylab.cm.jet)
    pylab.clabel(CS, inline=1, fontsize=10, fmt='%3.0f')
    pylab.title("Post-CBFS family income\nIncome target= $" + str(int(income_target_total/1000.)) \
      + " thousand")
    pylab.minorticks_on()
    pylab.grid(True, which='both')
    pylab.xlabel('Person 1 base income, thousand dollars')
    pylab.ylabel('Person 2 base income, thousand dollars')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/Option_1/postCBFS_family_income_' + \
      str(income_target_total/1000.).zfill(3) + '.png')
    pylab.close()
    

  # ------------------------------------------------------------------------------
  # assess all results
  # ------------------------------------------------------------------------------ 
    
  results = np.array(results)  
  Config.logOpt1.info("\n ********************* Results for Examine Option 1 *********************")
  
  f2 = interpolate.interp1d(results[:,2], results[:,0], kind='cubic')
  opt1_90th_pctl_target_income = f2(.9)
  Config.logOpt1.info(
    "income_target_total (target_end) needed for 90% of families to choose Option 1 = {0:,.9g} T&D".format(
    np.round(opt1_90th_pctl_target_income*1000.,0).item()))
  
  score_90 = stats.scoreatpercentile(Config.TF.cols.R_total[:], Config.max_participation_percentile*10)
  Config.logOpt1.info(
  (str(Config.max_participation_percentile*10) + "th percentile base family income = ${0:,.9g}").format(
    np.round(score_90,0).item()))
  
  f2 = interpolate.interp1d(results[:,0], results[:,3], kind='cubic')
  postCBFS_at_target = f2(opt1_90th_pctl_target_income)  
  Config.logOpt1.info("\nresulting post-CBFS family income @ threshold = {0:,.9g} T&D".format(
    np.round(postCBFS_at_target*1000.,0).item()))
    
  f2 = interpolate.interp1d(results[:,0], results[:,1], kind='cubic')
  postCBFS_mean = f2(opt1_90th_pctl_target_income)
  Config.logOpt1.info(
    "post-CBFS mean family income (100% of population) @ income_target_total = {0:,.9g} T&D".format(
      np.round(postCBFS_mean * 1000.,0).item()))

  # plot mean post CBFS income
  ax = pylab.subplot(1,1,1) 
  pylab.plot(results[:,0], results[:,1])
  pylab.xlabel('Pre-CBFS person income, thousand T&D')
  pylab.ylabel("Mean postCBFS family income")
  pylab.title("Mean postCBFS family income (100% participation)")
  pylab.minorticks_on()
  pylab.grid(True, which='both')
  ax.axvline(opt1_90th_pctl_target_income, color='r')
  ax.axhline(postCBFS_mean, color='r')
  c2 = ax.get_title().replace(" ","_")
  pylab.tight_layout() 
  pylab.savefig(RF+'/figs/Option_1/results_' + c2 + '.png')
  pylab.close()

  # plot fraction of families that choose Option 1
  ax = pylab.subplot(1,1,1) 
  pylab.plot(results[:,0], results[:,2])
  pylab.xlabel('Pre-CBFS person income, thousand T&D')
  pylab.ylabel("Fraction of families")
  pylab.title("Fraction of families that choose Option 1")
  pylab.minorticks_on()
  pylab.grid(True, which='both')
  ax.axvline(opt1_90th_pctl_target_income, color='r')
  ax.axhline(.9, color='r')
  c2 = ax.get_title().replace(" ","_")
  pylab.tight_layout() 
  pylab.savefig(RF+'/figs/Option_1/results_' + c2 + '.png')
  pylab.close()

  # plot post-CBFS income 
  ax = pylab.subplot(1,1,1) 
  pylab.plot(results[:,0], results[:,3])
  pylab.xlabel('Pre-CBFS person income, thousand T&D')
  pylab.ylabel("Post-CBFS income")
  pylab.title("Post-CBFS family Option 1 income")
  pylab.minorticks_on()
  pylab.grid(True, which='both')
  ax.axvline(opt1_90th_pctl_target_income, color='r')
  ax.axhline(postCBFS_at_target, color='r')
  c2 = ax.get_title().replace(" ","_")
  pylab.tight_layout() 
  pylab.savefig(RF+'/figs/Option_1/results_' + c2 + '.png')
  pylab.close()

     

  Config.logOpt1.info("""
  
  ********************* 
  Set Config.preliminary_graphs_Option_1=False to run simulation.  
  
  Change Config.target_end to match target_end calculated here (if desired).  
  
  Change Config.threshold_for_membership_family to match 90th percentile base family income (if desired). 
  
  Re-run examineOption1() if earmarks in Config change, or if Config.TSI_max or Config.incentive change.
  Make sure that Config.earmark_nurture is greater than "fraction below family threshold that are NIWF or
  unemployed" calculated in countyInfo(), or else nurture funds will run dry.  
  *********************
  
  """)

  sys.exit()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def countyInfo():
  """
  
  Config.logRoot.info(summaries of initial county income data.
  
  """

  Config.logRoot.info("""
  
  # =====================================================================
  # Config information
  # ===================================================================== 
  
  """)

  Config.logRoot.info("\n{0:>11s} {1:>11s} {2:>11s} {3:>11s} {4:>11s} {5:>11s} {6:>11s}".format(
    "index",
    "simulation",
    "income",
    "incentive",
    "Option 1",
    "TSI",
    "participate"))

  Config.logRoot.info("{0:>11s} {1:>11s} {2:>11s} {3:>11s} {4:>11s} {5:>11s} {6:>11s}".format(
    " ",
    "year",
    "target",
    " ",
    "fraction",
    " ",
    "rate"))
    
  for i in range(Config.income_target_total.size):
    if i in [Config.burn_in_period, Config.burn_in_period + Config.incentive_transition_yrs, 
      Config.burn_in_period + Config.growth_period]:
      Config.logRoot.info("\n")
    
    Config.logRoot.info(("{0:>10}, {1:>10d}, {2:>10.4g}, {3:>10.4g}, {4:>10.4g}, {5:>10.4g}, " + 
      "{6:>10.4g}").format(
      i, i-2, 
      Config.income_target_total[i], 
      Config.incentive[i], 
      Config.option_1_fraction_allowed[i], 
      Config.TSI_target[i], 
      Config.rate_participation[i]))

  Config.logRoot.info("\nearmarks total, without lending = {0:,.4g}".format(
    Config.earmark_nonlending_total))
  
  Config.logRoot.info("\nearmarks total, with lending = {0:,.4g}".format(
    Config.earmark_nonlending_total + \
    Config.earmark_lending_SB + Config.earmark_lending_PB + Config.earmark_lending_NP))

  Config.logRoot.info("adult population = {0:,d}\n".format(Config.TP.cols.R_dollars[:].size))
  
  Config.logRoot.info("""
  
  # =====================================================================
  # Initial County Data
  # ===================================================================== 
  
  """)
  
  incomeP = Config.TP.cols.R_wages_NP_dollars[:] + Config.TP.cols.R_wages_SB_dollars[:] + \
    Config.TP.cols.R_gov_support_dollars[:]
  
  Config.logRoot.info("\nfamily income, median = ${0:,.9g}".format(
    np.round(np.median(Config.TF.cols.R_dollars[:]),0).item()))
  
  Config.logRoot.info("family income, mean = ${0:,.9g}".format(
    np.round(Config.TF.cols.R_dollars[:].mean(),0).item()))
  
  We1 = Config.TP.getWhereList("(work_status >=4)")
  ave_working_income = incomeP[We1].mean()
  
  Config.logRoot.info("\nmean working income = ${0:,.9g}".format(np.round(ave_working_income,0).item()))
  
  ave_income = incomeP.mean()
  
  Config.logRoot.info(("\nmean person income = ${0:,.9g}, percentile of person income at " + 
    "mean = {1:,.9g}").format(
    np.round(ave_income,0).item(), stats.percentileofscore(incomeP, ave_income)))
  
  W0 = np.where(incomeP < ave_income)[0]
  W1 = np.where(incomeP >= ave_income)[0]
  
  Config.logRoot.info("total person income <  mean person income: ${0:,.9g}, size= {1:,d}".format(
    np.round(incomeP[W0].sum(),0).item(),  W0.size))
  
  Config.logRoot.info("total person income >= mean person income: ${0:,.9g}, size= {1:,d}".format(
    np.round(incomeP[W1].sum(),0).item(), W1.size))
  
  Config.logRoot.info("total county income = ${0:,.9g}\n".format(np.round(incomeP.sum(),0).item()))
  
  for i in np.linspace(0,100,21):
    Config.logRoot.info("  percentile = {0:>5.4g}, person income = ${1:>12,.9g}".format(
      i, np.round(stats.scoreatpercentile(incomeP, i),0).item()))
  Config.logRoot.info("\n")
  
  for i in np.linspace(0,100,21):
    Config.logRoot.info("  percentile = {0:>5.4g}, family income = ${1:>12,.9g}".format(
      i, np.round(stats.scoreatpercentile(Config.TF.cols.R_total[:], i),0).item()))
  Config.logRoot.info("\n")

  # calculate thresholds for ~ 90th percentile of family imcome
  threshold_family = float(Config.threshold_for_membership_family)
  threshold_person = threshold_family/2.
  
  
  # Set the maximum participation rate, and linear growth.  Here the maximum is set to about 90%, with 
  # the assumption that only individuals below about the 90th percentile of family income will join a 
  # LEDDA.
  persons_below_threshold = Config.Persons.checkFamilyIncome(0, threshold_family, Membership=0)
  
  percentile_threshold_person = stats.percentileofscore(Config.TP.cols.R_total[:], threshold_person)
  
  Config.logRoot.info(("\nthreshold for membership, person = ${0:,.9g}, percentile of county "  + 
    "person income = {1:,.4g}").format(
    np.round(threshold_person, 0).item(), percentile_threshold_person))
  
  percentile_threshold_family = stats.percentileofscore(Config.TF.cols.R_total[:], threshold_family)
  
  Config.logRoot.info(("threshold for membership, family = ${0:,.9g}, percentile of county " +
    "family income= {1:,.4g}").format(np.round(threshold_family, 0).item(), percentile_threshold_family))
  
  Config.Ledda.percentile_threshold_family = percentile_threshold_family
  
  ws0 = Config.TP.getWhereList("work_status==0")
  NIWF_below = np.intersect1d(persons_below_threshold, ws0, assume_unique=True)
  
  Config.logRoot.info("\nfraction of total NIWF below family threshold = {0:,.4g}".format(
    NIWF_below.size / float(ws0.size)))
  
  Config.logRoot.info("fraction below family threshold that are NIWF = {0:,.4g}".format(
    NIWF_below.size / float(persons_below_threshold.size)))
  
  Config.logRoot.info(("fraction below family threshold that are NIWF or unemployed (1% member " + 
    "unemployment) = {0:,.4g}").format((NIWF_below.size / float(persons_below_threshold.size)) + \
    (Config.adult_county_population * Config.rate_labor_participation * .01) / \
    float(persons_below_threshold.size)))

  ave_income_threshold = Config.TP.cols.R_total[:][persons_below_threshold].mean()
  
  Config.logRoot.info("\ntotal family income <= threshold_family = ${0:,.9g}".format(
    np.round(Config.TP.cols.R_total[:][persons_below_threshold].sum(),0).item()))
  
  Config.logRoot.info("mean of total family income <= threshold_family = ${0:,.9g}".format(
    np.round(ave_income_threshold,0).item()))
  
  Config.Ledda.income_below_threshold = Config.TP.cols.R_total[:][persons_below_threshold].sum()
  
  W4 = Config.TP.getWhereList("(work_status >=4)")
  persons_below_threshold_working = np.intersect1d(W4,persons_below_threshold)
  ave_income_working_county_threshold = Config.TP.cols.R_total[:][persons_below_threshold_working].mean()
  
  Config.logRoot.info("\naverage income, working, county, below threshold = ${0:,.9g}".format(
    np.round(ave_income_working_county_threshold,0).item()))
    
  Wnp = Config.TP.getWhereList("(work_status ==4) | (work_status ==6)")  
  
  Config.logRoot.info(("average income nonprofit = ${0:,.9g}, fraction of county income = " + 
    "{1:,.4g}").format(
    np.round(Config.TP.cols.R_total[:][Wnp].mean(), 0).item(), 
    Config.TP.cols.R_total[:][Wnp].sum() / Config.TP.cols.R_total[:].sum()))

  W3 = Config.TP.getWhereList("(work_status <=3)")  
  
  Config.logRoot.info(("average income NIWF and unemployed = ${0:,.9g}, fraction of county " + 
    "income = {1:,.4g}\n").format(
    np.round(Config.TP.cols.R_total[:][W3].mean(), 0).item(), 
    Config.TP.cols.R_total[:][W3].sum() / Config.TP.cols.R_total[:].sum()))       


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def setGovRates():
  """
  
  Initialize government spending amounts and the tax rate. Taxes are based on adjusted gross income 
  (AGI).  Every person donates dollars to NP at a fixed rate, and AGI equals total income - max(standard 
  deduction, amount donated to nonprofits).  Any AGI < 0 is set to 0.
  
  Every year, forprofits and nonprofits receive the same level of government spending due to grants, 
  contracts, and subsidies.  Spending on support for NIWF and unemployed individuals remains constant, 
  unless an unemployed person receives a job.  After that, government support after any job loss is 
  given at the mean value of initial per capita support.  

  """

  Config.logRoot.info("""

  # =====================================================================
  # Initialize government spending amounts and tax rate
  # ===================================================================== 

  """)
  
  # grants to nonprofits
  W = Config.TP0.getWhereList("(work_status==4)")
  P_grant_NP_dollars = Config.TP0.cols.R_dollars[:].sum() * Config.gov_grant_NP_fraction_total_income
  fraction = P_grant_NP_dollars / Config.TP0.cols.R_wages_NP_dollars[:].sum()
  
  Config.logRoot.info("\nGov spending, NP grants, fraction NP wages = {0:,.4g}".format(fraction))
  
  Config.logRoot.info("Gov spending, NP grants = ${0:,.9g}".format(
    np.round(P_grant_NP_dollars, 0).item()))
  
  Config.Gov.P_grant_NP_dollars_annual = P_grant_NP_dollars

  # contracts with NP
  W = Config.TP0.getWhereList("(work_status==4)")
  P_contract_NP_dollars = Config.TP0.cols.R_dollars[:].sum() * \
    Config.gov_contract_NP_fraction_total_income
  fraction = P_contract_NP_dollars / Config.TP0.cols.R_wages_NP_dollars[:].sum()
  
  Config.logRoot.info("\nGov spending, NP contracts, fraction NP wages = {0:,.4g}".format(fraction))
  
  Config.logRoot.info("Gov spending, NP contracts = ${0:,.9g}".format(
    np.round(P_contract_NP_dollars,0).item()))
  
  Config.Gov.P_contract_NP_dollars_annual = P_contract_NP_dollars

  # contracts with forprofits
  W = Config.TP0.getWhereList("(work_status==5)")
  P_contract_forprofit_dollars = Config.TP0.cols.R_dollars[:].sum() * \
    Config.gov_contract_forprofit_fraction_total_income
  fraction = P_contract_forprofit_dollars / Config.TP0.cols.R_wages_SB_dollars[:].sum()
  
  Config.logRoot.info(
    "\nGov spending, forprofit contracts, fraction forprofit wages = {0:,.4g}".format(fraction))
  
  Config.logRoot.info(
    "Gov spending, forprofit contracts = ${0:,.9g}".format(
      np.round(P_contract_forprofit_dollars,0).item()))
  
  Config.Gov.P_contract_forprofit_dollars_annual = P_contract_forprofit_dollars

  # subsidies to forprofits
  W = Config.TP0.getWhereList("(work_status==5)")
  P_subsidy_forprofit_dollars = Config.TP0.cols.R_dollars[:].sum() * \
    Config.gov_subsidy_forprofit_fraction_total_income
  fraction = P_subsidy_forprofit_dollars / Config.TP0.cols.R_wages_SB_dollars[:].sum()
  
  Config.logRoot.info(
    "\nGov spending, forprofit subsidy, fraction forprofit wages = {0:,.4g}".format(fraction))
  
  Config.logRoot.info(
    "Gov spending, forprofit subsidy = ${0:,.9g}".format(np.round(P_subsidy_forprofit_dollars,0).item()))
  
  Config.Gov.P_subsidy_forprofit_dollars_annual = P_subsidy_forprofit_dollars   
    
  # NIWF & unemployed
  W = Config.TP0.getWhereList("(work_status==0)|(work_status==2)")
  P_support_dollars = Config.TP0.cols.R_dollars[:][W].sum() 
  fraction = P_support_dollars / Config.TP0.cols.R_dollars[:].sum()
  
  Config.logRoot.info(
    "\nGov spending, NIWF & unemployed support, fraction total income = {0:,.4g}".format(fraction))
  
  Config.logRoot.info(
    "Gov spending, NIWF & unemployed support = ${0:,.9g}".format(np.round(P_support_dollars,0).item()))
    
  # mean support for NIWF & unemployed
  Config.Gov.support_dollars_mean = P_support_dollars / float(W.size)
  
  # assumes every person donates to NPs at fixed rate
  donation_dollars = Config.TP0.cols.R_dollars[:] * Config.rate_dollar_donation
  AGI = np.maximum(0, Config.TP0.cols.R_dollars[:] - np.maximum(
    donation_dollars, Config.gov_standard_deduction))
    
  spending_total = P_grant_NP_dollars + P_contract_NP_dollars + P_contract_forprofit_dollars + \
    P_subsidy_forprofit_dollars + P_support_dollars  
  
  Config.Gov.tax_rate = spending_total / AGI.sum()
  
  Config.logRoot.info("\nGovernment tax rate = {0:,.4g}\n".format(Config.Gov.tax_rate))


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def getHDF5():
  """
  
  Open existing HDF5 file or create new one.  The HDF5 contains the person table (TP) and family 
  table (TF), one each for every year.  TP and TF store data for individual persons and families, 
  whereas the Persons object (from class PERSONS), as well as objects from other novel classes, use 
  arrays to store summary, aggregate data for each year.
  
  Column names are mostly self-explanatory.  See abbreviations list in Config.py for assistance.  A few 
  column names are listed below:

    pid or fid            = person or family unique ID number
    incentive             = indicator of wage option choice:
                              0 = no option chosen
                              1 = Option 1
                              2 = option 2
    membership            = indicator for LEDDA membership:
                              0 = not member
                              1 = member
    job_loss              = indicator for loss of LFNJ in current year:
                              0 = no job loss
                              1 = job loss
    job_gain              = indicator for gain of any job in current year
                              0 = no job gain
                              1 = job gain                                
    R_*                   = prefix for received
    P_*                   = prefix for paid                    
    base_wage             = base wage used to calculate CBFS contributions
    P_donation_NP_dollars = dollar donations paid to nonprofits apart from CBFS contributions
    work_status           = indicator of type of job/support:
                              NIWF-not-Ledda-supported          = 0
                              NIWF-Ledda-supported              = 1
                              WF-unemployed-not-Ledda-supported = 2
                              WF-unemployed-Ledda-supported     = 3  
                              WF-employed-not-LFNJ, nonprofit   = 4
                              WF-employed-not-LFNJ, forprofit   = 5
                              WF-employed-LFNJ, NP              = 6
                              WF-employed-LFNJ, SB              = 7
                              WF-employed-LFNJ, PB              = 8 

  
  """
  
  RF = Config.RF
  PF = Config.PF
  
  if Config.create_new_HDF5 == True:  
    # ---------------------- create new HDF5 file containing Persons/Families tables ------------
    
    Config.logHDF5.info("""
    
    # =====================================================================
    # Create new HDF5 file
    # ===================================================================== 
    
    """)
        
    # open income files obtained from Census microdata for Lane County, OR 
    file1 = open(PF + "/data/INCTOT_2011_1yr.pickle", "r")  
    INCTOT = cPickle.load(file1)
    file1.close()  

    # use only positive incomes 
    INCTOT = INCTOT[INCTOT>0]
    
    HDF5 = tb.openFile(RF+'/LEDDA_simulation_master.hdf5', mode='w')
    
    # =====================================================================
    # Persons Table
    # =====================================================================
    
    Description = {}
    for ivar, Var in enumerate([
      'pid', 'fid', 'work_status', 'membership', 'partner',
      'number_job_gains', 'number_job_losses', "job_loss", "job_gain", 'wage_option',
      
      'R_wages_SB_tokens', 'R_wages_PB_tokens', 'R_wages_NP_tokens', 
      'R_CBFS_nurture_tokens',

      'R_wages_SB_dollars', 'R_wages_PB_dollars', 'R_wages_NP_dollars',
      'R_CBFS_nurture_dollars',
      'R_gov_support_dollars',

      'P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 'P_CBFS_loan_NP_tokens', 
      'P_CBFS_subsidy_SB_tokens', 'P_CBFS_subsidy_PB_tokens', 
      'P_CBFS_donation_NP_tokens', 'P_CBFS_nurture_tokens',
      'P_CBFS_tokens',
      
      'P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 'P_CBFS_loan_NP_dollars', 
      'P_CBFS_subsidy_SB_dollars', 'P_CBFS_subsidy_PB_dollars',
      'P_CBFS_donation_NP_dollars', 'P_CBFS_nurture_dollars',
      'P_CBFS_dollars',
      
      'P_CBFS_total', 'P_CBFS_loan',
       
      'P_spending_tokens','P_spending_dollars', 
      
      'P_gov_tax_dollars', 
      'P_donation_NP_dollars',
      
      'R_tokens', 'R_dollars', 'R_total', 
      'R_postCBFS_tokens', 'R_postCBFS_dollars', 'R_postCBFS_total', 'R_postCBFS_total_prelim',
      'P_tokens', 'P_dollars', 'P_total',
      'base_wage',
      
      'save_dollars', 'save_tokens', 'save_total']):      
      
      if Var in ['membership', 'pid', 'number_job_gains', 'number_job_losses', 'job_gain', 'job_loss',
        'work_status', 'wage_option', 'partner', 'fid']:
        Description[Var] = tb.Int64Col(dflt=0,pos=ivar)       
      else:
        Description[Var] = tb.Float64Col(dflt=0,pos=ivar)   
    
    TP = HDF5.createTable('/','Persons_00',description=Description, title='Table of individuals', \
      expectedrows= Config.adult_county_population)
    
    # choose hi/low ranges for selecting incomes for employed vs unemployed & NIWF persons. Break is 
    # chosen so that the mean and median are roughly equal to those published for Lane County, OR
    Cut = Config.census_employee_income_threshold
    INC_W0 = np.where(INCTOT < Cut)[0]
    INC_W1 = np.where(INCTOT >= Cut)[0]
    
    # -----------------------------------------------------------------------------------------
    # enter base info for Persons table -------------------------------------------
    row = TP.row
    
    # fill table for employed persons (SB and NP)
    for i in range(0, Config.County.number_employed[0]):
      row['pid'] = i
      row['number_job_gains'] = 0 
      row['work_status'] = np.random.choice([4,5], 1, \
        p=[Config.fraction_nonprofits, 1-Config.fraction_nonprofits])
      income = np.random.choice(INCTOT[INC_W1], size=1, replace=True)  
      if row['work_status'] == 4:
        # nonprofits
        row['R_wages_NP_dollars'] = income  
      else:
        # forprofits
        row['R_wages_SB_dollars'] = income     
      row['R_dollars'] = income
      row['R_total'] = income
      row['base_wage'] = income
      row.append()
    TP.flush()

    # fill table for unemployed persons
    for j in range(i+1, i+1+Config.County.number_unemployed[0]):
      row['pid'] = j
      row['work_status'] = 2
      row['R_gov_support_dollars'] = np.random.choice(INCTOT[INC_W0], size=1, replace=True)                 
      row['R_dollars'] = row['R_gov_support_dollars']
      row['R_total'] = row['R_gov_support_dollars']
      row['base_wage'] = row['R_gov_support_dollars']
      row.append()
    TP.flush()

    # fill table for not in work force (NIWF) persons
    for k in range(j+1, j+1+Config.County.number_NILF):
      row['pid'] = k
      row['work_status'] = 0
      row['R_gov_support_dollars'] = np.random.choice(INCTOT[INC_W0], size=1, replace=True)                 
      row['R_dollars'] = row['R_gov_support_dollars']
      row['R_total'] = row['R_gov_support_dollars']
      row['base_wage'] = row['R_gov_support_dollars']
      row.append()
    TP.flush()
    
    incomeP = TP.cols.R_wages_NP_dollars[:] + TP.cols.R_wages_SB_dollars[:] + \
      TP.cols.R_gov_support_dollars[:]
    
    assert np.allclose(incomeP, TP.cols.R_total[:])
    assert np.allclose(incomeP, TP.cols.R_dollars[:])
    assert np.all(incomeP > 0)
    
    Config.logHDF5.info("\ncounty income, mean = ${0:,.9g}".format(np.round(incomeP.mean(),0).item()))
    Config.logHDF5.info("county income, median = ${0:,.9g}\n".format(np.round(np.median(incomeP),0).item()))


    # =====================================================================
    # Families Table
    # =====================================================================
    
    Description = {}
    for ivar, Var in enumerate(['fid', 'person1', 'person2', 'membership',
      'job_gain', 'job_loss', 'wage_option',
      'R_total', 'R_dollars', 'R_tokens',
      'save_dollars', 'save_tokens', 'save_total',
      'P_CBFS_tokens', 'P_CBFS_dollars', 'P_CBFS_total',
      'R_postCBFS_total']):
                 
      if Var in ['fid', 'person1', 'person2', 'membership','job_gain', 'job_loss', 'wage_option']:
        Description[Var] = tb.Int64Col(dflt=0,pos=ivar)       
      else:
        Description[Var] = tb.Float64Col(dflt=0,pos=ivar)   
    
    TF = HDF5.createTable('/','Families_00',description=Description, title='Table of families', \
      expectedrows= Config.adult_county_population/2)

    # enter base info for Families table ------------------------------------------
    row = TF.row
    ran0 = np.random.permutation(Config.adult_county_population)
    ran1 = ran0[0:ran0.size/2]
    ran2 = ran0[ran0.size/2:]

    t0 = time.time()      
    for i in range(0, Config.adult_county_population/2): 
      row['fid'] = i
      row['person1'] = ran1[i]
      row['person2'] = ran2[i]
      
      income1 = TP[ran1[i]]['R_dollars'] 
      income2 = TP[ran2[i]]['R_dollars']         

      row['R_dollars'] = income1 + income2      
      row['R_total'] = income1 + income2   
      
      row.append()      
      
      # set fid and partners in Table Persons
      TP.cols.fid[ran1[i]] = i
      TP.cols.fid[ran2[i]] = i
      TP.cols.partner[ran1[i]] = ran2[i]
      TP.cols.partner[ran2[i]] = ran1[i]

    TF.flush()
    
    assert np.allclose(incomeP.sum(), TF.cols.R_dollars[:].sum())

    # create indexes for faster searching
    TP.cols.pid.create_index()
    TP.cols.fid.create_index()
    TP.cols.work_status.create_index()
    TP.cols.membership.create_index()
    TP.cols.partner.create_index()
    TP.cols.wage_option.create_index()
    TF.cols.fid.create_index()
    
    TP.filters.complevel = 5
    TF.filters.complevel = 5 
    
    # print results -------------------------------------------------------------------
    Config.logHDF5.info("\nfamily income, mean = ${0:,.9g}".format(np.round(TF.cols.R_dollars[:].mean(),0).item()))
    Config.logHDF5.info("family income, median = ${0:,.9g}\n".format(np.round(np.median(TF.cols.R_dollars[:]),0).item()))
    
    for i in np.linspace(0,100,21):
      Config.logHDF5.info("  percentile = {0:>3.0f},  person income = ${1:>12,.9g}".format(i, np.round(stats.scoreatpercentile(incomeP, i),0).item()))
    Config.logHDF5.info("\n")
    
    for i in np.linspace(0,100,21):
      Config.logHDF5.info("  percentile = {0:>3.0f},  family income = ${1:>12,.9g}".format(i, np.round(stats.scoreatpercentile(TF.cols.R_total[:], i),0).item()))
    Config.logHDF5.info("\n")

    Config.logHDF5.info("\nTable Persons compression = {0:d}".format(TP.filters.complevel))
    Config.logHDF5.info("Table Families compression = {0:d}\n".format(TF.filters.complevel))
    
    HDF5.close() 
    
    Config.logHDF5.info("""
    
    ********************* 
    New pytable has been created. Now set Config.create_new_HDF5=False and run script again for simulation.
    *********************
    
    """)
    sys.exit()
  
  else:
    # check that the HDF5 pytables file exists
    if os.path.exists(RF+'/LEDDA_simulation_master.hdf5') == False:
      Config.logRoot.info("\n *** set Config.create_new_HDF5=True to create new HDF5 file ***\n")
      sys.exit()
    
    if (Config.start_simulation_year==0):
      # ---------------------- open new copy of master HDF5 file ------------
      HDF5_orig = tb.openFile(RF+'/LEDDA_simulation_master.hdf5', mode='r')
      HDF5_orig.copy_file(RF+'/data/LEDDA_simulation_current.hdf5', overwrite=True)
      HDF5_orig.close()
      
      HDF5 = tb.openFile(RF+'/data/LEDDA_simulation_current.hdf5', mode='a')
      HDF5.root.Families_00.cols.fid.create_index()
      HDF5.root.Families_00.cols.person1.create_index()
      HDF5.root.Families_00.cols.person2.create_index()
      
      Config.HDF5 = HDF5
      Config.TP = HDF5.root.Persons_00
      Config.TF = HDF5.root.Families_00
      Config.TP0 = HDF5.root.Persons_00  # keep a copy of year-zero TP to obtain base wages, etc.
    
    else:
      # ---------------------- open old copy of master HDF5 file ------------
      HDF5 = tb.openFile(RF+'/data/LEDDA_simulation_current.hdf5', mode='a')
      
      Config.HDF5 = HDF5
      
      childs = Config.HDF5.root._v_children.keys()
      childs = [name for name in childs if 'Person' in name]
      childs.sort()
      Year = [int(name[-2:]) for name in childs] 
      
      Config.TP = HDF5.root._f_getChild("Persons_"+str(Year[-1]))
      Config.TF = HDF5.root._f_getChild("Families_"+str(Year[-1]))
      Config.TP0 = HDF5.root.Persons_00  # keep a copy of year-zero TP to obtain base wages, etc.      
 
      Config.last_year_old_simulation = Year[-1] 
 




