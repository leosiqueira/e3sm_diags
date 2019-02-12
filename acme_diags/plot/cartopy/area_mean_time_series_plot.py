import cdms2
import cdutil
from acme_diags.driver import utils
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

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
mv1 = fin1('TREFHT', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))
mv2 = fin2('tas', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))
mv3 = fin3('tas', time=(str(start_year)+"-01-01",str(end_year)+"-12-31"))
#mv1 = fin1('TREFHT', time=("1979-01-01","1980-12-31"))
#mv2 = fin2('tas', time=("1979-01-01","1980-12-31"))

cdutil.setTimeBoundsMonthly(mv1)
cdutil.setTimeBoundsMonthly(mv2)
cdutil.setTimeBoundsMonthly(mv3)

mv1_area_mean = cdutil.averager(mv1, axis='xy')
mv2_area_mean = cdutil.averager(mv2, axis='xy')
mv3_area_mean = cdutil.averager(mv3, axis='xy')

mv1_area_mean_year = cdutil.YEAR(mv1_area_mean)
mv2_area_mean_year = cdutil.YEAR(mv2_area_mean)
mv3_area_mean_year = cdutil.YEAR(mv3_area_mean)

print mv1_area_mean.shape, mv1_area_mean.getTime().asComponentTime()
print mv2_area_mean.shape, mv2_area_mean.getTime().asComponentTime()

#quit()

# plot time series
plotTitle = {'fontsize': 12.5}
plotSideTitle = {'fontsize': 11.5}

# Position and sizes of subplot axes in page coordinates (0 to 1)
panel = [(0.1500, 0.5500, 0.7500, 0.3000),
         (0.1500, 0.1300, 0.7500, 0.3000),
         ]

# Border padding relative to subplot axes for saving individual panels
# (left, bottom, right, top) in page coordinates
border = (-0.14, -0.06, 0.04, 0.08)



# Create figure
figsize = [8.5,11.0]
dpi = 150
fig = plt.figure(figsize=figsize, dpi=dpi)
#fig = plt.figure(figsize=parameter.figsize, dpi=parameter.dpi)

    # Top panel
ax1 = fig.add_axes(panel[0])
ax1.plot(mv1_area_mean_year[:].asma(), 'k', linewidth=2,label='Model')
ax1.plot(mv2_area_mean_year[:].asma(), 'r', linewidth=2,label='ERA-Interim')
ax1.plot(mv3_area_mean_year[:].asma(), 'b', linewidth=2,label='MERRA2')
ax1.set_ylim(286,289)
#ax1.set_xticks([-90, -60, -30, 0, 30, 60, 90])
x = np.arange(mv1_area_mean_year[:].asma().size)
ax1.set_xticks(x)
x_ticks_labels = [str(x) for x in range(start_year,end_year+1)]
print x_ticks_labels
ax1.set_xticklabels(x_ticks_labels, rotation='vertical', fontsize=10)

ax1.set_ylabel('Surface air temperature (K)')
ax1.legend()
fig.text(panel[0][0], panel[0][1]+panel[0][3]+0.03, 'Global mean',
ha='left', color='black')

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




