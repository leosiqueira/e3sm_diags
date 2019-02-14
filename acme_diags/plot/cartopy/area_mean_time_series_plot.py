import os
import copy
import cdms2
import cdutil
import acme_diags
from acme_diags.driver import utils
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from acme_diags.derivations.default_regions import regions_specs

def mask_by(input_var, maskvar, low_limit=None, high_limit=None):
    """masks a variable var to be missing except where maskvar>=low_limit and maskvar<=high_limit.
    None means to omit the constrint, i.e. low_limit = -infinity or high_limit = infinity.
    var is changed and returned; we don't make a new variable.
    var and maskvar: dimensioned the same variables.
    low_limit and high_limit: scalars.
    """
    var = copy.deepcopy(input_var)
    if low_limit is None and high_limit is None:
        return var
    if low_limit is None and high_limit is not None:
        maskvarmask = maskvar > high_limit
    elif low_limit is not None and high_limit is None:
        maskvarmask = maskvar < low_limit
    else:
        maskvarmask = (maskvar < low_limit) | (maskvar > high_limit)
    if var.mask is False:
        newmask = maskvarmask
    else:
        newmask = var.mask | maskvarmask
    var.mask = newmask
    return var

#def select_region(region, var1, var2, land_frac, ocean_frac, parameter):
def select_region(region, var1, var2, land_frac, ocean_frac, regrid_tool, regrid_method):
    """Select desired regions from transient variables."""
    domain = None
    # if region != 'global':
    if region.find('land') != -1 or region.find('ocean') != -1:
        land_ocean_frac = land_frac
        region_value = 0.65
        
        if region.find('land') != -1:
            var1_domain = mask_by(
                var1, land_ocean_frac, low_limit=region_value)
            var2_domain = var2.regrid(
                #var1.getGrid(), regridTool=parameter.regrid_tool, regridMethod=parameter.regrid_method)
                var1.getGrid(), regridTool=regrid_tool, regridMethod=regrid_method)
            var2_domain = mask_by(
                var2_domain, land_ocean_frac, low_limit=region_value)
        elif region.find('ocean') != -1:
            var1_domain = mask_by(
                var1, land_ocean_frac, high_limit=region_value)
            var2_domain = var2.regrid(
                #var1.getGrid(), regridTool=parameter.regrid_tool, regridMethod=parameter.regrid_method)
                var1.getGrid(), regridTool=regrid_tool, regridMethod=regrid_method)
            var2_domain = mask_by(
                var2_domain, land_ocean_frac, high_limit=region_value)
#        if region.find('land') != -1:
#            land_ocean_frac = land_frac
#        elif region.find('ocean') != -1:
#            land_ocean_frac = ocean_frac
#        region_value = regions_specs[region]['value']
#
#        var1_domain = mask_by(
#            var1, land_ocean_frac, low_limit=region_value)
#        var2_domain = var2.regrid(
#            #var1.getGrid(), regridTool=parameter.regrid_tool, regridMethod=parameter.regrid_method)
#            var1.getGrid(), regridTool=regrid_tool, regridMethod=regrid_method)
#        var2_domain = mask_by(
#            var2_domain, land_ocean_frac, low_limit=region_value)
    else:
        var1_domain = var1
        var2_domain = var2

    try:
        # if region.find('global') == -1:
        domain = regions_specs[region]['domain']
        print('Domain: ', domain)
    except:
        #print("No domain selector.")
        print("No domain selector for " + region)

    var1_domain_selected = var1_domain(domain)
    var2_domain_selected = var2_domain(domain)
    var1_domain_selected.units = var1.units
    var2_domain_selected.units = var1.units

    return var1_domain_selected, var2_domain_selected

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
mask_path = os.path.join(acme_diags.INSTALL_PATH, 'acme_ne30_ocean_land_mask.nc')
with cdms2.open(mask_path) as f:
    land_frac = f('LANDFRAC')
    ocean_frac = f('OCNFRAC')

regions = ['global']  
regrid_tool = 'esmf'
regrid_method = 'conservative'
regrid_method = 'linear'
mv1_region, mv2_region = select_region(regions[0], mv1, mv2, land_frac, ocean_frac, regrid_tool, regrid_method)



regions = ['global', 'land', 'ocean', '90S50S','50S20S','20S20N','20N50N','50N90N','global']
mv_all = np.empty((3,len(regions),num_years))
#select regions
for index, region in enumerate(regions):
    mv1_region, mv2_region = select_region(region, mv1, mv2, land_frac, ocean_frac, regrid_tool, regrid_method)
    mv1_region, mv3_region = select_region(region, mv1, mv3, land_frac, ocean_frac, regrid_tool, regrid_method)
    
    mv1_domain = cdutil.averager(mv1_region,axis = 'xy')
    mv2_domain = cdutil.averager(mv2_region,axis = 'xy')
    mv3_domain = cdutil.averager(mv3_region,axis = 'xy')

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
    ax1.plot(mv_all[0,i], 'k', linewidth=2,label='Model '+'{0:.1f}'.format(np.mean(mv_all[0,i])))
    ax1.plot(mv_all[1,i], 'r', linewidth=2,label='ERA-Interim ' + '{0:.1f}'.format(np.mean(mv_all[1,i])))
    ax1.plot(mv_all[2,i], 'b', linewidth=2,label='MERRA2 ' + '{0:.1f}'.format(np.mean(mv_all[2,i])))
#    ax1.plot(mv1_area_mean_year[:].asma(), 'k', linewidth=2,label='Model')
#    ax1.plot(mv2_area_mean_year[:].asma(), 'r', linewidth=2,label='ERA-Interim')
#    ax1.plot(mv3_area_mean_year[:].asma(), 'b', linewidth=2,label='MERRA2')
#    ax1.set_ylim(286,289)
    x = np.arange(mv1_area_mean_year[:].asma().size)
    ax1.set_xticks(x)
    x_ticks_labels = [str(x) for x in range(start_year,end_year+1)]
    ax1.set_xticklabels(x_ticks_labels, rotation='vertical', fontsize=8)
    
    if i % 3 == 0 :
        ax1.set_ylabel('Surface air temperature (K)')
    ax1.legend(loc=1, prop={'size': 6})
    fig.text(panel[i][0]+0.12, panel[i][1]+panel[i][3]-0.015, regions[i],ha='center', color='black')

plt.savefig('/global/project/projectdirs/acme/www/zhang40/figs/test_tas.png')

#plt.show()




#print mv1_area_mean.shape, mv1_area_mean.getTime().asComponentTime()
#print mv2_area_mean.shape, mv2_area_mean.getTime().asComponentTime()
