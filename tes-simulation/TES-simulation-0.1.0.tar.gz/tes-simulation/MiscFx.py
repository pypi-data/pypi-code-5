
import numpy as np
import cPickle, os, pylab, pdb, time, sys, os, glob
import tables as tb
from scipy import stats
from wand.image import Image


sys.path.append('./')
import Config

params = {'text.fontsize': 12, 'legend.fontsize': 9, 'axes.labelsize':'medium'}
pylab.rcParams.update(params)


# ===========================================================================================
# Miscellaneous functions
# ===========================================================================================

"""

This module holds miscellaneous functions related to graphing, saving objects, printing objects, etc. 

"""
   

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def copyTables(Year):
  
  # save copy of old tables
  Config.TP_old = Config.TP
  Config.TF_old = Config.TF
  
  sYear = str(Year).zfill(2)

  # make new Persons table and save object in Config
  Config.TP.copy(newparent='/', newname="Persons_" + sYear, overwrite=False, \
    createparents=False, propindexes=True)
  Config.TP = Config.HDF5.root._f_getChild('Persons_' + sYear)
  
  # set indicators to zero that do not carry over from year to year
  Config.TP.cols.job_loss[:] = np.zeros((Config.adult_county_population),'i')
  Config.TP.cols.job_gain[:] = np.zeros((Config.adult_county_population),'i')
  
  # make new Families table and save object in Config
  Config.TF.copy(newparent='/', newname="Families_" + sYear, overwrite=False, \
    createparents=False, propindexes=True)
  Config.TF = Config.HDF5.root._f_getChild('Families_' + sYear)
  


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def doChecks(Year): 
  
  # savings for persons
  assert np.allclose(Config.TP.cols.save_total[:], Config.TP.cols.save_tokens[:] + \
    Config.TP.cols.save_dollars[:])


  # families ------------------------------------------------------
  assert np.allclose(Config.TF.cols.R_total[:], Config.TF.cols.R_dollars[:] + Config.TF.cols.R_tokens[:])
  assert np.allclose(Config.TF.cols.R_total[:].sum(), Config.TP.cols.R_total[:].sum())
  
  assert np.allclose(Config.TF.cols.R_dollars[:].sum(), Config.TP.cols.R_dollars[:].sum())
  assert np.allclose(Config.TF.cols.R_tokens[:].sum(), Config.TP.cols.R_tokens[:].sum())
  
  assert np.allclose(Config.TF.cols.P_CBFS_dollars[:].sum(), Config.TP.cols.P_CBFS_dollars[:].sum())
  assert np.allclose(Config.TF.cols.P_CBFS_tokens[:].sum(), Config.TP.cols.P_CBFS_tokens[:].sum())

  assert np.allclose(Config.TF.cols.save_dollars[:].sum(), Config.TP.cols.save_dollars[:].sum())
  assert np.allclose(Config.TF.cols.save_tokens[:].sum(), Config.TP.cols.save_tokens[:].sum())
  assert np.allclose(Config.TF.cols.save_total[:].sum(), Config.TP.cols.save_total[:].sum())


  # county --------------------------------------------------------------  

  assert np.allclose(Config.County.R_dollars[Year], Config.TP.cols.R_dollars[:].sum())
  assert np.allclose(Config.County.R_tokens[Year], Config.TP.cols.R_tokens[:].sum())
  assert np.allclose(Config.County.R_total[Year], Config.County.R_dollars[Year] + \
    Config.County.R_tokens[Year])
  
  

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def PrintObj(Obj, Year):
  Config.logRoot.info("\n============ {0:s} ============\nYear = {1:d}".format(Obj.Title, Year))
  K = Obj.__dict__.keys()
  K.remove("Title")
  K.remove("graphGroup")
  K.sort()
  S = '\n'
  for k in K:
    v = Obj.__dict__[k]
    if v is None:
      continue
    if type(v) == type(4.2):
      if (('dollar' in k) or ('token' in k) or ('total' in k) or ('postCBFS' in k) or \
        ('base_wage' in k) or ('income' in k) or ('mean_CBFS' in k) or ('_sum' in k) or \
        ('incentive' in k)) and ('share' not in k) and ('rate' not in k) and ('fraction' not in k) \
        and ('saturation' not in k) and ('ratio' not in k):
        S = S + "{0:<50}   T/D {1:>15,.9G}\n".format(k, np.round(v,0).item()) 
      elif ('threshold_for_membership_family' in k):
        S = S + "{0:<50}   T/D {1:>15,.9G}\n".format(k, np.round(v,0).item())
      else:  
        S = S + "{0:<50}       {1:>15,.4G}\n".format(k, v)    
    elif type(v) == type(4):
      S = S + "{0:<50}       {1:>15,d}\n".format(k, v) 
    else:
      # an array
      if v.dtype == 'd':
        if v.size == 1:
          if (('dollar' in k) or ('token' in k) or ('total' in k) or ('postCBFS' in k) or \
            ('base_wage' in k) or ('income' in k) or ('mean_CBFS' in k) or ('_sum' in k) or \
            ('incentive' in k)) and ('share' not in k) and ('rate' not in k) and ('fraction' not in k) \
            and ('saturation' not in k) and ('ratio' not in k):
            S = S + "{0:<50}   T/D {1:>15,.9G}\n".format(k, np.round(v,0).item()) 
          else:  
            S = S + "{0:<50}       {1:>15,.4G}\n".format(k, v)    
        else:  
          if (('dollar' in k) or ('token' in k) or ('total' in k) or ('postCBFS' in k) or \
            ('base_wage' in k) or ('income' in k) or ('mean_CBFS' in k) or ('_sum' in k) or \
            ('incentive' in k)) and ('share' not in k) and ('rate' not in k) and ('fraction' not in k) \
            and ('saturation' not in k) and ('ratio' not in k):
            S = S + "{0:<50}   T/D {1:>15,.9G}\n".format(k, np.round(v[Year],0).item()) 
          else:  
            S = S + "{0:<50}       {1:>15,.4G}\n".format(k, v[Year])     

      else:
        S = S + "{0:<50}       {1:>15,.9g}\n".format(k, v[Year])   

  S = S + "\n"
  Config.logRoot.info(S)
 

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def plotArrays(Obj, Years_, Years):
  """
  
  Plot the arrays of objects according to graph groups set in __init__() for each object.  Arrays that
  are not included in a graph group are collected in a list called Single.  For graphing purposes, 
  Years_ =  np.arange(Start,Year+1) - Config.burn_in_period + 1.  Years =  np.arange(Start,Year+1).
  
  """
  
  RF = Config.RF
  
  K = Obj.__dict__.keys()
  K.remove('Title')
  K.remove('graphGroup')
  K.sort()

  # pick up any variables not included in graphGroup
  if 'Single' not in Obj.graphGroup.keys():
    Single = []
    for k in K:
      v = Obj.__dict__[k]
      if v is None:
        continue
      if (type(v) == type(4.2)) or (type(v) == type(4)):
        continue 
      else:
        # an array
        if v.size == 1:
          continue
        else:  
          new = 1
          for g in Obj.graphGroup.keys():
            if k in Obj.graphGroup[g]:
              new = 0
              break
          if new==1:
            Single.append(k)
    Obj.graphGroup['Single'] = Single
  
  # plot group variables
  for g in Obj.graphGroup.keys():
    if len(Obj.graphGroup[g]) == 0:
      continue
    if g == "Single":
      continue
    K = Obj.graphGroup[g]
    #K.sort()
    Legend = []
    for k in K:
      pylab.plot(Years_, Obj.__dict__[k][Years])
      Legend.append(k)
    pylab.title(Obj.Title + ": " + g)
    pylab.grid(True)
    pylab.xlabel('Years')
    pylab.legend(Legend, loc=2)
    pylab.tight_layout() 
    pylab.savefig(RF+"/figs/" + Obj.Title + "/" + g + ".png")
    pylab.close()

  # plot single (other) variables
    K = Obj.graphGroup['Single']
    for k in K:
      pylab.plot(Years_, Obj.__dict__[k][Years])
      pylab.title(Obj.Title + ": " + k)
      pylab.grid(True)
      pylab.xlabel('Years')
      pylab.tight_layout() 
      pylab.savefig(RF+"/figs/" + Obj.Title + "/Single_" + k + ".png")
      pylab.close()
    
  
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def graphResults(Year, Start=0):
  """
  
  Graph some specific results and call a function to plot the arrays of objects.  The parameter Start 
  specifies the starting year that some of the graphs plot.  For graphing purposes, consider Year 
  Config.burn_in_period as Year 1 (the first year of tokens).
  
  """  
  
  RF = Config.RF
  
  Config.logRoot.info("\n   ... graphing results, please wait ...\n")
    
  # set upper limit for x & y graph axis, and for upper TSI
  axis_limit_person = 1.5 * Config.threshold_for_membership_family/1000. 
  axis_limit_family = 2.3 * Config.threshold_for_membership_family/1000.
  axis_limit_TSI_multiplier = 1.2
  
  Year_ = Year - Config.burn_in_period + 1
  Years_ =  np.arange(Start,Year+1) - Config.burn_in_period + 1
  Years_all_ =  np.arange(0,Config.simulation_period) - Config.burn_in_period + 1
  Years =  np.arange(Start,Year+1)
  
  if Year >= Config.burn_in_period-1:
    
    # ============================================
    # LEDDA income histograms
    # ============================================
    
    # Save histogram of post-CBFS family income distribution for members. Some might not receive tokens.
    W1 = Config.TF.getWhereList("membership==1") 
    ax = pylab.subplot(1,1,1) 
    x = Config.TF.cols.R_postCBFS_total[:][W1]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 

    pylab.xlim([-1,axis_limit_person])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]

    pylab.title("LEDDA post-CBFS family income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/postCBFS_family_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


    # Save histogram of pre-CBFS family income distribution for members. Some might not receive tokens.
    W1 = Config.TF.getWhereList("membership==1") 
    ax = pylab.subplot(1,1,1) 
    x = Config.TF.cols.R_total[:][W1]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 

    pylab.xlim([-1,axis_limit_family])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]

    pylab.title("LEDDA pre-CBFS family income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Pre-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/preCBFS_family_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  
    

    # Save histogram of post-CBFS person income distribution for members. Some might not receive tokens.
    W1 = Config.TP.getWhereList("membership==1")
    ax = pylab.subplot(1,1,1) 
    x = Config.TP.cols.R_postCBFS_total[:][W1]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 

    pylab.xlim([-1,axis_limit_person])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]

    pylab.title("LEDDA post-CBFS person income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/postCBFS_person_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  

    
    # Save histogram of pre-CBFS person income distribution for members. Some might not receive tokens.
    W1 = Config.TP.getWhereList("membership==1")
    ax = pylab.subplot(1,1,1) 
    x = Config.TP.cols.R_total[:][W1]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 
    ax.axvline(Config.income_target_total[Year]/1000., color='r')

    pylab.xlim([-1,axis_limit_person])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]

    pylab.title("LEDDA pre-CBFS person income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Pre-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/preCBFS_person_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  
    
    
    # ============================================
    # County income histograms
    # ============================================
    
    # Save histograms for post-CBFS family county income
    ax = pylab.subplot(1,1,1) 
    x = Config.TF.cols.R_postCBFS_total[:]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 
    pylab.title("County post-CBFS family income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/County/hist/postCBFS_family_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  

    
    # Save histograms for post-CBFS person county income
    ax = pylab.subplot(1,1,1) 
    x = Config.TP.cols.R_postCBFS_total[:]/1000.
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 
    pylab.title("County post-CBFS person income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/County/hist/postCBFS_person_income_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


  if Year >= Config.burn_in_period:

    # ============================================
    # Other LEDDA histograms and scatter plots
    # ============================================

    # Save histograms for individual TSI based on pre-CBFS income.
    Wt = Config.TP.getWhereList("R_tokens > 0")
    ax = pylab.subplot(1,1,1) 
    x = Config.TP.cols.R_tokens[:][Wt] / Config.TP.cols.R_total[:][Wt]
    ax.hist(x, 100, normed= True)
    ax.set_yticks([])
    ax.axvline(Config.TSI_max, color='r') 
    
    pylab.xlim([-.01, Config.TSI_max * axis_limit_TSI_multiplier])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]    
    
    pylab.title("Token share of pre-CBFS person income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('TSI')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/TSI_preCBFS_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


    # Save hist for individual TSI based on post-CBFS income
    Wt = Config.TP.getWhereList("R_tokens > 0")
    x = Config.TP.cols.R_postCBFS_tokens[:][Wt] / Config.TP.cols.R_postCBFS_total[:][Wt]
    ax = pylab.subplot(1,1,1) 
    ax.hist(x, 100, normed= True)
    ax.set_yticks([]) 
    ax.axvline(Config.TSI_max, color='r') 

    pylab.xlim([-.01, Config.TSI_max * axis_limit_TSI_multiplier])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]    

    pylab.title("Token share of post-CBFS person income, Year = "+ str(Year_))
    pylab.ylabel('Density')
    pylab.xlabel('TSI')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/TSI_postCBFS_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


    # Save scatter plot TSI vs. post-CBFS income for members.  Some members might not receive tokens.
    W1 = Config.TP.getWhereList("membership==1")
    
    Wi0 = Config.TP.getWhereList("(membership==1) & (wage_option==0)")
    Wi1 = Config.TP.getWhereList("(membership==1) & (wage_option==1)")
    Wi2 = Config.TP.getWhereList("(membership==1) & (wage_option==2)")
    
    ax = pylab.subplot(1,1,1)     
    
    x0 = Config.TP.cols.R_postCBFS_total[:][Wi0]/1000.
    y0 = Config.TP.cols.R_tokens[:][Wi0] / Config.TP.cols.R_total[:][Wi0]
    ax.scatter(x0, y0, color='g')
    
    x1 = Config.TP.cols.R_postCBFS_total[:][Wi1]/1000.
    y1 = Config.TP.cols.R_tokens[:][Wi1] / Config.TP.cols.R_total[:][Wi1]
    ax.scatter(x1, y1, color='b')    
    
    x2 = Config.TP.cols.R_postCBFS_total[:][Wi2]/1000.
    y2 = Config.TP.cols.R_tokens[:][Wi2] / Config.TP.cols.R_total[:][Wi2]
    ax.scatter(x2, y2, color='r')    
    
    pylab.xlim([-5,axis_limit_person])
    pylab.ylim([-.01, Config.TSI_max * axis_limit_TSI_multiplier])
    assert Config.TP.cols.R_postCBFS_total[:][W1].min()/1000. >= ax.get_xlim()[0]
    assert Config.TP.cols.R_postCBFS_total[:][W1].max()/1000. <= ax.get_xlim()[1]
    assert (Config.TP.cols.R_tokens[:] / Config.TP.cols.R_total[:])[W1].min() >= ax.get_ylim()[0]
    assert (Config.TP.cols.R_tokens[:] / Config.TP.cols.R_total[:])[W1].max() <= ax.get_ylim()[1]
    
    pylab.legend(['wage_option==0', 'wage_option==1', 'wage_option==2'])    
    pylab.grid(True)
    pylab.title("Post-CBFS person income vs. TSI, Year = "+ str(Year_))
    pylab.ylabel('TSI')
    pylab.xlabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/scatter/postCBFS_person_income_vs_TSI_year=' + \
      str(Year).zfill(2) + '.png')
    pylab.close()      


    # Save plot TSI vs. base wage for members.  Some members might not receive tokens.
    ax = pylab.subplot(1,1,1) 
    
    x0 = Config.TP.cols.base_wage[:][Wi0]/1000
    y0 = Config.TP.cols.R_tokens[:][Wi0] / Config.TP.cols.R_total[:][Wi0]
    ax.scatter(x0, y0, color='g')
    
    x1 = Config.TP.cols.base_wage[:][Wi1]/1000.
    y1 = Config.TP.cols.R_tokens[:][Wi1] / Config.TP.cols.R_total[:][Wi1]
    ax.scatter(x1, y1, color='b')
    
    x2 = Config.TP.cols.base_wage[:][Wi2]/1000.
    y2 = Config.TP.cols.R_tokens[:][Wi2] / Config.TP.cols.R_total[:][Wi2]
    ax.scatter(x2, y2, color='r')
    
    pylab.xlim([-5,axis_limit_person])
    pylab.ylim([-.05, Config.TSI_max * axis_limit_TSI_multiplier])
    assert Config.TP.cols.base_wage[:][W1].min()/1000. >= ax.get_xlim()[0]
    assert Config.TP.cols.base_wage[:][W1].max()/1000. <= ax.get_xlim()[1]
    assert (Config.TP.cols.R_tokens[:] / Config.TP.cols.R_total[:])[W1].min() >= ax.get_ylim()[0]
    assert (Config.TP.cols.R_tokens[:] / Config.TP.cols.R_total[:])[W1].max() <= ax.get_ylim()[1]

    pylab.legend(['wage_option==0', 'wage_option==1', 'wage_option==2'])
    pylab.grid(True)
    pylab.title("Person base income vs. TSI, Year = "+ str(Year_))
    pylab.ylabel('TSI')
    pylab.xlabel('Base income, thousand dollars')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/scatter/base_income_vs_TSI_year=' + str(Year).zfill(2) + '.png')
    pylab.close()    


    # Save scatter plot wage_option vs. base wage for members.  Some members might not receive tokens.
    W1 = Config.TP.getWhereList("membership==1")
    ax = pylab.subplot(1,1,1) 
    ax.scatter(Config.TP.cols.base_wage[:][Wi0]/1000., Config.TP.cols.wage_option[:][Wi0], color='g')
    ax.scatter(Config.TP.cols.base_wage[:][Wi1]/1000., Config.TP.cols.wage_option[:][Wi1], color='b')
    ax.scatter(Config.TP.cols.base_wage[:][Wi2]/1000., Config.TP.cols.wage_option[:][Wi2], color='r')
    pylab.grid(True)
    pylab.title("Person base income vs. wage option choice, Year = "+ str(Year_))
    pylab.ylabel('Wage option')
    pylab.xlabel('Base income, thousand dollars')
    pylab.tight_layout() 
    pylab.savefig(
      RF+'/figs/LEDDA/scatter/base_income_vs_wage_option_year=' + str(Year).zfill(2) + '.png')
    pylab.close()    


    # Save scatter plot base wage vs R_postCBFS
    ax = pylab.subplot(1,1,1) 
    
    x1 = Config.TP.cols.base_wage[:][Wi1]/1000.
    y1 = Config.TP.cols.R_postCBFS_total[:][Wi1]/1000.
    ax.scatter(x1, y1, color='b')
    
    x2 = Config.TP.cols.base_wage[:][Wi2]/1000.
    y2 = Config.TP.cols.R_postCBFS_total[:][Wi2]/1000.
    ax.scatter(x2, y2, color='r')

    pylab.xlim([-5,axis_limit_person])
    pylab.ylim([-5, axis_limit_person])
    assert Config.TP.cols.base_wage[:][W1].min()/1000. >= ax.get_xlim()[0]
    assert Config.TP.cols.base_wage[:][W1].max()/1000. <= ax.get_xlim()[1]
    assert Config.TP.cols.R_postCBFS_total[:][W1].min()/1000. >= ax.get_ylim()[0]
    assert Config.TP.cols.R_postCBFS_total[:][W1].max()/1000. <= ax.get_ylim()[1]

    pylab.legend(['wage_option==1', 'wage_option==2'])
    pylab.grid(True)
    pylab.title("Person base income vs. post-CBFS income, Year = "+ str(Year_))
    pylab.xlabel('Base income, thousand dollars')
    pylab.ylabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/scatter/base_income_R_postCBFS_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


    # Save scatter plot and histogram of post-CBFS family income gain from current base wage
    P0 = Config.TP.getWhereList("(membership==1) & (work_status != 0) & (work_status != 2)")
    Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0 = \
      Config.Persons.getFamilyData(P0) 
    JL = JobLoss.sum(1)
    Wj = np.where(JL==0)[0]
    postCBFS = np.column_stack((Config.TP.cols.R_postCBFS_total[:][Persons[:,0]], \
        Config.TP.cols.R_postCBFS_total[:][Persons[:,1]]))
    postCBFS = postCBFS[Wj].sum(1)
    
    BW = BaseWage[Wj].sum(1)
    Gain = postCBFS - BW
    assert np.all(Gain > 0)
    
    families = Config.TP.cols.fid[:][Persons[:,0]][Wj]
    FWO = Config.TF.cols.wage_option[:][families]
    assert np.all(FWO > 0)
    
    W1 = np.where(FWO==1)[0]
    W2 = np.where(FWO==2)[0]

    if (W1.size > 0) or (W2.size>0):
      # gain compared to current base wage
      ax = pylab.subplot(1,1,1) 
      x1 = (BW/1000.)[W1]
      y1 = Gain[W1]/100.
      ax.scatter(x1, y1, color='b')
      
      x2 = (BW/1000.)[W2]
      y2 = Gain[W2]/1000.
      ax.scatter(x2, y2, color='r')    
      
      pylab.legend(['Option 1', 'Option 2'])
      pylab.grid(True)
      pylab.title("Family post-CBFS income gain over base, Year = "+ str(Year_))
      pylab.xlabel('Family base income, thousand dollars')
      pylab.ylabel('Family gain, thousand T&D')
      pylab.tight_layout() 
      pylab.savefig(RF+'/figs/LEDDA/scatter/postCBFS_income_gain_year=' + str(Year).zfill(2) + '.png')
      pylab.close() 


    # Save histogram of gain
    ax = pylab.subplot(1,1,1) 
    x = Gain/1000.
    ax.hist(x, 100, normed=True)
    ax.set_yticks([])
    pylab.title("Family post-CBFS income gain over base, Year = "+ str(Year_))
    pylab.xlabel('Family gain, thousand T&D')
    pylab.ylabel('Density')
    
    pylab.xlim([-1,axis_limit_person])
    assert x.min() >= ax.get_xlim()[0]
    assert x.max() <= ax.get_xlim()[1]

    pylab.tight_layout() 
    pylab.savefig(RF+'/figs/LEDDA/hist/postCBFS_income_gain_year=' + str(Year).zfill(2) + '.png')
    pylab.close()  


    # Save scatter plot and histogram of post-CBFS family income year-to-year loss, only for those 
    # families where no person had a job loss.
    P0 = Config.TP.getWhereList("(membership==1) & (work_status != 0) & (work_status != 2)")
    Persons, BaseWage, WorkStatus, Membership, JobGain, JobLoss, BaseWage0 = \
      Config.Persons.getFamilyData(P0) 
    JL = JobLoss.sum(1)
    Wj = np.where(JL==0)[0]
    
    # current year post-CBFS income
    postCBFS = np.column_stack((Config.TP.cols.R_postCBFS_total[:][Persons[:,0]], \
        Config.TP.cols.R_postCBFS_total[:][Persons[:,1]]))
    postCBFS = postCBFS[Wj].sum(1)

    # last year's post-CBFS income
    postCBFS_old = np.column_stack((Config.TP_old.cols.R_postCBFS_total[:][Persons[:,0]], \
        Config.TP_old.cols.R_postCBFS_total[:][Persons[:,1]]))
    postCBFS_old = postCBFS_old[Wj].sum(1)

    # loss
    Loss = np.minimum(0, postCBFS - postCBFS_old)
    
    Config.logRoot.debug("\nMinimum year-to-year family income loss = {0:,.9g} T&D\n".format(
      np.round(Loss.min(),0).item()))
    
    WL = np.where(Loss < -1)[0]
    Loss = Loss[WL]
    BW = BaseWage[Wj][WL].sum(1)
    
    families = Config.TP.cols.fid[:][Persons[:,0]][Wj][WL]
    FWO = Config.TF.cols.wage_option[:][families]
    assert np.all(FWO > 0)
    
    W1 = np.where(FWO==1)[0]
    W2 = np.where(FWO==2)[0]

    if (W1.size > 0) or (W2.size>0):
      ax = pylab.subplot(1,1,1) 
      x1 = (BW/1000.)[W1]
      y1 = Loss[W1]
      ax.scatter(x1, y1, color='b')
      
      x2 = (BW/1000.)[W2]
      y2 = Loss[W2]
      ax.scatter(x2, y2, color='r')    
      
      pylab.legend(['Option 1', 'Option 2'])
      pylab.grid(True)
      pylab.title("Year-to-year family post-CBFS income loss, Year = "+ str(Year_))
      pylab.xlabel('Family base income, thousand dollars')
      pylab.ylabel('Family loss, T&D')
      pylab.tight_layout() 
      pylab.savefig(RF+'/figs/LEDDA/scatter/postCBFS_income_loss_year=' + str(Year).zfill(2) + '.png')
      pylab.close() 

  if Year < 1:
    return

  if Year <= Start:
    return

  # ============================================
  # County and LEDDA plots, x axis == year
  # ============================================

  if Config.make_annimations == True:
    # Save plot of county post-CBFS family income (for animations)
    pylab.plot(Years_, Config.County.post_CBFS_family_income_total_mean[Years]/1e3,'-b')
    pylab.plot(Years_, Config.County.post_CBFS_family_income_total_plus_savings_mean[Years]/1e3,'--r', \
      lw=2)
    pylab.title("County post-CBFS family mean income, Year = "+ str(Year_))
    pylab.legend(['without CBFS savings', 'with CBFS savings'], loc=2)
    pylab.grid(True)
    pylab.xlim([Years_all_[0], Years_all_[-1]])
    pylab.ylim([30, axis_limit_family])
    pylab.xlabel('Years')
    pylab.ylabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+"/figs/County/plot/postCBFS_family_income_year=" + str(Year).zfill(2) + '.png')
    pylab.close()
  

  # Save plot of county post-CBFS family income (all years on one plot)
  pylab.plot(Years_, Config.County.post_CBFS_family_income_total_mean[Years]/1e3,'-b')
  pylab.plot(Years_, Config.County.post_CBFS_family_income_total_plus_savings_mean[Years]/1e3,'--r',lw=2)
  pylab.title("County post-CBFS mean family income")
  pylab.legend(['without CBFS savings', 'with CBFS savings'], loc=2)
  pylab.grid(True)
  pylab.xlabel('Years')
  pylab.ylabel('Post-CBFS income, thousand T&D')
  pylab.tight_layout() 
  pylab.savefig(RF+"/figs/County/plot_postCBFS_family_income.png")
  pylab.close()


  if Config.make_annimations == True:
    # Save plot of LEDDA post-CBFS family income (for animations)
    pylab.plot(Years_, Config.Ledda.post_CBFS_family_income_total_mean[Years]/1e3,'-b')
    pylab.plot(Years_, Config.Ledda.post_CBFS_family_income_total_plus_savings_mean[Years]/1e3,'--r', \
      lw=2)
    pylab.title("Post-CBFS mean family income, Year = "+ str(Year_))
    pylab.legend(['without CBFS savings', 'with CBFS savings'], loc=2)
    pylab.grid(True)
    pylab.xlim([Years_all_[0], Years_all_[-1]])
    pylab.ylim([30, axis_limit_family])
    pylab.xlabel('Years')
    pylab.ylabel('Post-CBFS income, thousand T&D')
    pylab.tight_layout() 
    pylab.savefig(RF+"/figs/LEDDA/plot/postCBFS_family_income_year=" + str(Year).zfill(2) + '.png')
    pylab.close()


  # Save plot of LEDDA post-CBFS family income (all years on one plot)
  pylab.plot(Years_, Config.Ledda.post_CBFS_family_income_total_mean[Years]/1e3,'-b')
  pylab.plot(Years_, Config.Ledda.post_CBFS_family_income_total_plus_savings_mean[Years]/1e3,'--r', lw=2)
  pylab.title("Post-CBFS mean family income")
  pylab.legend(['without CBFS savings', 'with CBFS savings'], loc=2)
  pylab.grid(True)
  pylab.xlabel('Years')
  pylab.ylabel('Post-CBFS income, thousand T&D')
  pylab.tight_layout() 
  pylab.savefig(RF+"/figs/LEDDA/plot_postCBFS_family_income.png")
  pylab.close()
  

  # plot arrays of all objects
  plotArrays(Config.County, Years_, Years)
  plotArrays(Config.Ledda, Years_, Years)
  plotArrays(Config.Org, Years_, Years)
  plotArrays(Config.Persons, Years_, Years)
  plotArrays(Config.Gov, Years_, Years)
  plotArrays(Config.Cbfs, Years_, Years)
  plotArrays(Config.Roc, Years_, Years)



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def makeAnnimations():
  """
  
  Create gif animations from saved png images.
  
  """
  
  RF = Config.RF
  
  if Config.make_annimations == True:
    
    # ============================================
    # annimations, hist
    # ============================================

    # post-CBFS family income, LEDDA 
    L = glob.glob(RF+"/figs/LEDDA/hist/postCBFS_family_income_year=*.png")
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/LEDDA/annimations/hist_postCBFS_family_income.gif')
    imgs.close()


    # post-CBFS person income, LEDDA 
    L = glob.glob(RF+"/figs/LEDDA/hist/postCBFS_person_income_year=*.png")
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/LEDDA/annimations/hist_postCBFS_person_income.gif')
    imgs.close()
    

    # pre-CBFS family income, LEDDA 
    L = glob.glob(RF+'/figs/LEDDA/hist/preCBFS_family_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/LEDDA/annimations/hist_preCBFS_family_income.gif')
    imgs.close()


    # pre-CBFS person income, LEDDA 
    L = glob.glob(RF+'/figs/LEDDA/hist/preCBFS_person_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/LEDDA/annimations/hist_preCBFS_person_income.gif')
    imgs.close()


    # post-CBFS family income, county 
    L = glob.glob(RF+'/figs/County/hist/postCBFS_family_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120           
    imgs.save(filename=RF+'/figs/County/annimations/hist_postCBFS_family_income.gif')
    imgs.close()


    # post-CBFS person income, county 
    L = glob.glob(RF+'/figs/County/hist/postCBFS_person_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120           
    imgs.save(filename=RF+'/figs/County/annimations/hist_postCBFS_person_income.gif')  
    imgs.close()  

    
    # post-CBFS gain
    L = glob.glob(RF+'/figs/LEDDA/hist/postCBFS_income_gain_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120           
    imgs.save(filename=RF+'/figs/LEDDA/annimations/hist_postCBFS_income_gain.gif')  
    imgs.close()  




    # ============================================
    # annimations, plots, x axis == year
    # ============================================
    
    # post-CBFS family income, LEDDA 
    L = glob.glob(RF+'/figs/LEDDA/plot/postCBFS_family_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/LEDDA/annimations/plot_postCBFS_family_income.gif')
    imgs.close()
    
    
    # post-CBFS family income, County
    L = glob.glob(RF+'/figs/County/plot/postCBFS_family_income_year=*.png')
    L.sort()
    imgs = Image(filename=L[0])
    for i in L[1:]:
      im2 = Image(filename=i)
      imgs.sequence.append(im2)
    for i in range(len(imgs.sequence)):
      with imgs.sequence[i] as frame:
        if (i==0) or (i==len(imgs.sequence)-1):
          frame.delay = 250  
        else:
          frame.delay = 120      
    imgs.save(filename=RF+'/figs/County/annimations/plot_postCBFS_family_income.gif')   
    imgs.close() 
    
      
      
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def saveData():
  """
  
  Save objects to disk at the end of the simulation.
  
  """  
  
  Config.HDF5.close()
  RF = Config.RF
  
  
  file1 = open(RF+"/data/results_County.pickle", "w") 
  cPickle.dump(Config.County,file1,2)
  file1.close()   

  file1 = open(RF+"/data/results_Ledda.pickle", "w") 
  cPickle.dump(Config.Ledda,file1,2)
  file1.close()   

  file1 = open(RF+"/data/results_Org.pickle", "w") 
  cPickle.dump(Config.Org,file1,2)
  file1.close()   

  file1 = open(RF+"/data/results_Gov.pickle", "w") 
  cPickle.dump(Config.Gov,file1,2)
  file1.close()     

  file1 = open(RF+"/data/results_CBFS.pickle", "w") 
  cPickle.dump(Config.Cbfs,file1,2)
  file1.close()   

  file1 = open(RF+"/data/results_Persons.pickle", "w") 
  cPickle.dump(Config.Persons,file1,2)
  file1.close()   

  file1 = open(RF+"/data/results_ROC.pickle", "w") 
  cPickle.dump(Config.Roc,file1,2)
  file1.close()   

    
  # Note: to open saved objects, use, for example (where RF is given as above):
  # file1 = open(RF+"/data/results_Persons.pickle", "r") 
  # Persons = cPickle.load(file1)
  # file1.close()
  #
  # To open the saved HDF5 file, see the last group of lines in InitializeFx.py under the heading
  # "--- open HDF5 file ---"


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def graphPerson(IDD):
  """
  
  This utility function prints and plots the history of data stored in the person's table for an 
  individual.  IDD is the person's pid in Config.TP.  This function is not called in the simulation, but 
  can be called by the user as an aid to diagnose errors.
  
  """
  RF = Config.RF
  
  childs = Config.HDF5.root._v_children.keys()
  childs = [name for name in childs if 'Person' in name]
  childs.sort()
  Year = [int(name[-2:]) for name in childs] 
  
  Cols = np.array(Config.HDF5.root._f_getChild(childs[0]).colnames)
  Cols = Cols[Cols != 'pid']
  Cols.sort()
  
  Data = {}
  for c in Cols:
    data = np.zeros((len(Year)),'d')
    for y in Year:
      data[y] = Config.HDF5.root._f_getChild(childs[y]).cols.__dict__[c][IDD]
    Data[c] = data

  # plot data ----------------------------

  graphGroup = {}
  graphGroup['work_status'] = ['work_status', 'membership', 'wage_option']
  graphGroup['jobs'] = ['number_job_gains', 'number_job_losses', 'job_gain', 'job_loss']
  graphGroup['wages+tokens'] = ['R_wages_SB_tokens', 'R_wages_PB_tokens', 'R_wages_NP_tokens']
  graphGroup['wages+dollars'] = ['R_wages_SB_dollars', 'R_wages_PB_dollars', 'R_wages_NP_dollars', 
    'base_wage']
  graphGroup['nurture'] = ['R_CBFS_nurture_tokens', 'R_CBFS_nurture_dollars', 'R_gov_support_dollars']
  graphGroup['P+CBFS+loan+tokens'] = ['P_CBFS_loan_SB_tokens', 'P_CBFS_loan_PB_tokens', 
    'P_CBFS_loan_NP_tokens']
  graphGroup['P+CBFS+loan+dollars'] = ['P_CBFS_loan_SB_dollars', 'P_CBFS_loan_PB_dollars', 
    'P_CBFS_loan_NP_dollars']
  graphGroup['P+CBFS+other+tokens'] = ['P_CBFS_subsidy_SB_tokens', 'P_CBFS_subsidy_PB_tokens', 
    'P_CBFS_donation_NP_tokens', 'P_CBFS_nurture_tokens']
  graphGroup['P+CBFS+other+dollars'] = ['P_CBFS_subsidy_SB_dollars', 'P_CBFS_subsidy_PB_dollars', 
    'P_CBFS_donation_NP_dollars', 'P_CBFS_nurture_dollars']
  graphGroup['P+CBFS+total'] = ['P_CBFS_tokens', 'P_CBFS_dollars', 'P_CBFS_total']
  graphGroup['P+other'] = ['P_spending_tokens', 'P_spending_dollars', 'P_gov_tax_dollars', 
    'P_donation_NP_dollars']
  graphGroup['R+total'] = ['R_tokens', 'R_dollars', 'R_total']
  
  graphGroup['R+total+post'] = ['R_postCBFS_tokens', 'R_postCBFS_dollars', 'R_postCBFS_total', 
    'R_postCBFS_total_prelim']
  graphGroup['P+total'] = ['P_tokens', 'P_dollars', 'P_total']
  graphGroup['save'] = ['save_tokens', 'save_dollars', 'save_total']

  for Title in graphGroup:
    print "\n\n*** Person ", str(IDD), ": ", Title
    Legend = []
    for c in graphGroup[Title]:
      pylab.plot(Year, Data[c])
      Legend.append(c)
      print c, Data[c], "\n"
    pylab.title("Person: " + str(IDD) + ": " + Title)
    pylab.grid(True)
    pylab.xlabel('Years')
    pylab.legend(Legend, loc=2)
    pylab.tight_layout() 
    pylab.savefig(RF+ "/"+ str(IDD) + "_" + Title + ".png")
    pylab.close()

  print "\n\n"


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
class ParameterError(Exception):
  """
   
  Generic exception handling.
  
  """
  pass
  

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
def errorCode(code):
  """
  
  Error codes and information that can help a user understand what has gone wrong.
  
  """
  
  if code == 1000:
    Config.logRoot.info("""

******************************************************************************************
Error Code 1000:

Token and/or dollar contributions to the CBFS donation fund are insufficient to cover wage obligations 
for LFNJ nonprofit employees.  Increase the donation earmark in Config, decrease the NP lending earmark 
(to create fewer jobs), increase the token share of CBFS contributions, increase the target token share 
of income, or take other measures.

******************************************************************************************

""")

  elif code == 1010:
    Config.logRoot.info("""

******************************************************************************************
Error Code 1010:

A negative token and/or dollar income occurs after CBFS contributions are made.  Quite likely, the 
multiplication factors to control token share of contributions are too high, or earmarks are too high.  
Decrease either or take other measures.

******************************************************************************************

""")    

  elif code == 1020:
    Config.logRoot.info("""

******************************************************************************************
Error Code 1020:

Token and/or dollar contributions to the CBFS nurture fund are insufficient to cover wage obligations 
for unemployed and NIWF supported members.  Increase the nurture earmark in Config, increase the token 
share of CBFS contributions, increase the target token share of income, or take other measures.

******************************************************************************************

""")   





  else:
    Config.logRoot.info("\n *** Error code not recognized ***\n")
    raise ParameterError 


