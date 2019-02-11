import cdms2
from acme_diags.driver import utils

test_data_path = '/global/project/projectdirs/acme/acme_diags/test_model_data_for_acme_diags/time-series/E3SM_v1/'
reference_data_path = '/global/project/projectdirs/acme/acme_diags/obs_for_e3sm_diags/time-series/ERA-Interim/'

file1 = test_data_path + 'TREFHT_185001_201312.nc'

file2 = reference_data_path + 'tas_197901_201612.nc' 

fin1 = cdms2.open('file1')

fin2 = cdms2.open('file2')

# select years, region and averaging
mv1 = fin1('TREFHT', time=("1979","2013"))
mv2 = fin2('tas', time=("1979","2013"))

mv1_area_mean = cdutil.averager(mv1, axis='xy')
mv2_area_mean = cdutil.averager(mv2, axis='xy')




# plot time series


