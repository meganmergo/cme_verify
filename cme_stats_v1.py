# cme_stats_v1.py
#
# analyses HELCATS ICMECAT data for paper on CME statistics
# Author: C. Moestl, Space Research Institute IWF Graz, Austria
# started May 2015
# last update: February 2018


from scipy import stats
import scipy.io
from matplotlib import cm
import sys
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import sunpy.time
import time
import pickle
import seaborn as sns


def getcat(filename):
  print('reading CAT')
  cat=scipy.io.readsav(filename, verbose='true')  
  print('done CAT')
  return cat  
  
def decode_array(bytearrin):
 #for decoding the strings from the IDL .sav file to a list of python strings, not bytes 
 #make list of python lists with arbitrary length
 bytearrout= ['' for x in range(len(bytearrin))]
 for i in range(0,len(bytearrin)-1):
  bytearrout[i]=bytearrin[i].decode()
 #has to be np array so to be used with numpy "where"
 bytearrout=np.array(bytearrout)
 return bytearrout  
  

def time_to_num_cat(time_in):  

  #for time conversion from catalogue .sav to numerical time
  #this for 1-minute data or lower time resolution

  #for all catalogues
  #time_in is the time in format: 2007-11-17T07:20:00 or 2007-11-17T07:20Z
  #for times help see: 
  #http://docs.sunpy.org/en/latest/guide/time.html
  #http://matplotlib.org/examples/pylab_examples/date_demo2.html
  
  j=0
  #time_str=np.empty(np.size(time_in),dtype='S19')
  time_str= ['' for x in range(len(time_in))]
  #=np.chararray(np.size(time_in),itemsize=19)
  time_num=np.zeros(np.size(time_in))
  
  for i in time_in:

   #convert from bytes (output of scipy.readsav) to string
   time_str[j]=time_in[j][0:16].decode()+':00'
   year=int(time_str[j][0:4])
   time_str[j]
   #convert time to sunpy friendly time and to matplotlibdatetime
   #only for valid times so 9999 in year is not converted
   #pdb.set_trace()
   if year < 2100:
    	  time_num[j]=mdates.date2num(sunpy.time.parse_time(time_str[j]))
   j=j+1  
   #the date format in matplotlib is e.g. 735202.67569444
   #this is time in days since 0001-01-01 UTC, plus 1.
   
   #return time_num which is already an array and convert the list of strings to an array
  return time_num, np.array(time_str)


def IDL_time_to_num(time_in):  
 #convert IDL time to matplotlib datetime
 time_num=np.zeros(np.size(time_in))
 for ii in np.arange(0,np.size(time_in)):
   time_num[ii]=mdates.date2num(sunpy.time.parse_time(time_in[ii]))   
 return time_num 
  


def gaussian(x, amp, mu, sig):
     return amp * exp(-(x-cen)**2 /wid)


def dynamic_pressure(density, speed):
   ############# make dynamic pressure
   #pdyn=np.zeros(len([density])) #in nano Pascals
   protonmass=1.6726219*1e-27  #kg
   #assume pdyn is only due to protons
   pdyn=np.multiply(np.square(speed*1e3),density)*1e6*protonmass*1e9  #in nanoPascal
   return pdyn




######################################################
#main program

plt.close('all')
print('Start catpy main program. Analyses and plots for ICME duration and planetary (Mars!) impacts')


#-------------------------------------------------------- get cats
#filename_arrcat='ALLCATS/HELCATS_ARRCAT_v6.sav'
#a=getcat(filename_arrcat)

filename_icmecat='ALLCATS/HELCATS_ICMECAT_v20_SCEQ.sav'
i=getcat(filename_icmecat)

#filename_linkcat='ALLCATS/HELCATS_LINKCAT_v10.sav'
#l=getcat(filename_linkcat)


#now this is a structured array  
#access each element of the array see http://docs.scipy.org/doc/numpy/user/basics.rec.html
#access variables
#i.icmecat['id']
#look at contained variables
#print(a.arrcat.dtype)
#print(i.icmecat.dtype)


#get spacecraft and planet positions
pos=getcat('../catpy/DATACAT/positions_2007_2018_HEEQ_6hours.sav')
pos_time_num=time_to_num_cat(pos.time)[0]
#---------------------------- get all parameters from ICMECAT


iid=i.icmecat['id']
#need to decode all strings
iid=decode_array(iid)

isc=i.icmecat['sc_insitu'] #string
isc=decode_array(isc)

icme_start_time=i.icmecat['ICME_START_TIME']
[icme_start_time_num,icme_start_time_str]=time_to_num_cat(icme_start_time)

mo_start_time=i.icmecat['MO_START_TIME']
[mo_start_time_num,mo_start_time_str]=time_to_num_cat(mo_start_time)

mo_end_time=i.icmecat['MO_END_TIME']
[mo_end_time_num,mo_end_time_str]=time_to_num_cat(mo_end_time)

icme_end_time=i.icmecat['ICME_END_TIME']
[icme_end_time_num,icme_end_time_str]=time_to_num_cat(icme_end_time)

sc_heliodistance=i.icmecat['SC_HELIODISTANCE']
sc_long_heeq=i.icmecat['SC_LONG_HEEQ']
sc_lat_heeq=i.icmecat['SC_LAT_HEEQ']
mo_bmax=i.icmecat['MO_BMAX']
mo_bmean=i.icmecat['MO_BMEAN']
mo_bstd=i.icmecat['MO_BSTD']
mo_bzmean=i.icmecat['MO_BZMEAN']
mo_bzmin=i.icmecat['MO_BZMIN']
mo_duration=i.icmecat['MO_DURATION']
mo_mva_axis_long=i.icmecat['MO_MVA_AXIS_LONG']
mo_mva_axis_lat=i.icmecat['MO_MVA_AXIS_LAT']
mo_mva_ratio=i.icmecat['MO_MVA_RATIO']
sheath_speed=i.icmecat['SHEATH_SPEED']
sheath_speed_std=i.icmecat['SHEATH_SPEED_STD']
mo_speed=i.icmecat['MO_SPEED']
mo_speed_st=i.icmecat['MO_SPEED_STD']
sheath_density=i.icmecat['SHEATH_DENSITY']
sheath_density_std=i.icmecat['SHEATH_DENSITY_STD']
mo_density=i.icmecat['MO_DENSITY']
mo_density_std=i.icmecat['MO_DENSITY_STD']
sheath_pdyn=i.icmecat['SHEATH_PDYN']
sheath_pdyn_std=i.icmecat['SHEATH_PDYN_STD']
mo_pdyn=i.icmecat['MO_PDYN']
mo_pdyn_std=i.icmecat['MO_PDYN_STD']


sheath_temperature=i.icmecat['SHEATH_TEMPERATURE']
sheath_temperature_std=i.icmecat['SHEATH_TEMPERATURE_STD']
mo_temperature=i.icmecat['MO_TEMPERATURE']
mo_temperature_std=i.icmecat['MO_TEMPERATURE_STD']


#get indices of events in different spacecraft
ivexind=np.where(isc == 'VEX')
istaind=np.where(isc == 'STEREO-A')
istbind=np.where(isc == 'STEREO-B')
iwinind=np.where(isc == 'Wind')
imesind=np.where(isc == 'MESSENGER')
iulyind=np.where(isc == 'ULYSSES')
imavind=np.where(isc == 'MAVEN')


#take MESSENGER only at Mercury, only events after orbit insertion
imercind=np.where(np.logical_and(isc =='MESSENGER',icme_start_time_num > mdates.date2num(sunpy.time.parse_time('2011-03-18'))))

#limits of solar minimum, rising phase and solar maximum

minstart=mdates.date2num(sunpy.time.parse_time('2007-01-01'))
minend=mdates.date2num(sunpy.time.parse_time('2009-12-31'))

risestart=mdates.date2num(sunpy.time.parse_time('2010-01-01'))
riseend=mdates.date2num(sunpy.time.parse_time('2011-06-30'))

maxstart=mdates.date2num(sunpy.time.parse_time('2011-07-01'))
maxend=mdates.date2num(sunpy.time.parse_time('2014-12-31'))


#extract events by limits of solar min, rising, max, too few events for MAVEN and Ulysses


iallind_min=np.where(np.logical_and(icme_start_time_num > minstart,icme_start_time_num < minend))
iallind_rise=np.where(np.logical_and(icme_start_time_num > risestart,icme_start_time_num < riseend))
iallind_max=np.where(np.logical_and(icme_start_time_num > maxstart,icme_start_time_num < maxend))

iwinind_min=np.where(np.logical_and(icme_start_time_num[iwinind] > minstart,icme_start_time_num[iwinind] < minend))
iwinind_rise=np.where(np.logical_and(icme_start_time_num[iwinind] > risestart,icme_start_time_num[iwinind] < riseend))
iwinind_max=np.where(np.logical_and(icme_start_time_num[iwinind] > maxstart,icme_start_time_num[iwinind] < maxend))

ivexind_min=np.where(np.logical_and(icme_start_time_num[ivexind] > minstart,icme_start_time_num[ivexind] < minend))
ivexind_rise=np.where(np.logical_and(icme_start_time_num[ivexind] > risestart,icme_start_time_num[ivexind] < riseend))
ivexind_max=np.where(np.logical_and(icme_start_time_num[ivexind] > maxstart,icme_start_time_num[ivexind] < maxend))

imesind_min=np.where(np.logical_and(icme_start_time_num[imesind] > minstart,icme_start_time_num[imesind] < minend))
imesind_rise=np.where(np.logical_and(icme_start_time_num[imesind] > risestart,icme_start_time_num[imesind] < riseend))
imesind_max=np.where(np.logical_and(icme_start_time_num[imesind] > maxstart,icme_start_time_num[imesind] < maxend))

imercind_min=np.where(np.logical_and(icme_start_time_num[imercind] > minstart,icme_start_time_num[imercind] < minend))
imercind_rise=np.where(np.logical_and(icme_start_time_num[imercind] > risestart,icme_start_time_num[imercind] < riseend))
imercind_max=np.where(np.logical_and(icme_start_time_num[imercind] > maxstart,icme_start_time_num[imercind] < maxend))

istaind_min=np.where(np.logical_and(icme_start_time_num[istaind] > minstart,icme_start_time_num[istaind] < minend))
istaind_rise=np.where(np.logical_and(icme_start_time_num[istaind] > risestart,icme_start_time_num[istaind] < riseend))
istaind_max=np.where(np.logical_and(icme_start_time_num[istaind] > maxstart,icme_start_time_num[istaind] < maxend))

istbind_min=np.where(np.logical_and(icme_start_time_num[istbind] > minstart,icme_start_time_num[istbind] < minend))
istbind_rise=np.where(np.logical_and(icme_start_time_num[istbind] > risestart,icme_start_time_num[istbind] < riseend))
istbind_max=np.where(np.logical_and(icme_start_time_num[istbind] > maxstart,icme_start_time_num[istbind] < maxend))

#use these indices like  mo_bmean[imercind][imercind_rise] to get all MO_BMEAN at Mercury in the rising phase





Rs_in_AU=7e5/149.5e6















###################################################################################

##################### (3) DURATION PLOT and linear fit  ############################




sns.set_context("talk")     
#sns.set_style("darkgrid")  
sns.set_style("ticks",{'grid.linestyle': '--'})

fig=plt.figure(1,figsize=(12,11	))
fsize=15
ax1 = plt.subplot2grid((2,1), (0, 0))


icme_durations=(mo_end_time_num-icme_start_time_num)*24 #hours

#make linear fits
durfit=np.polyfit(sc_heliodistance,icme_durations,1)
durfitmin=np.polyfit(sc_heliodistance[iallind_min],icme_durations[iallind_min],1)
durfitrise=np.polyfit(sc_heliodistance[iallind_rise],icme_durations[iallind_rise],1)
durfitmax=np.polyfit(sc_heliodistance[iallind_max],icme_durations[iallind_max],1)

#this is similar to D=durfit[0]*xfit+durfit[1]
durfitall=np.poly1d(durfit)
durfitmin=np.poly1d(durfitmin)
durfitrise=np.poly1d(durfitrise)
durfitmax=np.poly1d(durfitmax)

#for fit plotting
xfit=np.linspace(0,2,1000)
print('ICME duration linear function: D[hours]={:.2f}r[AU]+{:.2f}'.format(durfit[0],durfit[1]))



plt.plot(sc_heliodistance,icme_durations,'o',color='blue',markersize=5, alpha=0.3,label='D')
#plt.plot(sc_heliodistance[iallind_min],icme_durations[iallind_min],'o',color='dimgrey',markersize=3, alpha=0.4,label='D min')
#plt.plot(sc_heliodistance[iallind_rise],icme_durations[iallind_rise],'o',color='grey',markersize=3, alpha=0.7,label='D rise')
#plt.plot(sc_heliodistance[iallind_max],icme_durations[iallind_max],'o',color='black',markersize=3, alpha=0.8,label='D max')



#fit for all
plt.plot(xfit,durfitall(xfit),'-',color='blue', lw=2.5, alpha=0.9,label='fit')
plt.plot(xfit,durfitmin(xfit),'--',color='black', lw=2, alpha=0.9,label='min fit')
plt.plot(xfit,durfitrise(xfit),'-.',color='black', lw=2, alpha=0.9,label='rise fit')
plt.plot(xfit,durfitmax(xfit),'-',color='black', lw=2, alpha=0.9,label='max fit')



plt.annotate('overall: D[h]={:.2f} R[AU] + {:.2f}'.format(durfitall[0],durfitall[1]),xy=(0.1,120),fontsize=12)
plt.annotate('minimum: D[h]={:.2f} R[AU] + {:.2f}'.format(durfitmin[0],durfitmin[1]),xy=(0.1,100),fontsize=12)
plt.annotate('rising phase: D[h]={:.2f} R[AU] + {:.2f}'.format(durfitrise[0],durfitrise[1]),xy=(0.1,80),fontsize=12)
plt.annotate('maximum: D[h]={:.2f} R[AU] + {:.2f}'.format(durfitmax[0],durfitmax[1]),xy=(0.1,60),fontsize=12)


#planet limits
plt.axvspan(np.min(pos.mars[0]),np.max(pos.mars[0]), color='orangered', alpha=0.2)
plt.axvspan(np.min(pos.mercury[0]),np.max(pos.mercury[0]), color='darkgrey', alpha=0.2)
plt.axvspan(np.min(pos.venus[0]),np.max(pos.venus[0]), color='orange', alpha=0.2)
plt.axvspan(np.min(pos.earth[0]),np.max(pos.earth[0]), color='mediumseagreen', alpha=0.2)
plt.axvspan(Rs_in_AU*10,Rs_in_AU*36,color='magenta', alpha=0.2)

plt.annotate('Mars', xy=(1.5,150), ha='center',fontsize=fsize)
plt.annotate('SPP', xy=(0.1,150), ha='center',fontsize=fsize)
plt.annotate('Mercury', xy=(0.37,150), ha='center',fontsize=fsize)
plt.annotate('Venus', xy=(0.72,150), ha='center',fontsize=fsize)
plt.annotate('Earth', xy=(1,150), ha='center',fontsize=fsize)

ax1.set_xticks(np.arange(0,2,0.2))


plt.xlim(0,max(sc_heliodistance)+0.3)
plt.ylim(0,max(icme_durations)+30)


plt.legend(loc=1,fontsize=fsize-1)

plt.xlabel('Heliocentric distance R [AU]',fontsize=fsize)
plt.ylabel('ICME duration D [hours]',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 


#plt.grid()



ax2 = plt.subplot2grid((2,1), (1, 0))


markers=6
linew=0


plt.plot_date(icme_start_time_num[imercind],icme_durations[imercind],'o',color='darkgrey',markersize=markers,linestyle='-',linewidth=linew,label='Mercury')
plt.plot_date(icme_start_time_num[ivexind],icme_durations[ivexind],'o',color='orange',markersize=markers,linestyle='-',linewidth=linew, label='Venus')
plt.plot_date(icme_start_time_num[iwinind],icme_durations[iwinind],'o',color='mediumseagreen',markersize=markers, linestyle='-', linewidth=linew, label='Earth')
plt.plot_date(icme_start_time_num[imavind],icme_durations[imavind],'o',color='steelblue',markersize=markers,linestyle='-',linewidth=linew, label='Mars')


#exclude STEREO for better visibility
#plt.plot_date(icme_start_time_num[istbind],np.log10(mo_bmean[istbind]),'o',color='royalblue',markersize=markers,linestyle='-',linewidth=linew)
#plt.plot_date(icme_start_time_num[istaind],np.log10(mo_bmean[istaind]),'o',color='red',markersize=markers,linestyle='-',linewidth=linew)



#Wind

tfit=mdates.date2num(sunpy.time.parse_time('2009-04-01'))+np.arange(0,365*10)
t0=mdates.date2num(sunpy.time.parse_time('2009-01-01'))

#is a gaussian better?
#sigma=1000
#bfitmax=30
#mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))
#ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
#plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='mediumseagreen',linestyle='-',markersize=0, label='Earth fit')


#or is this better, like sunspot cycle?
#Hathaway 2015 equation 6 page 40
#average cycle sunspot number 
A=100 #amplitude ##195 for sunspot
b=100*12 #56*12 for months to days
c=0.8

#4 free parameters A, b, c, t0

Fwind=A*(((tfit-t0)/b)**3) * 1/(np.exp((((tfit-t0)/b)**2))-c)
plt.plot_date(tfit, Fwind,'o',color='mediumseagreen',linestyle='-',markersize=0, label='Earth fit')


#same for Bfield plot



#xaxis: 10 years, daily data point
xfit=mdates.date2num(sunpy.time.parse_time('2007-01-01'))+np.arange(0,365*10)
#MESSENGER
sigma=1000
bfitmax=10
mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))

ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='darkgrey',linestyle='-',markersize=0, label='Mercury fit')


#VEX
#inital guess
sigma=1000
bfitmax=20
mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))
ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='orange',linestyle='-',markersize=0, label='Venus fit')





#for Mars: reconstruct likely parameters if sigma is quite similar for all fits, take mean of those sigmas and adjust bfitmax as function of distance with power law)
#plot reconstructed function for Mars
bfitmax=40
#plt.plot_date(xfit, Fwind,'o',color='steelblue',linestyle='--',markersize=0, label='Mars reconstr.')












plt.legend(loc=1,fontsize=fsize-1)

#limits solar min/rise/max

vlevel=120

plt.axvspan(minstart,minend, color='green', alpha=0.1)
plt.annotate('solar minimum',xy=(minstart+(minend-minstart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(minstart+10,vlevel),ha='left')
plt.annotate('>',xy=(minend-10,vlevel),ha='right')


plt.axvspan(risestart,riseend, color='yellow', alpha=0.1)
plt.annotate('rising phase',xy=(risestart+(riseend-risestart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(risestart+10,vlevel),ha='left')
plt.annotate('>',xy=(riseend-10,vlevel),ha='right')

plt.axvspan(maxstart,maxend, color='red', alpha=0.1)
plt.annotate('solar maximum',xy=(maxstart+(maxend-maxstart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(maxstart+10,vlevel),ha='left')
plt.annotate('>',xy=(maxend,vlevel),ha='right')



plt.ylim(0,max(icme_durations)+10)
plt.xlim(mdates.date2num(sunpy.time.parse_time('2007-01-01')), mdates.date2num(sunpy.time.parse_time('2016-12-31')))

plt.ylabel('ICME duration D [hours]',fontsize=fsize)
plt.xlabel('year',fontsize=fsize)

plt.tight_layout()

plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 



#panel labels
plt.figtext(0.03,0.98,'a',color='black', fontsize=fsize, ha='left',fontweight='bold')
plt.figtext(0.03,0.485,'b',color='black', fontsize=fsize, ha='left',fontweight='bold')

plt.show()
plt.savefig('plots/icme_durations_distance_time.pdf', dpi=300)
plt.savefig('plots/icme_durations_distance_time.png', dpi=300)



#results on durations

























###################################################################################

##################### (2) Bfield plot ICMECAT  ############################



#-------------------------------------------------------------- Bfield plot


sns.set_context("talk")     
#sns.set_style("darkgrid")  
sns.set_style("ticks",{'grid.linestyle': '--'})

fig=plt.figure(2,figsize=(12,12	))
#fig=plt.figure(2,figsize=(12,6	))
fsize=15

ax1 = plt.subplot2grid((2,2), (0, 0))
#ax1 = plt.subplot2grid((1,2), (0, 0))


xfit=np.linspace(0,2,1000)

#power law fits
bmaxfit=np.polyfit(np.log10(sc_heliodistance),np.log10(mo_bmax),1)
b=10**bmaxfit[1]
bmaxfitfun=b*(xfit**bmaxfit[0])
print('exponent for bmax fit:', bmaxfit[0])

bmeanfit=np.polyfit(np.log10(sc_heliodistance),np.log10(mo_bmean),1)
b=10**bmeanfit[1]
bmeanfitfun=b*(xfit**bmeanfit[0])
print('exponent for bmean fit:', bmeanfit[0])

plt.plot(sc_heliodistance,mo_bmean,'o',color='black',markersize=5, alpha=0.7,label='$\mathregular{<B>}$')
plt.plot(xfit,bmeanfitfun,'-',color='black', lw=2, alpha=0.7,label='$\mathregular{<B> \\ fit}$')

plt.plot(sc_heliodistance,mo_bmax,'o',color='dodgerblue',markersize=5, alpha=0.7,label='$\mathregular{B_{max}}$')
plt.plot(xfit,bmaxfitfun,'-',color='dodgerblue', lw=2, alpha=0.7,label='$\mathregular{B_{max} \\ fit}$')


#mars limits
plt.axvspan(np.min(pos.mars[0]),np.max(pos.mars[0]), color='orangered', alpha=0.2)
#plt.figtext(0.8,0.8,'Mars',color='orangered')

plt.axvspan(np.min(pos.mercury[0]),np.max(pos.mercury[0]), color='darkgrey', alpha=0.2)
#plt.figtext(0.25,0.8,'Mercury',color='darkgrey')

plt.axvspan(np.min(pos.venus[0]),np.max(pos.venus[0]), color='orange', alpha=0.2)
#plt.figtext(0.42,0.8,'Venus',color='orange')

plt.axvspan(np.min(pos.earth[0]),np.max(pos.earth[0]), color='mediumseagreen', alpha=0.2)
#plt.figtext(0.6,0.8,'Earth',color='mediumseagreen')

#solar probe plus 10 to 36 Rs close approaches
Rs_in_AU=7e5/149.5e6
plt.axvspan(Rs_in_AU*10,Rs_in_AU*36,color='magenta', alpha=0.2)


#plt.figtext(0.65,0.2,' D[h]={:.2f} R[AU] + {:.2f}'.format(durfit[0],durfit[1]))
plt.xlim(0,1.8)
plt.ylim(0,max(mo_bmax)+20)



plt.legend(loc=1,fontsize=fsize)

plt.xlabel('Heliocentric distance R [AU]',fontsize=fsize)
plt.ylabel('Magnetic field in MO B [nT]',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 
#plt.grid()





######################## logarithmic plot with Sun


#for the bmean fit, append one value for the coronal field at 0.007 AU for 1.5 Rs with 1 Gauss or 10^5 nT
#or better
#patsourakos georgoulis 2016: 0.03 G for 10 Rs #10^5 nT is 1 Gauss
mo_bmean_sun=np.append(mo_bmean,10**5*0.03) 


sc_heliodistance_sun=np.append(sc_heliodistance,10*Rs_in_AU)

ax3 = plt.subplot2grid((2,2), (0, 1))

bmeanfit_sun=np.polyfit(np.log10(sc_heliodistance_sun),np.log10(mo_bmean_sun),1)
b=10**bmeanfit_sun[1]
bmeanfitfun_sun=b*(xfit**bmeanfit_sun[0])
print('exponent for bmean fit sun:', bmeanfit_sun[0])


plt.plot(sc_heliodistance_sun,np.log10(mo_bmean_sun),'o',color='black',markersize=5, alpha=0.7,label='$\mathregular{<B> + B(10 Rs) = 3000 nT}$')
plt.plot(xfit,np.log10(bmeanfitfun_sun),'-',color='black', lw=2, alpha=0.7,label='$\mathregular{<B> + B(10 Rs) = 3000 nT \\ fit}$')

plt.ylim(0,6)

ax3.annotate('Mars', xy=(1.5,4), ha='center',fontsize=fsize-2)
ax3.annotate('SPP', xy=(0.1,4), ha='center',fontsize=fsize-2)
ax3.annotate('Mercury', xy=(0.37,4), ha='center',fontsize=fsize-2)
ax3.annotate('Venus', xy=(0.72,4), ha='center',fontsize=fsize-2)
ax3.annotate('Earth', xy=(1,4), ha='center',fontsize=fsize-2)


plt.legend(loc=1,fontsize=fsize)

plt.xlabel('Heliocentric distance R [AU]',fontsize=fsize)
plt.ylabel('Magnetic field in MO log(B) [nT]',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 


#mars limits
plt.axvspan(np.min(pos.mars[0]),np.max(pos.mars[0]), color='orangered', alpha=0.2)
#plt.figtext(0.8,0.8,'Mars',color='orangered')
plt.axvspan(np.min(pos.mercury[0]),np.max(pos.mercury[0]), color='darkgrey', alpha=0.2)
#plt.figtext(0.25,0.8,'Mercury',color='darkgrey')
plt.axvspan(np.min(pos.venus[0]),np.max(pos.venus[0]), color='orange', alpha=0.2)
#plt.figtext(0.42,0.8,'Venus',color='orange')
plt.axvspan(np.min(pos.earth[0]),np.max(pos.earth[0]), color='mediumseagreen', alpha=0.2)
#plt.figtext(0.6,0.8,'Earth',color='mediumseagreen')
plt.xlim(0,1.8)

#solar probe plus 10 to 36 Rs close approaches

plt.axvspan(Rs_in_AU*10,Rs_in_AU*36,color='magenta', alpha=0.2)




#panel labels
plt.figtext(0.03,0.96,'a',color='black', fontsize=fsize, ha='left',fontweight='bold')
plt.figtext(0.515,0.96,'b',color='black', fontsize=fsize, ha='left',fontweight='bold')
plt.figtext(0.03,0.49,'c',color='black', fontsize=fsize, ha='left',fontweight='bold')



#sns.despine()
#plt.tight_layout()







################################# B vs. time


ax2 = plt.subplot2grid((2,2), (1, 0), colspan=2)

markers=6
linew=0


plt.plot_date(icme_start_time_num[imercind],mo_bmean[imercind],'o',color='darkgrey',markersize=markers,linestyle='-',linewidth=linew,label='Mercury')
plt.plot_date(icme_start_time_num[ivexind],mo_bmean[ivexind],'o',color='orange',markersize=markers,linestyle='-',linewidth=linew, label='Venus')
plt.plot_date(icme_start_time_num[iwinind],mo_bmean[iwinind],'o',color='mediumseagreen',markersize=markers, linestyle='-', linewidth=linew, label='Earth')
plt.plot_date(icme_start_time_num[imavind],mo_bmean[imavind],'o',color='steelblue',markersize=markers,linestyle='-',linewidth=linew, label='Mars')


#exclude STEREO for better visibility
#plt.plot_date(icme_start_time_num[istbind],np.log10(mo_bmean[istbind]),'o',color='royalblue',markersize=markers,linestyle='-',linewidth=linew)
#plt.plot_date(icme_start_time_num[istaind],np.log10(mo_bmean[istaind]),'o',color='red',markersize=markers,linestyle='-',linewidth=linew)





#add gaussian fits for MESSENGER, VEX, Wind (MAVEN too few data points)


##########just gaussian, no fit yet


#instead of gaussian, fit solar cycle functions in Hathaway 2015 solar cycle living reviews equation 6

#xaxis: 10 years, daily data point
xfit=mdates.date2num(sunpy.time.parse_time('2007-01-01'))+np.arange(0,365*10)

#MESSENGER
sigma=1000
bfitmax=80
mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))

ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='darkgrey',linestyle='-',markersize=0, label='Mercury fit')


#VEX
#inital guess
sigma=1000
bfitmax=40
mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))
ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='orange',linestyle='-',markersize=0, label='Venus fit')

#Wind
sigma=1000
bfitmax=10
mu=mdates.date2num(sunpy.time.parse_time('2013-01-01'))
ygauss=1/(sigma*np.sqrt(2*np.pi))*np.exp(-((xfit-mu)**2)/(2*sigma**2) )
#normalize with 1/max(ygauss)
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='mediumseagreen',linestyle='-',markersize=0, label='Earth fit')


#for Mars: reconstruct likely parameters if sigma is quite similar for all fits, take mean of those sigmas and adjust bfitmax as function of distance with power law)
#plot reconstructed function for Mars
bfitmax=6
plt.plot_date(xfit, ygauss*1/max(ygauss)*bfitmax,'o',color='steelblue',linestyle='--',markersize=0, label='Mars reconstr.')


plt.legend(loc=1,fontsize=fsize-2)

#limits solar min/rise/max

vlevel=150

plt.axvspan(minstart,minend, color='green', alpha=0.1)
plt.annotate('solar minimum',xy=(minstart+(minend-minstart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(minstart+10,vlevel),ha='left')
plt.annotate('>',xy=(minend-10,vlevel),ha='right')


plt.axvspan(risestart,riseend, color='yellow', alpha=0.1)
plt.annotate('rising phase',xy=(risestart+(riseend-risestart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(risestart+10,vlevel),ha='left')
plt.annotate('>',xy=(riseend-10,vlevel),ha='right')

plt.axvspan(maxstart,maxend, color='red', alpha=0.1)
plt.annotate('solar maximum',xy=(maxstart+(maxend-maxstart)/2,vlevel),color='black', ha='center')
plt.annotate('<',xy=(maxstart+10,vlevel),ha='left')
plt.annotate('>',xy=(maxend,vlevel),ha='right')




plt.ylabel('Magnetic field in MO [nT]', fontsize=fsize)

plt.xlabel('Year', fontsize=fsize)

#sets planet / spacecraft labels
xoff=0.15
yoff=0.8
fsize=14

#plt.figtext(xoff,yoff,'Earth L1',color='mediumseagreen', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*1,'VEX',color='orange', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*2,'MESSENGER',color='dimgrey', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*3,'STEREO-A',color='red', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*4,'STEREO-B',color='royalblue', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*5,'MAVEN',color='steelblue', fontsize=fsize, ha='left')


#plt.ylim(0,45)
#plt.xlim(yearly_start_times[0],yearly_end_times[9])

#plt.grid()
plt.tight_layout()

#plt.show()
plt.savefig('plots/icme_total_field_distance_time.pdf', dpi=300)
plt.savefig('plots/icme_total_field_distance_time.png', dpi=300)




















































###############################################################
##########time spent inside ICMEs, in %
##########################################################


icme_durations=(mo_end_time_num-icme_start_time_num)*24 #hours





sns.set_context("talk")     
#sns.set_style("darkgrid")  
sns.set_style("ticks",{'grid.linestyle': '--'})


yearly_start_times=[mdates.date2num(sunpy.time.parse_time('2007-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2008-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2009-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2010-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2011-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2012-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2013-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2014-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2015-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2016-01-01'))]
                  
yearly_end_times=[mdates.date2num(sunpy.time.parse_time('2007-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2008-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2009-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2010-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2011-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2012-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2013-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2014-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2015-12-31')),
                  mdates.date2num(sunpy.time.parse_time('2016-12-31'))]

yearly_mid_times=[mdates.date2num(sunpy.time.parse_time('2007-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2008-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2009-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2010-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2011-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2012-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2013-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2014-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2015-07-01')),
                  mdates.date2num(sunpy.time.parse_time('2016-07-01'))]



#***check further : for each year, calculate how much data is NaN for each spacecraft
#and use in calculation

#converted times are here:
[vex_time,wind_time,sta_time,stb_time,mav_time,mes_time]=pickle.load( open( "../catpy/DATACAT/insitu_times_mdates_maven_interp.p", "rb" ) )
sta= pickle.load( open( "../catpy/DATACAT/STA_2007to2015_SCEQ.p", "rb" ) )
stb= pickle.load( open( "../catpy/DATACAT/STB_2007to2014_SCEQ.p", "rb" ) )
wind=pickle.load( open( "../catpy/DATACAT/WIND_2007to2016_HEEQ.p", "rb" ) )

total_data_days_sta=np.zeros(np.size(yearly_mid_times))
total_data_days_sta.fill(np.nan)


total_data_days_stb=np.zeros(np.size(yearly_mid_times))
total_data_days_stb.fill(np.nan)


total_data_days_wind=np.zeros(np.size(yearly_mid_times))
total_data_days_wind.fill(np.nan)



#go through each year and search for data gaps, ok for solar wind missions 

for i in range(np.size(yearly_mid_times)):
 
  #Wind
  thisyear=np.where(np.logical_and((wind_time > yearly_start_times[i]),(wind_time < yearly_end_times[i])))
  nan=np.isnan(wind.btot[thisyear]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_wind[i]=365
  if np.size(nan) > 0: total_data_days_wind[i]=np.size(notnan)/np.size(nan)*365
  
  #STA
  thisyear=np.where(np.logical_and((sta_time > yearly_start_times[i]),(sta_time < yearly_end_times[i])))
  nan=np.isnan(sta.btot[thisyear]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_sta[i]=365
  if np.size(nan) > 0: total_data_days_sta[i]=np.size(notnan)/np.size(nan)*365

  #STB
  thisyear=np.where(np.logical_and((stb_time > yearly_start_times[i]),(stb_time < yearly_end_times[i])))
  nan=np.isnan(stb.btot[thisyear]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_stb[i]=365
  if np.size(nan) > 0: total_data_days_stb[i]=np.size(notnan)/np.size(nan)*365

#for MESSENGER; VEX, MAVEN this is not correct because the nans during orbits are counted; 
#thats why we search manually for longer data gaps, and manually set the total_data_days_vex for each year




##################longer data gaps for MESSENGER and Mercury
total_data_days_mes=np.zeros(np.size(yearly_mid_times))
total_data_days_mes.fill(np.nan)

total_data_days_merc=np.zeros(np.size(yearly_mid_times))
total_data_days_merc.fill(np.nan)
#total_data_days_mes.fill(365)

#2007

jump1beg=mdates.date2num(sunpy.time.parse_time('2007-Jan-1'))
jump1end=mdates.date2num(sunpy.time.parse_time('2007-Mar-31'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2007-Jul-1'))
jump2end=mdates.date2num(sunpy.time.parse_time('2007-Jul-21'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2007-Aug-25'))
jump3end=mdates.date2num(sunpy.time.parse_time('2007-Dec-21'))

total_data_days_mes[0]=yearly_end_times[0]-yearly_start_times[0]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)

#2008
jump1beg=mdates.date2num(sunpy.time.parse_time('2008-Feb-24'))
jump1end=mdates.date2num(sunpy.time.parse_time('2008-Dec-31'))
#data gap too long - set nan
total_data_days_mes[1]=np.nan


#2009
jump1beg=mdates.date2num(sunpy.time.parse_time('2009-Jan-01'))
jump1end=mdates.date2num(sunpy.time.parse_time('2009-Jan-12'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2009-Jul-08'))
jump2end=mdates.date2num(sunpy.time.parse_time('2009-Jul-22'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2009-Aug-18'))
jump3end=mdates.date2num(sunpy.time.parse_time('2009-Aug-24'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2009-Sep-01'))
jump4end=mdates.date2num(sunpy.time.parse_time('2009-Sep-04'))

jump5beg=mdates.date2num(sunpy.time.parse_time('2009-Sep-30'))
jump5end=mdates.date2num(sunpy.time.parse_time('2009-Oct-02'))

jump6beg=mdates.date2num(sunpy.time.parse_time('2009-Oct-13'))
jump6end=mdates.date2num(sunpy.time.parse_time('2009-Dec-10'))

total_data_days_mes[2]=yearly_end_times[2]-yearly_start_times[2]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)-(jump4end-jump4beg)-(jump5end-jump5beg)-(jump6end-jump6beg)

#2010
total_data_days_mes[3]=yearly_end_times[3]-yearly_start_times[3]

#2011
jump1beg=mdates.date2num(sunpy.time.parse_time('2011-Mar-16'))
jump1end=mdates.date2num(sunpy.time.parse_time('2011-Mar-24'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2011-Jan-01'))
jump2end=mdates.date2num(sunpy.time.parse_time('2011-Mar-24'))

total_data_days_merc[4]=yearly_end_times[4]-yearly_start_times[4]-(jump2end-jump2beg)
total_data_days_mes[4]=yearly_end_times[4]-yearly_start_times[4]-(jump1end-jump1beg)


#2012
jump1beg=mdates.date2num(sunpy.time.parse_time('2012-Jun-06'))
jump1end=mdates.date2num(sunpy.time.parse_time('2012-Jun-13'))

total_data_days_merc[5]=yearly_end_times[5]-yearly_start_times[5]-(jump1end-jump1beg)
total_data_days_mes[5]=yearly_end_times[5]-yearly_start_times[5]-(jump1end-jump1beg)

#2013
jump1beg=mdates.date2num(sunpy.time.parse_time('2013-Apr-01'))
jump1end=mdates.date2num(sunpy.time.parse_time('2013-May-01'))


total_data_days_merc[6]=yearly_end_times[6]-yearly_start_times[6]-(jump1end-jump1beg)
total_data_days_mes[6]=yearly_end_times[6]-yearly_start_times[6]-(jump1end-jump1beg)


#2014
jump1beg=mdates.date2num(sunpy.time.parse_time('2014-Feb-25'))
jump1end=mdates.date2num(sunpy.time.parse_time('2014-Mar-26'))

total_data_days_merc[7]=yearly_end_times[7]-yearly_start_times[7]-(jump1end-jump1beg)
total_data_days_mes[7]=yearly_end_times[7]-yearly_start_times[7]-(jump1end-jump1beg)

#2015
jump1beg=mdates.date2num(sunpy.time.parse_time('2015-Apr-30'))
jump1end=mdates.date2num(sunpy.time.parse_time('2015-Dec-31'))

total_data_days_merc[8]=yearly_end_times[8]-yearly_start_times[8]-(jump1end-jump1beg)

total_data_days_mes[8]=yearly_end_times[8]-yearly_start_times[8]-(jump1end-jump1beg)





############################ MAVEN

startdata=mdates.date2num(sunpy.time.parse_time('2014-Nov-27'))

#2015
jump1beg=mdates.date2num(sunpy.time.parse_time('2015-Mar-8'))
jump1end=mdates.date2num(sunpy.time.parse_time('2015-Jun-17'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2015-Oct-3'))
jump2end=mdates.date2num(sunpy.time.parse_time('2015-Dec-18'))

#2016
jump3beg=mdates.date2num(sunpy.time.parse_time('2016-Mar-27'))
jump3end=mdates.date2num(sunpy.time.parse_time('2016-Jun-3'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2016-Sep-30'))
jump4end=mdates.date2num(sunpy.time.parse_time('2016-Dec-6'))

enddata=mdates.date2num(sunpy.time.parse_time('2016-Dec-31'))

total_data_days_mav=np.zeros(np.size(yearly_mid_times))
total_data_days_mav.fill(np.nan)

#this is 2014 - too few data points MAVEN (only 1 month)
#total_data_days_mav[7]=yearly_end_times[7]-startdata
total_data_days_mav[7]=np.nan


#this is 2015
total_data_days_mav[8]=yearly_end_times[8]-yearly_start_times[8]-(jump1end-jump1beg)-(jump2end-jump2beg)


#this is 2016
total_data_days_mav[9]=yearly_end_times[9]-yearly_start_times[9]-(jump3end-jump3beg)-(jump4end-jump4beg)






#################VEX 
total_data_days_vex=np.zeros(np.size(yearly_mid_times))
total_data_days_vex.fill(np.nan)


#times of longer data gaps

#2007
#from Jan 1 - Apr 1 there is not data gap

jump1beg=mdates.date2num(sunpy.time.parse_time('2007-Jul-5'))
jump1end=mdates.date2num(sunpy.time.parse_time('2007-Jul-12'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2007-Aug-23'))
jump2end=mdates.date2num(sunpy.time.parse_time('2007-Aug-28'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2007-Sep-18'))
jump3end=mdates.date2num(sunpy.time.parse_time('2007-Sep-20'))

total_data_days_vex[0]=yearly_end_times[0]-yearly_start_times[0]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)


#2008
jump1beg=mdates.date2num(sunpy.time.parse_time('2008-May-28'))
jump1end=mdates.date2num(sunpy.time.parse_time('2008-Jun-21'))

total_data_days_vex[1]=yearly_end_times[1]-yearly_start_times[1]-(jump1end-jump1beg)

#2009
jump1beg=mdates.date2num(sunpy.time.parse_time('2009-Apr-17'))
jump1end=mdates.date2num(sunpy.time.parse_time('2009-Apr-28'))
jump2beg=mdates.date2num(sunpy.time.parse_time('2009-Dec-28'))
jump2end=mdates.date2num(sunpy.time.parse_time('2009-Dec-31'))

total_data_days_vex[2]=yearly_end_times[2]-yearly_start_times[2]-(jump1end-jump1beg)-(jump2end-jump2beg)



#2010
jump1beg=mdates.date2num(sunpy.time.parse_time('2010-Jan-01'))
jump1end=mdates.date2num(sunpy.time.parse_time('2010-Jan-23'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2010-Apr-12'))
jump2end=mdates.date2num(sunpy.time.parse_time('2010-Apr-17'))

total_data_days_vex[3]=yearly_end_times[3]-yearly_start_times[3]-(jump1end-jump1beg)-(jump2end-jump2beg)


#2011
jump1beg=mdates.date2num(sunpy.time.parse_time('2011-Jan-24'))
jump1end=mdates.date2num(sunpy.time.parse_time('2011-Jan-27'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2011-Aug-05'))
jump2end=mdates.date2num(sunpy.time.parse_time('2011-Sep-01'))
total_data_days_vex[4]=yearly_end_times[4]-yearly_start_times[4]-(jump1end-jump1beg)-(jump2end-jump2beg)


#2012
jump1beg=mdates.date2num(sunpy.time.parse_time('2012-Mar-10'))
jump1end=mdates.date2num(sunpy.time.parse_time('2012-Mar-12'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2012-Jun-04'))
jump2end=mdates.date2num(sunpy.time.parse_time('2012-Jun-07'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2012-Jul-13'))
jump3end=mdates.date2num(sunpy.time.parse_time('2012-Jul-15'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2012-Dec-29'))
jump4end=mdates.date2num(sunpy.time.parse_time('2012-Dec-31'))

total_data_days_vex[5]=yearly_end_times[5]-yearly_start_times[5]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg) -(jump4end-jump4beg)


#2013
jump1beg=mdates.date2num(sunpy.time.parse_time('2013-Mar-17'))
jump1end=mdates.date2num(sunpy.time.parse_time('2013-Apr-14'))
total_data_days_vex[6]=yearly_end_times[6]-yearly_start_times[6]-(jump1end-jump1beg)


#2014
jump1beg=mdates.date2num(sunpy.time.parse_time('2014-Feb-25'))
jump1end=mdates.date2num(sunpy.time.parse_time('2014-Mar-26'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2014-May-16'))
jump2end=mdates.date2num(sunpy.time.parse_time('2014-May-21'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2014-Jul-12'))
jump3end=mdates.date2num(sunpy.time.parse_time('2014-Jul-21'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2014-Oct-13'))
jump4end=mdates.date2num(sunpy.time.parse_time('2014-Nov-11'))

jump5beg=mdates.date2num(sunpy.time.parse_time('2014-Nov-26'))
jump5end=mdates.date2num(sunpy.time.parse_time('2014-Dec-31'))

total_data_days_vex[7]=yearly_end_times[7]-yearly_start_times[7]-(jump1end-jump1beg)-(jump2end-jump2beg) -(jump3end-jump3beg) -(jump4end-jump4beg) -(jump5end-jump5beg)




#drop ulysses because too short, so 6 spacecraft

#make array with inside percentage

inside_wind_perc=np.zeros(np.size(yearly_mid_times))
inside_wind_perc.fill(np.nan)

inside_sta_perc=np.zeros(np.size(yearly_mid_times))
inside_sta_perc.fill(np.nan)

inside_stb_perc=np.zeros(np.size(yearly_mid_times))
inside_stb_perc.fill(np.nan)

inside_mes_perc=np.zeros(np.size(yearly_mid_times))
inside_mes_perc.fill(np.nan)

inside_merc_perc=np.zeros(np.size(yearly_mid_times))
inside_merc_perc.fill(np.nan)

inside_vex_perc=np.zeros(np.size(yearly_mid_times))
inside_vex_perc.fill(np.nan)

inside_mav_perc=np.zeros(np.size(yearly_mid_times))
inside_mav_perc.fill(np.nan)


#go through each year 
for i in range(np.size(yearly_mid_times)):
  
  #Wind:
  
  #select those icmes that are inside the current year
  thisyear=np.where(np.logical_and((icme_start_time_num[iwinind] > yearly_start_times[i]),(icme_start_time_num[iwinind] < yearly_end_times[i])))
  #summarize durations per year and convert to days
  total_icme_days=np.sum(icme_durations[thisyear])/24
  #get percentage
  if total_icme_days > 0:   inside_wind_perc[i]=total_icme_days/total_data_days_wind[i]*100

  thisyear=np.where(np.logical_and((icme_start_time_num[istaind] > yearly_start_times[i]),(icme_start_time_num[istaind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_sta_perc[i]=total_icme_days/total_data_days_sta[i]*100
  
  thisyear=np.where(np.logical_and((icme_start_time_num[istbind] > yearly_start_times[i]),(icme_start_time_num[istbind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_stb_perc[i]=total_icme_days/total_data_days_stb[i]*100

  thisyear=np.where(np.logical_and((icme_start_time_num[imesind] > yearly_start_times[i]),(icme_start_time_num[imesind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_mes_perc[i]=total_icme_days/total_data_days_mes[i]*100
  
  thisyear=np.where(np.logical_and((icme_start_time_num[imercind] > yearly_start_times[i]),(icme_start_time_num[imercind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_merc_perc[i]=total_icme_days/total_data_days_merc[i]*100

  
  thisyear=np.where(np.logical_and((icme_start_time_num[ivexind] > yearly_start_times[i]),(icme_start_time_num[ivexind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_vex_perc[i]=total_icme_days/total_data_days_vex[i]*100

  thisyear=np.where(np.logical_and((icme_start_time_num[imavind] > yearly_start_times[i]),(icme_start_time_num[imavind] < yearly_end_times[i])))
  total_icme_days=np.sum(icme_durations[thisyear])/24
  if total_icme_days > 0:   inside_mav_perc[i]=total_icme_days/total_data_days_mav[i]*100













#######*********************** check next section again; if min/rise/max shifts, manually adjust data gaps

#####################################################################################
############ make the same thing not yearly, but for the 3 solar cycle phases


cycle_start_times=[minstart, risestart, maxstart]
cycle_end_times=[minend, riseend, maxend]


total_data_days_sta_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_sta_cycle.fill(np.nan)

total_data_days_stb_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_stb_cycle.fill(np.nan)

total_data_days_wind_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_wind_cycle.fill(np.nan)


#define manually the data time ranges inside min, rise, max

#go through each year and search for data gaps, ok for solar wind missions 

for i in range(np.size(cycle_start_times)):
 
  #Wind
  phase=np.where(np.logical_and((wind_time > cycle_start_times[i]),(wind_time < cycle_end_times[i])))
  nan=np.isnan(wind.btot[phase]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_wind_cycle[i]=cycle_end_times[i]-cycle_start_times[i]
  if np.size(nan) > 0: total_data_days_wind_cycle[i]=np.size(notnan)/np.size(nan)*(cycle_end_times[i]-cycle_start_times[i])
  
  #STA
  phase=np.where(np.logical_and((sta_time > cycle_start_times[i]),(sta_time < cycle_end_times[i])))
  nan=np.isnan(sta.btot[phase]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_sta_cycle[i]=cycle_end_times[i]-cycle_start_times[i]
  if np.size(nan) > 0: total_data_days_sta_cycle[i]=np.size(notnan)/np.size(nan)*(cycle_end_times[i]-cycle_start_times[i])

  #STB
  phase=np.where(np.logical_and((stb_time > cycle_start_times[i]),(stb_time < cycle_end_times[i])))
  nan=np.isnan(stb.btot[phase]) 
  notnan=np.where(nan == False)
  if np.size(notnan) >0: total_data_days_stb_cycle[i]=cycle_end_times[i]-cycle_start_times[i]
  if np.size(nan) > 0: total_data_days_stb_cycle[i]=np.size(notnan)/np.size(nan)*(cycle_end_times[i]-cycle_start_times[i])

#for MESSENGER; VEX, MAVEN this is not correct because the nans during orbits are counted; 
#thats why we search manually for longer data gaps, and manually set the total_data_days_vex_cycle for each phase


##################longer data gaps for MESSENGER and Mercury
total_data_days_mes_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_mes_cycle.fill(np.nan)

total_data_days_merc_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_merc_cycle.fill(np.nan)
#total_data_days_mes.fill(365)

#min

jump1beg=mdates.date2num(sunpy.time.parse_time('2007-Jan-1'))
jump1end=mdates.date2num(sunpy.time.parse_time('2007-Mar-31'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2007-Jul-1'))
jump2end=mdates.date2num(sunpy.time.parse_time('2007-Jul-21'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2007-Aug-25'))
jump3end=mdates.date2num(sunpy.time.parse_time('2007-Dec-21'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2008-Feb-24'))
jump4end=mdates.date2num(sunpy.time.parse_time('2008-Dec-31'))

jump5beg=mdates.date2num(sunpy.time.parse_time('2009-Jan-01'))
jump5end=mdates.date2num(sunpy.time.parse_time('2009-Jan-12'))

jump6beg=mdates.date2num(sunpy.time.parse_time('2009-Jul-08'))
jump6end=mdates.date2num(sunpy.time.parse_time('2009-Jul-22'))

jump7beg=mdates.date2num(sunpy.time.parse_time('2009-Aug-18'))
jump7end=mdates.date2num(sunpy.time.parse_time('2009-Aug-24'))

jump8beg=mdates.date2num(sunpy.time.parse_time('2009-Sep-01'))
jump8end=mdates.date2num(sunpy.time.parse_time('2009-Sep-04'))

jump9beg=mdates.date2num(sunpy.time.parse_time('2009-Sep-30'))
jump9end=mdates.date2num(sunpy.time.parse_time('2009-Oct-02'))

jump10beg=mdates.date2num(sunpy.time.parse_time('2009-Oct-13'))
jump10end=mdates.date2num(sunpy.time.parse_time('2009-Dec-10'))

total_data_days_mes_cycle[0]=cycle_end_times[0]-cycle_start_times[0]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)-(jump4end-jump4beg)-(jump5end-jump5beg)-(jump6end-jump6beg)-(jump7end-jump7beg)-(jump8end-jump8beg)-(jump9end-jump9beg)-(jump10end-jump10beg)



#rise 2010 anfang bis mitte 2011

jump1beg=mdates.date2num(sunpy.time.parse_time('2011-Mar-16'))
jump1end=mdates.date2num(sunpy.time.parse_time('2011-Mar-24'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2011-Jan-01'))
jump2end=mdates.date2num(sunpy.time.parse_time('2011-Mar-24'))

total_data_days_mes_cycle[1]=cycle_end_times[1]-cycle_start_times[1]-(jump1end-jump1beg)-(jump2end-jump2beg)
##*******correct?
total_data_days_merc_cycle[1]=cycle_end_times[1]-mdates.date2num(sunpy.time.parse_time('2011-Mar-24'))

#max 
#2011 mitte bis ende 2015
jump1beg=mdates.date2num(sunpy.time.parse_time('2012-Jun-06'))
jump1end=mdates.date2num(sunpy.time.parse_time('2012-Jun-13'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2013-Apr-01'))
jump2end=mdates.date2num(sunpy.time.parse_time('2013-May-01'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2014-Feb-25'))
jump3end=mdates.date2num(sunpy.time.parse_time('2014-Mar-26'))

total_data_days_mes_cycle[2]=cycle_end_times[2]-cycle_start_times[2]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)
total_data_days_merc_cycle[2]=cycle_end_times[2]-cycle_start_times[2]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)



############################ MAVEN

total_data_days_mav_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_mav_cycle.fill(np.nan)

#only declining phase

jump1beg=mdates.date2num(sunpy.time.parse_time('2015-Mar-8'))
jump1end=mdates.date2num(sunpy.time.parse_time('2015-Jun-17'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2015-Oct-3'))
jump2end=mdates.date2num(sunpy.time.parse_time('2015-Dec-18'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2016-Mar-27'))
jump3end=mdates.date2num(sunpy.time.parse_time('2016-Jun-3'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2016-Sep-30'))
jump4end=mdates.date2num(sunpy.time.parse_time('2016-Dec-6'))

startdata=mdates.date2num(sunpy.time.parse_time('2014-Nov-27'))
enddata=mdates.date2num(sunpy.time.parse_time('2016-Dec-31'))

total_data_days_mav_cycle[1]=enddata-startdata-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)-(jump4end-jump4beg)


#################VEX 
total_data_days_vex_cycle=np.zeros(np.size(cycle_start_times))
total_data_days_vex_cycle.fill(np.nan)

#times of longer data gaps

#min
#2007 #from Jan 1 - Apr 1 there is not data gap

jump1beg=mdates.date2num(sunpy.time.parse_time('2007-Jul-5'))
jump1end=mdates.date2num(sunpy.time.parse_time('2007-Jul-12'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2007-Aug-23'))
jump2end=mdates.date2num(sunpy.time.parse_time('2007-Aug-28'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2007-Sep-18'))
jump3end=mdates.date2num(sunpy.time.parse_time('2007-Sep-20'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2008-May-28'))
jump4end=mdates.date2num(sunpy.time.parse_time('2008-Jun-21'))

jump5beg=mdates.date2num(sunpy.time.parse_time('2009-Apr-17'))
jump5end=mdates.date2num(sunpy.time.parse_time('2009-Apr-28'))

jump6beg=mdates.date2num(sunpy.time.parse_time('2009-Dec-28'))
jump6end=mdates.date2num(sunpy.time.parse_time('2009-Dec-31'))

total_data_days_vex_cycle[0]=cycle_end_times[0]-cycle_start_times[0]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)-(jump4end-jump4beg)-(jump5end-jump5beg)-(jump6end-jump6beg)

#rise
#2010 bis mitte 2011
jump1beg=mdates.date2num(sunpy.time.parse_time('2010-Jan-01'))
jump1end=mdates.date2num(sunpy.time.parse_time('2010-Jan-23'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2010-Apr-12'))
jump2end=mdates.date2num(sunpy.time.parse_time('2010-Apr-17'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2011-Jan-24'))
jump3end=mdates.date2num(sunpy.time.parse_time('2011-Jan-27'))

total_data_days_vex_cycle[1]=cycle_end_times[1]-cycle_start_times[1]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)


#max 2011 mitte bis ende 2015 (end of mission VEX)
jump1beg=mdates.date2num(sunpy.time.parse_time('2011-Aug-05'))
jump1end=mdates.date2num(sunpy.time.parse_time('2011-Sep-01'))

jump2beg=mdates.date2num(sunpy.time.parse_time('2012-Mar-10'))
jump2end=mdates.date2num(sunpy.time.parse_time('2012-Mar-12'))

jump3beg=mdates.date2num(sunpy.time.parse_time('2012-Jun-04'))
jump3end=mdates.date2num(sunpy.time.parse_time('2012-Jun-07'))

jump4beg=mdates.date2num(sunpy.time.parse_time('2012-Jul-13'))
jump4end=mdates.date2num(sunpy.time.parse_time('2012-Jul-15'))

jump5beg=mdates.date2num(sunpy.time.parse_time('2012-Dec-29'))
jump5end=mdates.date2num(sunpy.time.parse_time('2012-Dec-31'))

jump6beg=mdates.date2num(sunpy.time.parse_time('2013-Mar-17'))
jump6end=mdates.date2num(sunpy.time.parse_time('2013-Apr-14'))

jump7beg=mdates.date2num(sunpy.time.parse_time('2014-Feb-25'))
jump7end=mdates.date2num(sunpy.time.parse_time('2014-Mar-26'))

jump8beg=mdates.date2num(sunpy.time.parse_time('2014-May-16'))
jump8end=mdates.date2num(sunpy.time.parse_time('2014-May-21'))

jump9beg=mdates.date2num(sunpy.time.parse_time('2014-Jul-12'))
jump9end=mdates.date2num(sunpy.time.parse_time('2014-Jul-21'))

jump10beg=mdates.date2num(sunpy.time.parse_time('2014-Oct-13'))
jump10end=mdates.date2num(sunpy.time.parse_time('2014-Nov-11'))

jump11beg=mdates.date2num(sunpy.time.parse_time('2014-Nov-26'))
jump11end=mdates.date2num(sunpy.time.parse_time('2014-Dec-31'))

total_data_days_vex_cycle[2]=cycle_end_times[2]-cycle_start_times[2]-(jump1end-jump1beg)-(jump2end-jump2beg)-(jump3end-jump3beg)-(jump4end-jump4beg)-(jump5end-jump5beg)-(jump6end-jump6beg)-(jump7end-jump7beg)-(jump8end-jump8beg)-(jump9end-jump9beg)-(jump10end-jump10beg)-(jump11end-jump11beg)









############################################


inside_wind_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_wind_perc_cycle.fill(np.nan)

inside_sta_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_sta_perc_cycle.fill(np.nan)

inside_stb_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_stb_perc_cycle.fill(np.nan)

inside_mes_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_mes_perc_cycle.fill(np.nan)

inside_merc_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_merc_perc_cycle.fill(np.nan)

inside_vex_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_vex_perc_cycle.fill(np.nan)

inside_mav_perc_cycle=np.zeros(np.size(cycle_start_times))
inside_mav_perc_cycle.fill(np.nan)

#maven only declining phase
inside_mav_perc_cycle[1]=(np.sum(icme_durations[imavind]))/24/total_data_days_mav_cycle[1]*100

#go through solar cycle phases min, rise, max for Wind, VEX, MES, STA, STB
for i in range(np.size(cycle_start_times)):
  
  #Wind:
  #select those icmes that are inside min, rise, max
  phase=np.where(np.logical_and((icme_start_time_num[iwinind] > cycle_start_times[i]),(icme_start_time_num[iwinind] < cycle_end_times[i])))
  #summarize durations per phase and convert to days
  total_icme_days=np.sum(icme_durations[phase])/24
  #get percentage
  if total_icme_days > 0:   inside_wind_perc_cycle[i]=total_icme_days/total_data_days_wind_cycle[i]*100

  phase=np.where(np.logical_and((icme_start_time_num[istaind] > cycle_start_times[i]),(icme_start_time_num[istaind] < cycle_end_times[i])))
  total_icme_days=np.sum(icme_durations[phase])/24
  if total_icme_days > 0:   inside_sta_perc_cycle[i]=total_icme_days/total_data_days_sta_cycle[i]*100
  
  phase=np.where(np.logical_and((icme_start_time_num[istbind] > cycle_start_times[i]),(icme_start_time_num[istbind] < cycle_end_times[i])))
  total_icme_days=np.sum(icme_durations[phase])/24
  if total_icme_days > 0:   inside_stb_perc_cycle[i]=total_icme_days/total_data_days_stb_cycle[i]*100

  phase=np.where(np.logical_and((icme_start_time_num[imesind] > cycle_start_times[i]),(icme_start_time_num[imesind] < cycle_end_times[i])))
  total_icme_days=np.sum(icme_durations[phase])/24
  if total_icme_days > 0:   inside_mes_perc_cycle[i]=total_icme_days/total_data_days_mes_cycle[i]*100
  
  phase=np.where(np.logical_and((icme_start_time_num[imercind] > cycle_start_times[i]),(icme_start_time_num[imercind] < cycle_end_times[i])))
  total_icme_days=np.sum(icme_durations[phase])/24
  if total_icme_days > 0:   inside_merc_perc_cycle[i]=total_icme_days/total_data_days_merc_cycle[i]*100
  
  phase=np.where(np.logical_and((icme_start_time_num[ivexind] > cycle_start_times[i]),(icme_start_time_num[ivexind] < cycle_end_times[i])))
  total_icme_days=np.sum(icme_durations[phase])/24
  if total_icme_days > 0:   inside_vex_perc_cycle[i]=total_icme_days/total_data_days_vex_cycle[i]*100

  #phase=np.where(np.logical_and((icme_start_time_num[imavind] > cycle_start_times[i]),(icme_start_time_num[imavind] < cycle_end_times[i])))
  #total_icme_days=np.sum(icme_durations[phase])/24
  #if total_icme_days > 0:   inside_mav_perc_cycle[i]=total_icme_days/total_data_days_mav_cycle[i]*100





















  
  

### fix that VEX MESSENGER impact frequency is less than 1 AU by multiplying with a factor of 1.5
#check exact values with frequency plot

#inside_vex_perc=inside_vex_perc*1.5
#inside_mes_perc=inside_mes_perc*1.5


fig=plt.figure(5,figsize=(10,10	))

ax1 = plt.subplot(211) 

plt.plot_date(yearly_mid_times,inside_wind_perc,'o',color='mediumseagreen',markersize=8, linestyle='-')
plt.plot_date(yearly_mid_times,inside_merc_perc,'o',color='darkgrey',markersize=8,linestyle='-')
plt.plot_date(yearly_mid_times,inside_vex_perc,'o',color='orange',markersize=8,linestyle='-')
plt.plot_date(yearly_mid_times,inside_stb_perc,'o',color='royalblue',markersize=8,linestyle='-')
plt.plot_date(yearly_mid_times,inside_sta_perc,'o',color='red',markersize=8,linestyle='-')
plt.plot_date(yearly_mid_times,inside_mav_perc,'o',color='steelblue',markersize=8,linestyle='-')

plt.ylabel('Time inside ICME [%]')

#plt.xlim(yearly_bin_edges[0],yearly_bin_edges[10])
ax1.xaxis_date()
myformat = mdates.DateFormatter('%Y')
ax1.xaxis.set_major_formatter(myformat)

#sets planet / spacecraft labels
xoff=0.15
yoff=0.85
fsize=14

plt.figtext(xoff,yoff-0.03*0,'Mercury',color='darkgrey', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*1,'Venus',color='orange', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*2,'Earth',color='mediumseagreen', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*3,'Mars',color='steelblue', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*4,'STEREO-A',color='red', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*5,'STEREO-B',color='royalblue', fontsize=fsize, ha='left')
#panel labels
plt.figtext(0.02,0.98,'a',color='black', fontsize=fsize, ha='left',fontweight='bold')
plt.figtext(0.02,0.48,'b',color='black', fontsize=fsize, ha='left',fontweight='bold')



#limits solar min/rise/max

vlevel=22
fsize=11

plt.axvspan(minstart,minend, color='green', alpha=0.1)
plt.annotate('solar minimum',xy=(minstart+(minend-minstart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(minstart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(minend-10,vlevel),ha='right', fontsize=fsize)


plt.axvspan(risestart,riseend, color='yellow', alpha=0.1)
plt.annotate('rising phase',xy=(risestart+(riseend-risestart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(risestart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(riseend-10,vlevel),ha='right', fontsize=fsize)

plt.axvspan(maxstart,maxend, color='red', alpha=0.1)
plt.annotate('solar maximum',xy=(maxstart+(maxend-maxstart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(maxstart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(maxend,vlevel),ha='right', fontsize=fsize)


plt.ylim((0,25))
fsize=15
plt.ylabel('Time inside ICME [%]')
plt.xlabel('Year',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 


plt.tight_layout()










#plt.ylim(0,45)
plt.xlim(yearly_start_times[0],yearly_end_times[9])

#sns.despine()




#### plot time inside vs. heliocentric distance

pos_wind_perc=np.zeros(np.size(yearly_mid_times))
pos_wind_perc.fill(np.nan)
pos_wind_perc_std=np.zeros(np.size(yearly_mid_times))
pos_wind_perc_std.fill(np.nan)

pos_sta_perc=np.zeros(np.size(yearly_mid_times))
pos_sta_perc.fill(np.nan)
pos_sta_perc_std=np.zeros(np.size(yearly_mid_times))
pos_sta_perc_std.fill(np.nan)

pos_stb_perc=np.zeros(np.size(yearly_mid_times))
pos_stb_perc.fill(np.nan)
pos_stb_perc_std=np.zeros(np.size(yearly_mid_times))
pos_stb_perc_std.fill(np.nan)

#pos_mes_perc=np.zeros(np.size(yearly_mid_times))
#pos_mes_perc.fill(np.nan)
#pos_mes_perc_std=np.zeros(np.size(yearly_mid_times))
#pos_mes_perc_std.fill(np.nan)


pos_merc_perc=np.zeros(np.size(yearly_mid_times))
pos_merc_perc.fill(np.nan)
pos_merc_perc_std=np.zeros(np.size(yearly_mid_times))
pos_merc_perc_std.fill(np.nan)

pos_vex_perc=np.zeros(np.size(yearly_mid_times))
pos_vex_perc.fill(np.nan)
pos_vex_perc_std=np.zeros(np.size(yearly_mid_times))
pos_vex_perc_std.fill(np.nan)

pos_mav_perc=np.zeros(np.size(yearly_mid_times))
pos_mav_perc.fill(np.nan)
pos_mav_perc_std=np.zeros(np.size(yearly_mid_times))
pos_mav_perc_std.fill(np.nan)


allpositions=np.zeros([np.size(yearly_mid_times), 6])
allinside=np.zeros([np.size(yearly_mid_times), 6])

#calculate average distance +/- std for each year
#go through each year 
for i in range(np.size(yearly_mid_times)):
  
  #select those positions that are inside the current year
  thisyear=np.where(np.logical_and((pos_time_num > yearly_start_times[i]),(pos_time_num < yearly_end_times[i])))
  
  #pos_mes_perc[i]=np.mean(pos.messenger[0][thisyear])
  #pos_mes_perc_std[i]=np.std(pos.messenger[0][thisyear])
  pos_merc_perc[i]=np.mean(pos.mercury[0][thisyear])
  pos_merc_perc_std[i]=np.std(pos.mercury[0][thisyear])
  

  pos_mav_perc[i]=np.mean(pos.mars[0][thisyear])
  pos_mav_perc_std[i]=np.std(pos.mars[0][thisyear])

  pos_vex_perc[i]=np.mean(pos.venus[0][thisyear])
  pos_vex_perc_std[i]=np.std(pos.venus[0][thisyear])

  pos_wind_perc[i]=np.mean(pos.earth_l1[0][thisyear])
  pos_wind_perc_std[i]=np.std(pos.earth_l1[0][thisyear])

  pos_sta_perc[i]=np.mean(pos.sta[0][thisyear])
  pos_sta_perc_std[i]=np.std(pos.sta[0][thisyear])

  pos_stb_perc[i]=np.mean(pos.stb[0][thisyear])
  pos_stb_perc_std[i]=np.std(pos.stb[0][thisyear])
  
  allpositions[i][:]=(pos_merc_perc[i], pos_mav_perc[i], pos_vex_perc[i],pos_wind_perc[i],pos_sta_perc[i],pos_stb_perc[i])
  allinside[i][:]=(inside_merc_perc[i], inside_mav_perc[i], inside_vex_perc[i],inside_wind_perc[i],inside_sta_perc[i],inside_stb_perc[i])
  
 
  



#***make alpha variable for each year?

ax3 = plt.subplot(212) 


#for every year linear fit **check if power law works better

#for fit plotting
xfit=np.linspace(0,2,1000)

#allpositions[i] and allinside[i] are the data for each year
#no fit for 2016 as only MAVEN data is available


for i in range(np.size(yearly_mid_times)-2):
 #make linear fits ignoring NaN
 notnan=np.where(np.isfinite(allinside[i]) > 0)
 durfit=np.polyfit(allpositions[i][notnan],allinside[i][notnan],1)
 #this is similar to D=durfit[0]*xfit+durfit[1]
 durfitfun=np.poly1d(durfit)
 print('year',i+2007)
 print('time inside linear fit: D[hours]={:.2f}r[AU]+{:.2f}'.format(durfit[0],durfit[1]))
 plt.plot(xfit,durfitfun(xfit),'-',color='black', lw=2, alpha=i/10+0.2)#,label='fit')
 
 plt.errorbar(pos_merc_perc[i], inside_merc_perc[i], xerr=pos_merc_perc_std[i],yerr=0,fmt='o',color='darkgrey',markersize=8,linestyle=' ',alpha=i/10+0.2)
 plt.errorbar(pos_mav_perc[i], inside_mav_perc[i],xerr=pos_mav_perc_std[i],fmt='o',color='steelblue',markersize=8,linestyle=' ',alpha=i/10+0.2)
 plt.errorbar(pos_sta_perc[i], inside_sta_perc[i],xerr=pos_sta_perc_std[i],fmt='o',color='red',markersize=8,linestyle=' ',alpha=i/10+0.2)
 plt.errorbar(pos_stb_perc[i], inside_stb_perc[i],xerr=pos_stb_perc_std[i],fmt='o',color='royalblue',markersize=8,linestyle=' ',alpha=i/10+0.2)
 plt.errorbar(pos_wind_perc[i], inside_wind_perc[i],xerr=pos_wind_perc_std[i],fmt='o',color='mediumseagreen',markersize=8, linestyle=' ',alpha=i/10+0.2)
 plt.errorbar(pos_vex_perc[i], inside_vex_perc[i],xerr=pos_vex_perc_std[i],fmt='o',color='orange',markersize=8,linestyle=' ',alpha=i/10+0.2)
 
 plt.annotate(str(i+2007), xy=(0.1,5+2.5*i), alpha=i/10+0.2)
 
 
 #reconstruct Mars time inside from linear fits but not for years 2015 /2016
 if i < 8: inside_mav_perc[i]=durfitfun(pos_mav_perc[i])


#mars limits
plt.axvspan(np.min(pos.mars[0]),np.max(pos.mars[0]), color='orangered', alpha=0.2)
#plt.figtext(0.8,0.8,'Mars',color='orangered')
plt.axvspan(np.min(pos.mercury[0]),np.max(pos.mercury[0]), color='darkgrey', alpha=0.2)
#plt.figtext(0.25,0.8,'Mercury',color='darkgrey')
plt.axvspan(np.min(pos.venus[0]),np.max(pos.venus[0]), color='orange', alpha=0.2)
#plt.figtext(0.42,0.8,'Venus',color='orange')
plt.axvspan(np.min(pos.earth[0]),np.max(pos.earth[0]), color='mediumseagreen', alpha=0.2)
#plt.figtext(0.6,0.8,'Earth',color='mediumseagreen')
plt.xlim(0,1.8)

#solar probe plus 10 to 36 Rs close approaches

#plt.axvspan(Rs_in_AU*10,Rs_in_AU*36,color='magenta', alpha=0.2)

plt.ylabel('Time inside ICME [%]')
plt.xlabel('Heliocentric distance [AU]')
ax3.set_xticks(np.arange(0,2,0.2))

#add reconstructed Mars time inside on previous plot
ax1.plot_date(yearly_mid_times,inside_mav_perc,'o',color='steelblue',markersize=8,linestyle='--')


plt.ylim((0,25))

plt.tight_layout()

plt.show()
plt.savefig('plots/inside.pdf', dpi=300)
plt.savefig('plots/inside.png', dpi=300)
































###################################################################################

##################### (1) arrival frequencies in ICMECAT  ##############


yearly_bin_edges=[mdates.date2num(sunpy.time.parse_time('2007-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2008-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2009-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2010-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2011-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2012-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2013-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2014-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2015-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2016-01-01')),
                  mdates.date2num(sunpy.time.parse_time('2017-01-01'))]

#bin width in days         
binweite=360/8


sns.set_context("talk")     
#sns.set_style("darkgrid")  
sns.set_style("ticks",{'grid.linestyle': '--'})

fig=plt.figure(4,figsize=(12,10	))


fsize=15

ax1 = plt.subplot(211) 

plt.plot_date(icme_start_time_num[iwinind],sc_heliodistance[iwinind],fmt='o',color='mediumseagreen',markersize=5)
plt.plot_date(icme_start_time_num[imesind],sc_heliodistance[imesind],fmt='o',color='darkgrey',markersize=5)
plt.plot_date(icme_start_time_num[ivexind],sc_heliodistance[ivexind],fmt='o',color='orange',markersize=5)
plt.plot_date(icme_start_time_num[istbind],sc_heliodistance[istbind],fmt='o',color='royalblue',markersize=5)
plt.plot_date(icme_start_time_num[istaind],sc_heliodistance[istaind],fmt='o',color='red',markersize=5)
plt.plot_date(icme_start_time_num[iulyind],sc_heliodistance[iulyind],fmt='o',color='brown',markersize=5)
plt.plot_date(icme_start_time_num[imavind],sc_heliodistance[imavind],fmt='o',color='steelblue',markersize=5)






fsize=15
plt.ylabel('Heliocentric distance R [AU]',fontsize=fsize)
plt.xlabel('Year',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 


plt.xlim(yearly_bin_edges[0],yearly_bin_edges[10])
ax1.xaxis_date()
myformat = mdates.DateFormatter('%Y')
ax1.xaxis.set_major_formatter(myformat)



##############

ax2 = plt.subplot(212) 

(histwin, bin_edgeswin) = np.histogram(icme_start_time_num[iwinind], yearly_bin_edges)
(histvex, bin_edgesvex) = np.histogram(icme_start_time_num[ivexind], yearly_bin_edges)
(histmes, bin_edgesmes) = np.histogram(icme_start_time_num[imesind], yearly_bin_edges)
(histstb, bin_edgesstb) = np.histogram(icme_start_time_num[istbind], yearly_bin_edges)
(histsta, bin_edgessta) = np.histogram(icme_start_time_num[istaind], yearly_bin_edges)
(histmav, bin_edgesmav) = np.histogram(icme_start_time_num[imavind], yearly_bin_edges)

#********
#recalculate number of ICMEs as events per month or day, including data gaps


cycle_bin_edges=[minstart, minend, riseend, maxend]

(histwincyc, bin_edgescyc) = np.histogram(icme_start_time_num[iwinind], cycle_bin_edges)
(histvexcyc, bin_edgescyc) = np.histogram(icme_start_time_num[ivexind], cycle_bin_edges)
(histmescyc, bin_edgescyc) = np.histogram(icme_start_time_num[imesind], cycle_bin_edges)
(histstbcyc, bin_edgescyc) = np.histogram(icme_start_time_num[istbind], cycle_bin_edges)
(histstacyc, bin_edgescyc) = np.histogram(icme_start_time_num[istaind], cycle_bin_edges)
(histmavcyc, bin_edgescyc) = np.histogram(icme_start_time_num[imavind], cycle_bin_edges)

#use total_data_days_vex etc. from previous plot 
histwincyc=histwincyc/total_data_days_wind_cycle*365
histvexcyc=histvexcyc/total_data_days_vex_cycle*365
histmescyc=histmescyc/total_data_days_mes_cycle*365
histstbcyc=histstbcyc/total_data_days_stb_cycle*365
histstacyc=histstacyc/total_data_days_sta_cycle*365
histmavcyc=histmavcyc/total_data_days_mav_cycle*365


#normalize each dataset for data gaps

histwin=histwin/total_data_days_wind*365
histvex=histvex/total_data_days_vex*365
histmes=histmes/total_data_days_mes*365
histsta=histsta/total_data_days_sta*365
histstb=histstb/total_data_days_stb*365
histmav=histmav/total_data_days_mav*365

binedges=bin_edgeswin
pickle.dump([binedges,histwin,histvex,histmes,histsta,histstb,histmav], open( "plots/icme_frequency.p", "wb" ), protocol=2 )
#[binedges,histwin,histvex,histmes,histsta,histstb,histmav]=pickle.load( open( "plots/stats/icme_frequency.p", "rb" ) )

#binweite=45
ax2.bar(bin_edgeswin[:-1]+30,histwin, width=binweite,color='mediumseagreen', alpha=0.5)
ax2.bar(bin_edgesvex[:-1]+30+binweite,histvex, width=binweite,color='orange', alpha=0.5)
ax2.bar(bin_edgesmes[:-1]+30+ binweite*2,histmes, width=binweite,color='darkgrey', alpha=0.5)
ax2.bar(bin_edgesstb[:-1]+30+binweite*3,histstb, width=binweite,color='royalblue', alpha=0.5)
ax2.bar(bin_edgessta[:-1]+30+binweite*4,histsta, width=binweite,color='red', alpha=0.5)
#ax2.bar(bin_edgessta[:-1]+30+binweite*5,histuly, width=binweite,color='brown', alpha=0.5)
ax2.bar(bin_edgesmav[:-1]+30+binweite*6,histmav, width=binweite,color='steelblue', alpha=0.5)

plt.xlim(yearly_bin_edges[0],yearly_bin_edges[10])
ax2.xaxis_date()
myformat = mdates.DateFormatter('%Y')
ax2.xaxis.set_major_formatter(myformat)
#sets planet / spacecraft labels
xoff=0.85
yoff=0.45
fsize=12
plt.figtext(xoff,yoff,'Earth L1',color='mediumseagreen', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*1,'VEX',color='orange', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*2,'MESSENGER',color='dimgrey', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*3,'STEREO-A',color='red', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*4,'STEREO-B',color='royalblue', fontsize=fsize, ha='left')
#plt.figtext(xoff,yoff-0.03*5,'Ulysses',color='brown', fontsize=fsize, ha='left')
plt.figtext(xoff,yoff-0.03*5,'MAVEN',color='steelblue', fontsize=fsize, ha='left')
#panel labels
plt.figtext(0.02,0.98,'a',color='black', fontsize=fsize, ha='left',fontweight='bold')
plt.figtext(0.02,0.48,'b',color='black', fontsize=fsize, ha='left',fontweight='bold')

plt.ylim(0,48)


#limits solar min/rise/max

vlevel=44
fsize=13

plt.axvspan(minstart,minend, color='green', alpha=0.1)
plt.annotate('solar minimum',xy=(minstart+(minend-minstart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(minstart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(minend-10,vlevel),ha='right', fontsize=fsize)


plt.axvspan(risestart,riseend, color='yellow', alpha=0.1)
plt.annotate('rising phase',xy=(risestart+(riseend-risestart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(risestart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(riseend-10,vlevel),ha='right', fontsize=fsize)

plt.axvspan(maxstart,maxend, color='red', alpha=0.1)
plt.annotate('solar maximum',xy=(maxstart+(maxend-maxstart)/2,vlevel),color='black', ha='center', fontsize=fsize)
plt.annotate('<',xy=(maxstart+10,vlevel),ha='left', fontsize=fsize)
plt.annotate('>',xy=(maxend,vlevel),ha='right', fontsize=fsize)


fsize=15
plt.ylabel('ICMEs per year',fontsize=fsize)
plt.xlabel('Year',fontsize=fsize)
plt.yticks(fontsize=fsize) 
plt.xticks(fontsize=fsize) 


plt.tight_layout()

#sns.despine()
plt.show()
plt.savefig('plots/frequency.pdf', dpi=300)
plt.savefig('plots/frequency.png', dpi=300)
























































###################################### ALL RESULTS


##########

#B 

print('--------------------------------------------------')
print('Magnetic field B MO_BMEAN')

print()
print('Mercury +/-')
print(round(np.mean(mo_bmean[imercind]),1))
print(round(np.std(mo_bmean[imercind]),1))
#print('min')
#np.mean(mo_bmean[imercind][imercind_min])
#np.std(mo_bmean[imercind][imercind_min])
print('rise')
print(round(np.mean(mo_bmean[imercind][imercind_rise]),1))
print(round(np.std(mo_bmean[imercind][imercind_rise]),1))
print('max')
print(round(np.mean(mo_bmean[imercind][imercind_max]),1))
print(round(np.std(mo_bmean[imercind][imercind_max]),1))


print()
print('Venus')
print(round(np.mean(mo_bmean[ivexind]),1))
print(round(np.std(mo_bmean[ivexind]),1))
print('min')
print(round(np.mean(mo_bmean[ivexind][ivexind_min]),1))
print(round(np.std(mo_bmean[ivexind][ivexind_min]),1))
print('rise')
print(round(np.mean(mo_bmean[ivexind][ivexind_rise]),1))
print(round(np.std(mo_bmean[ivexind][ivexind_rise]),1))
print('max')
print(round(np.mean(mo_bmean[ivexind][ivexind_max]),1))
print(round(np.std(mo_bmean[ivexind][ivexind_max]),1))

print()
print('Earth')
print(round(np.mean(mo_bmean[iwinind]),1))
print(round(np.std(mo_bmean[iwinind]),1))
print('min')
print(round(np.mean(mo_bmean[iwinind][iwinind_min]),1))
print(round(np.std(mo_bmean[iwinind][iwinind_min]),1))
print('rise')
print(round(np.mean(mo_bmean[iwinind][iwinind_rise]),1))
print(round(np.std(mo_bmean[iwinind][iwinind_rise]),1))
print('max')
print(round(np.mean(mo_bmean[iwinind][iwinind_max]),1))
print(round(np.std(mo_bmean[iwinind][iwinind_max]),1))

print()


#only declining phase
print('MAVEN')
print(round(np.mean(mo_bmean[imavind]),1))
print(round(np.std(mo_bmean[imavind]),1))


#################################################

#D


print()
print()
print('--------------------------------------------------')
print()
print()

print('DURATION ')

print()
print('Mercury +/-')
print(round(np.mean(icme_durations[imercind]),1))
print(round(np.std(icme_durations[imercind]),1))

#print('min')
#np.mean(icme_durations[imercind][imercind_min])
#np.std(icme_durations[imercind][imercind_min])
print('rise')
print(round(np.mean(icme_durations[imercind][imercind_rise]),1))
print(round(np.std(icme_durations[imercind][imercind_rise]),1))
print('max')
print(round(np.mean(icme_durations[imercind][imercind_max]),1))
print(round(np.std(icme_durations[imercind][imercind_max]),1))


print()
print('Venus')
print(round(np.mean(icme_durations[ivexind]),1))
print(round(np.std(icme_durations[ivexind]),1))
print('min')
print(round(np.mean(icme_durations[ivexind][ivexind_min]),1))
print(round(np.std(icme_durations[ivexind][ivexind_min]),1))
print('rise')
print(round(np.mean(icme_durations[ivexind][ivexind_rise]),1))
print(round(np.std(icme_durations[ivexind][ivexind_rise]),1))
print('max')
print(round(np.mean(icme_durations[ivexind][ivexind_max]),1))
print(round(np.std(icme_durations[ivexind][ivexind_max]),1))

print()
print('Earth')
print(round(np.mean(icme_durations[iwinind]),1))
print(round(np.std(icme_durations[iwinind]),1))
print('min')
print(round(np.mean(icme_durations[iwinind][iwinind_min]),1))
print(round(np.std(icme_durations[iwinind][iwinind_min]),1))
print('rise')
print(round(np.mean(icme_durations[iwinind][iwinind_rise]),1))
print(round(np.std(icme_durations[iwinind][iwinind_rise]),1))
print('max')
print(round(np.mean(icme_durations[iwinind][iwinind_max]),1))
print(round(np.std(icme_durations[iwinind][iwinind_max]),1))

print()


#only declining phase
print('MAVEN')
print(round(np.mean(icme_durations[imavind]),1))
print(round(np.std(icme_durations[imavind]),1))

###################################################
#F


#TI

print()
print()
print('--------------------------------------------------')
print()
print()

print('Time Inside')

print()
print('Mercury +/-')
print(round(np.nanmean(inside_merc_perc_cycle),1))
print(round(np.nanstd(inside_merc_perc_cycle),1))
#print('min')
#print(round(inside_merc_perc_cycle[0],1))
print('rise')
print(round(inside_merc_perc_cycle[1],1))
print('max')
print(round(inside_merc_perc_cycle[2],1))


print()
print('Venus +/-')
print(round(np.nanmean(inside_vex_perc_cycle),1))
print(round(np.nanstd(inside_vex_perc_cycle),1))
print('min')
print(round(inside_vex_perc_cycle[0],1))
print('rise')
print(round(inside_vex_perc_cycle[1],1))
print('max')
print(round(inside_vex_perc_cycle[2],1))


print()
print('Earth +/-')
print(round(np.nanmean(inside_wind_perc_cycle),1))
print(round(np.nanstd(inside_wind_perc_cycle),1))
print('min')
print(round(inside_wind_perc_cycle[0],1))
print('rise')
print(round(inside_wind_perc_cycle[1],1))
print('max')
print(round(inside_wind_perc_cycle[2],1))


#only declining phase
print('MAVEN')
print(round(inside_mav_perc_cycle[1],1))

histwincyc






###################### MAVEN

#from processing program
#all in days
totaldays=385 
total_icme_duration_maven=np.sum(icme_durations[imavind])/24

print()
print()
print()


print('MAVEN results from 385 days of data, Dec 2014-Feb 2016, with gaps where no solar wind is available')
print('MAVEN total days of observations with solar wind data:')
print(totaldays)
print('MAVEN total ICME durations:')
print(total_icme_duration_maven)
print('Mars is in percent of time inside ICMEs, for intervals in 2014-2016 (declining phase):')
print(total_icme_duration_maven/totaldays*100)
print('on average, Mars is hit by a CME every ... days')
print(totaldays/np.size(imavind))
print('The ICME average duration is, in hours')
print(np.mean(icme_durations[imavind]))












































