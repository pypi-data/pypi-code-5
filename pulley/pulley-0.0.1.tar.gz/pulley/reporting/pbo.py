# PBO = Probability of Overfitting
# http://www.quantresearch.info/
# lopezdeprado@lbl.gov

import numpy as np, scipy.stats as ss, pandas as pd, datetime as dt
from random import gauss
from itertools import product

# implements the PBO estimation via Monte Carlo. 
def testAccuracy_MC(sr_base,sr_case):
	# Test the accuracy of CSCV against hold-out
	# It generates numTrials random samples and directly computes the …
	# … proportion where OOS performance was below the median.
	length,numTrials,numMC=1000,100,1000
	pathOutput='H:/Studies/Quant #23/paper/'
	#1) Determine mu,sigma
	mu_base,sigma_base=sr_base/(365.25*5/7.),1/(365.25*5/7.)**.5
	mu_case,sigma_case=sr_case/(365.25*5/7.),1/(365.25*5/7.)**.5
	hist,probOverfit=[],0
	#2) Generate trials
	for m in range(numMC):
		for i in range(1,numTrials):
			j=np.array([gauss(0,1) for j in range(length)])
			j*=sigma_base/np.std(j) # re-scale
			j+=mu_base-np.mean(j) # re-center
			j=np.reshape(j,(j.shape[0],1))
			if i==1:pnl=np.copy(j)
			else:pnl=np.append(pnl,j,axis=1)
		#3) Add test case
		j=np.array([gauss(0,1) for j in range(length)])
		j*=sigma_case/np.std(j) # re-scale
		j+=mu_case-np.mean(j) # re-center
		j=np.reshape(j,(j.shape[0],1))
		pnl=np.append(pnl,j,axis=1)
		#4) Run test
		# Reference distribution
		mu_is=[np.average(pnl[:length/2,i]) for i in range(pnl.shape[1])]
		sigma_is=[np.std(pnl[:length/2,i]) for i in range(pnl.shape[1])]
		mu_oos=[np.average(pnl[length/2:,i]) for i in range(pnl.shape[1])]
		sigma_oos=[np.std(pnl[length/2:,i]) for i in range(pnl.shape[1])]
		sr_is=[mu_is[i]/sigma_is[i] for i in range(len(mu_is))]
		sr_oos=[mu_oos[i]/sigma_oos[i] for i in range(len(mu_oos))]
		print m,sr_is.index(max(sr_is)),max(sr_is), \
			sr_oos[sr_is.index(max(sr_is))]
		sr_oos_=sr_oos[sr_is.index(max(sr_is))]
		hist.append(sr_oos_)
		if sr_oos_<np.median(sr_oos):probOverfit+=1
	probOverfit/=float(numMC)
	print probOverfit
	return

# implements the PBO estimation by Extreme Value Theory
def testAccuracy_EVT(sr_base,sr_case):
	# Test accuracy by numerical integration
	# It does the same as testAccuracy_MC, but through numerical integration ...
	# ... of the base and case distributions.
	#1) Parameters
	parts,length,freq,minX,trials=1e4,1000,365.25*5/7.,-10,100
	emc=0.57721566490153286 # Euler-Mascheroni constant
	#2) SR distributions
	dist_base=[sr_base,((freq+.5*sr_base**2)/length)**.5]
	dist_case=(sr_case,((freq+.5*sr_case**2)/length)**.5)
	#3) Fit Gumbel (method of moments)
	maxList=[]
	for x in range(int(parts)):
		max_=max([gauss(dist_base[0],dist_base[1]) for i in range(trials)])
		maxList.append(max_)
	dist_base[1]=np.std(maxList)*6**.5/math.pi
	dist_base[0]=np.mean(maxList)-emc*dist_base[1]
	#4) Integration
	prob1=0
	for x in np.linspace(minX*dist_case[1],2*dist_case[0]-sr_base,parts):
		f_x=ss.norm.pdf(x,dist_case[0],dist_case[1])
		F_y=1-ss.gumbel_r.cdf(x,dist_base[0],dist_base[1])
		prob1+=f_x*F_y
	prob1*=(2*dist_case[0]-sr_base-minX*dist_case[1])/parts
	prob2=1-ss.norm.cdf(2*dist_case[0]-sr_base,dist_case[0],dist_case[1])
	print dist_base,dist_case
	print prob1,prob2,prob1+prob2
	return

# Simulates the performance of a seasonal trading strategy under various overfitting scenarios,
# which can be used to corroborate the Probability of BacktestOverfitting (PBO) usefulness in real
# investment applications.
#----------------------------------------------------------------------------------------
def getRefDates_MonthBusinessDate(dates):
	refDates,pDay={},[]
	first=dt.date(year=dates[0].year,month=dates[0].month,day=1)
	m=dates[0].month
	d=numBusinessDays(first,dates[0])+1
	for i in dates:
		if m!=i.month:m,d=i.month,1
		pDay.append(d)
		d+=1
	for j in range(1,30):
		lst=[dates[i] for i in range(len(dates)) if pDay[i]==j]
		refDates[j]=lst
	return refDates
#----------------------------------------------------------------------------------------
def numBusinessDays(date0,date1):
	m,date0_=1,date0
	while True:
		date0_+=dt.timedelta(days=1)
		if date0_>=date1:break
		if date0_.isoweekday()<6:m+=1
	return m
#----------------------------------------------------------------------------------------
def getTrades(series,dates,refDates,exit,stopLoss,side):
	# Get trades
	trades,pnl,position_,j,num=[],0,0,0,None
	for i in range(1,len(dates)):
		# Find next roll and how many trading dates to it
		if dates[i]>=refDates[j]:
			if dates[i-1]<refDates[j]:num,pnl=0,0
			if j<len(refDates)-1:
				while dates[i]>refDates[j]:j+=1
		if num==None:continue
		# Trading rule
		position=0
		if num<exit and pnl>stopLoss:position=side
		if position!=0 or position_!=0:
			trades.append([dates[i],num,position,position_*(series[i]-series[i-1])])
			pnl+=trades[-1][3]
			position_=position
		num+=1
	return trades
#----------------------------------------------------------------------------------------
def computePSR(stats,obs,sr_ref=0,moments=4):
	#Compute PSR
	stats_=[0,0,0,3]
	stats_[:moments]=stats[:moments]
	sr=stats_[0]/stats_[1]
	psrStat=(sr-sr_ref)*(obs-1)**0.5/(1-sr*stats_[2]+sr**2*(stats_[3]-1)/4.)**0.5
	psr=ss.norm.cdf((sr-sr_ref)*(obs-1)**0.5/(1-sr*stats_[2]+sr**2*(stats_[3]-1)/4.)**0.5)
	return psrStat,psr
#----------------------------------------------------------------------------------------
def attachTimeSeries(series,series_,index=None,label='',how='outer'):
	# Attach a time series to a pandas dataframe
	if not isinstance(series_,pd.DataFrame):
		series_=pd.DataFrame({label:series_},index=index)
	elif label!='':series_.columns=[label]
	if isinstance(series,pd.DataFrame):
		series=series.join(series_,how=how)
	else:
		series=series_.copy(deep=True)
	return series
#----------------------------------------------------------------------------------------
def evalPerf(pnl,date0,date1,sr_ref=0):
	freq=float(len(pnl))/((date1-date0).days+1)*365.25
	m1=np.mean(pnl)
	m2=np.std(pnl)
	m3=ss.skew(pnl)
	m4=ss.kurtosis(pnl,fisher=False)
	sr=m1/m2*freq**.5
	psr=computePSR([m1,m2,m3,m4],len(pnl),sr_ref=sr_ref/freq**.5,moments=4)[0]
	return sr,psr,freq
#----------------------------------------------------------------------------------------
def backTest(nDays=0,factor=0):
	#1) Input parameters --- to be changed by the user
	holdingPeriod,sigma,stopLoss,length=20,1,10,1000
	#2) Prepare series
	date_,dates=dt.date(year=2000,month=1,day=1),[]
	while len(dates)<length:
		if date_.isoweekday()<5:dates.append(date_)
		date_+=dt.timedelta(days=1)
	series=np.empty((length))
	for i in range(series.shape[0]):
		series[i]=gauss(0,sigma)
		pDay_=dt.date(year=dates[i].year,month=dates[i].month,day=1)
		if numBusinessDays(pDay_,dates[i])<=nDays:
			series[i]+=sigma*factor
	series=np.cumsum(series)
	#3) Optimize
	refDates=getRefDates_MonthBusinessDate(dates)
	psr,sr,trades,sl,freq,pDay,pnl,count=None,None,None,None,None,None,None,0
	for pDay_ in refDates.keys():
		refDates_=refDates[pDay_]
		if len(refDates_)==0:continue
		#4) Get trades
		for prod_ in product(range(holdingPeriod+1),range(-stopLoss,1),[-1,1]):
			count+=1
			trades_=getTrades(series,dates,refDates_,prod_[0],prod_[1]*sigma, \
				prod_[2])
			dates_,pnl_=[j[0] for j in trades_],[j[3] for j in trades_]
			#5) Eval performance
			if len(pnl_)>2:
				#6) Reconcile PnL
				pnl=attachTimeSeries(pnl,pnl_,dates_,count)
				#7) Evaluate
				sr_,psr_,freq_=evalPerf(pnl_,dates[0],dates[-1])
				for j in range(1,len(pnl_)):pnl_[j]+=pnl_[j-1]
				if sr==None or sr_>sr:
					psr,sr,trades=psr_,sr_,trades_
					freq,pDay,prod=freq_,pDay_,prod_
					print count,pDay,prod,round(sr,2), \
						round(freq,2),round(psr,2)
	print 'Total # iterations='+str(count)
	return pnl,psr,sr,trades,freq,pDay,prod,dates,series

