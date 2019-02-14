import cdms2
import cdutil
from acme_diags.driver import utils
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from acme_diags.derivations.default_regions import regions_specs

test_data_path = '/global/project/projectdirs/acme/acme_diags/test_model_data_for_acme_diags/time-series/E3SM_v1/'
reference_data_path = '/global/project/projectdirs/acme/acme_diags/obs_for_e3sm_diags/time-series/ERA-Interim/'
reference_data_path_2 = '/global/project/projectdirs/acme/acme_diags/obs_for_e3sm_diags/time-series/MERRA2/'

file1 = test_data_path + 'TREFHT_185001_201312.nc'

file2 = reference_data_path + 'tas_197901_201612.nc' 

file3 = reference_data_path_2 + 'tas_198001_201612.nc' 

fin1 = cdms2.open(file1)

fin2 = cdms2.open(file2)

fin3 = cdms2.open(file3)

# select years, region and averaging
start_year = 1980
end_year = 2013
#end_year = 1981
num_years = end_year - start_year + 1
mv1 = fin1('TREFHT', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))
mv2 = fin2('tas', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))
mv3 = fin3('tas', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))

cdutil.setTimeBoundsMonthly(mv1)
cdutil.setTimeBoundsMonthly(mv2)
cdutil.setTimeBoundsMonthly(mv3)

#mv1_area_mean = cdutil.averager(mv1, axis='xy')
#mv2_area_mean = cdutil.averager(mv2, axis='xy')
#mv3_area_mean = cdutil.averager(mv3, axis='xy')

#mv1_area_mean_year = cdutil.YEAR(mv1_area_mean)
#mv2_area_mean_year = cdutil.YEAR(mv2_area_mean)
#mv3_area_mean_year = cdutil.YEAR(mv3_area_mean)


regions = ['90S50S','90S50S','50S20S','20S20N','20N50N','50N90N','20S20N','20N50N','50N90N']
mv_all = np.empty((3,len(regions),num_years))
#select regions
for index, region in enumerate(regions):
    try:
        # if region.find('global') == -1:
        domain = regions_specs[region]['domain']
        print('Domain: ', domain)
        #print dir(domain)
    except:
        print("No domain selector.")
    
    mv1_domain = cdutil.averager(mv1(domain),axis = 'xy')
    mv2_domain = cdutil.averager(mv2(domain),axis = 'xy')
    mv3_domain = cdutil.averager(mv3(domain),axis = 'xy')
    mv1_area_mean_year = cdutil.YEAR(mv1_domain)
    mv2_area_mean_year = cdutil.YEAR(mv2_domain)
    mv3_area_mean_year = cdutil.YEAR(mv3_domain)
    
    mv_all[0,index,:] = mv1_area_mean_year
    mv_all[1,index,:] = mv2_area_mean_year
    mv_all[2,index,:] = mv3_area_mean_year



#quit()

# plot time series
plotTitle = {'fontsize': 8.5}
plotSideTitle = {'fontsize': 6.5}

# Position and sizes of subplot axes in page coordinates (0 to 1)
# The dimensions [left, bottom, width, height] of the new axes. All quantities are in fractions of figure width and height.

panel = [(0.1500, 0.5500, 0.7500, 0.3000),
         (0.1500, 0.1300, 0.7500, 0.3000),
         ]

panel = [(0.1, 0.68, 0.25, 0.25),
         (0.4, 0.68, 0.25, 0.25),
         (0.7, 0.68, 0.25, 0.25),
         (0.1, 0.38, 0.25, 0.25),
         (0.4, 0.38, 0.25, 0.25),
         (0.7, 0.38, 0.25, 0.25),
         (0.1, 0.08, 0.25, 0.25),
         (0.4, 0.08, 0.25, 0.25),
         (0.7, 0.08, 0.25, 0.25),
         ]
# Border padding relative to subplot axes for saving individual panels
# (left, bottom, right, top) in page coordinates
border = (-0.14, -0.06, 0.04, 0.08)



# Create figure
figsize = [11.0,8.5]
dpi = 150
fig = plt.figure(figsize=figsize, dpi=dpi)
#fig = plt.figure(figsize=parameter.figsize, dpi=parameter.dpi)

    # Top panel
for i in range(9):
    ax1 = fig.add_axes(panel[i])
    ax1.plot(mv_all[0,i], 'k', linewidth=2,label='Model')
    ax1.plot(mv_all[1,i], 'r', linewidth=2,label='ERA-Interim')
    ax1.plot(mv_all[2,i], 'b', linewidth=2,label='MERRA2')
#    ax1.plot(mv1_area_mean_year[:].asma(), 'k', linewidth=2,label='Model')
#    ax1.plot(mv2_area_mean_year[:].asma(), 'r', linewidth=2,label='ERA-Interim')
#    ax1.plot(mv3_area_mean_year[:].asma(), 'b', linewidth=2,label='MERRA2')
#    ax1.set_ylim(286,289)
    #ax1.set_xticks([-90, -60, -30, 0, 30, 60, 90])
    x = np.arange(mv1_area_mean_year[:].asma().size)
    ax1.set_xticks(x)
    x_ticks_labels = [str(x) for x in range(start_year,end_year+1)]
    ax1.set_xticklabels(x_ticks_labels, rotation='vertical', fontsize=8)
    
    if i % 3 == 0 :
        ax1.set_ylabel('Surface air temperature (K)')
    ax1.legend(loc=1, prop={'size': 6})
    fig.text(panel[i][0]+0.12, panel[i][1]+panel[i][3]-0.015, regions[i],ha='center', color='black')

##fig, ax = plt.subplots(1)
##fig.autofmt_xdate()
#fig = plt.figure()
#print mv1_area_mean.getTime()[:],mv1_area_mean[:]
##plt.plot(mv1_area_mean.getTime()[:], mv1_area_mean[:].asma(),mv2_area_mean.getTime()[:],mv2_area_mean[:].asma())
#plt.plot(mv1_area_mean_year[:].asma())
#plt.plot(mv2_area_mean_year[:].asma())
##import pdb
##pdb.set_trace()
##print mv1_area_mean.getValue()
##print mv1_area_mean[:]
##plt.plot( mv1_area_mean[:].asma())
##plt.plot(mv1_area_mean.getValue())
##plt.plot(mv1_area_mean.getTime()[:])
##plt.plot(times, range(times.size))
#
##xfmt = mdates.DateFormatter('%Y-%m-%d %H:%M')
##ax.xaxis.set_major_formatter(xfmt)
plt.savefig('/global/project/projectdirs/acme/www/zhang40/figs/test_tas.png')

#plt.show()




#print mv1_area_mean.shape, mv1_area_mean.getTime().asComponentTime()
#print mv2_area_mean.shape, mv2_area_mean.getTime().asComponentTime()
