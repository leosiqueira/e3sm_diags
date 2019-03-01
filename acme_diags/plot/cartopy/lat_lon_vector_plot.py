import cdms2
import cdutil
from acme_diags.driver import utils
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import numpy as np
from acme_diags.derivations.default_regions import regions_specs

import numpy.ma as ma
import cartopy.crs as ccrs
from cartopy.mpl.ticker import LongitudeFormatter, LatitudeFormatter
from acme_diags.driver.utils.general import get_output_dir
from acme_diags.plot import get_colormap

#test_data_path = '/p/cscratch/acme/data/test_model_data_for_acme_diags/climatology/'
#file1 = test_data_path + '20161118.beta0.FC5COSP.ne30_ne30.edison_ANN_climo.nc'
test_data_path = '/export/zhang40/test_data/'
file1 = test_data_path + '20170926.FCT2.A_WCYCL1850S.ne30_oECv3.anvil_ANN_000101_003012_climo.nc'
test_data_path = '/Users/zhang40/Documents/ACME_simulations/'
file1 = test_data_path + '20160520.A_WCYCL1850.ne30_oEC.edison.alpha6_01_ANN_climo.nc' 
#reference_data_path = '/p/cscratch/acme/data/obs_for_e3sm_diags/climatology/ERA-Interim/'
#file2 = reference_data_path + 'ERA-Interim_ANN_197901_201612_climo.nc' 

fin1 = cdms2.open(file1)

#fin2 = cdms2.open(file2)

x1 = fin1('TAUX')
y1 = fin1('TAUY')
print x1.shape
#y1 = fin1('TAUY')
#
#x2 = fin2('tauu')
#y2 = fin2('tauv')


#var = add_cyclic(var)
lon = x1.getLongitude()
lat = x1.getLatitude()
u = ma.squeeze(x1.asma())
v = ma.squeeze(y1.asma())

proj = ccrs.PlateCarree(central_longitude=180)

# Position and sizes of subplot axes in page coordinates (0 to 1)
panel = [(0.1691, 0.6810, 0.6465, 0.2258),
         (0.1691, 0.3961, 0.6465, 0.2258),
         (0.1691, 0.1112, 0.6465, 0.2258),
         ]


# Contour levels
levels = None
norm = None


#figsize = [8.5, 11.0]
figsize = [17, 22.0]
dpi = 150
fig = plt.figure(figsize=figsize, dpi=dpi)

# Contour plot
ax = fig.add_axes(panel[0], projection=proj)
ax.set_global()
#cmap = get_colormap(cmap, parameters)
p1 = ax.contourf(lon, lat, u,
                 transform=ccrs.PlateCarree(),
                 norm=norm,
                 levels=levels,
#                 cmap=cmap,
                 extend='both',
                 )

x  , y = np.meshgrid(lon,lat)
u = ma.squeeze(x1.asma())
v = ma.squeeze(y1.asma())
print x.shape
print y.shape
print u.shape
print v.shape
skip=(slice(None,None,None),slice(None,None,None))

#ax.quiver(x,y,u,v)
ax.quiver(x[skip],y[skip],u[skip],v[skip])#,color='black', headwidth=1, scale = 10, headlength=2)
ax.set_aspect('auto')
ax.coastlines(lw=0.3)
plt.savefig('test_vector.png')

quit()


plotTitle = {'fontsize': 11.5}
plotSideTitle = {'fontsize': 9.5}

# Position and sizes of subplot axes in page coordinates (0 to 1)
panel = [(0.1691, 0.6810, 0.6465, 0.2258),
         (0.1691, 0.3961, 0.6465, 0.2258),
         (0.1691, 0.1112, 0.6465, 0.2258),
         ]

# Border padding relative to subplot axes for saving individual panels
# (left, bottom, right, top) in page coordinates
border = (-0.06, -0.03, 0.13, 0.03)


def add_cyclic(var):
    lon = var.getLongitude()
    return var(longitude=(lon[0], lon[0] + 360.0, 'coe'))


def get_ax_size(fig, ax):
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    width, height = bbox.width, bbox.height
    width *= fig.dpi
    height *= fig.dpi
    return width, height


def plot_panel(n, fig, proj, var, clevels, cmap,
               title, parameters, stats=None):

    var = add_cyclic(var)
    lon = var.getLongitude()
    lat = var.getLatitude()
    var = ma.squeeze(var.asma())

    # Contour levels
    levels = None
    norm = None
    if len(clevels) > 0:
        levels = [-1.0e8] + clevels + [1.0e8]
        norm = colors.BoundaryNorm(boundaries=levels, ncolors=256)

    # Contour plot
    ax = fig.add_axes(panel[n], projection=proj)
    ax.set_global()
    cmap = get_colormap(cmap, parameters)
    p1 = ax.contourf(lon, lat, var,
                     transform=ccrs.PlateCarree(),
                     norm=norm,
                     levels=levels,
                     cmap=cmap,
                     extend='both',
                     )
    
    ax.set_aspect('auto')
    ax.coastlines(lw=0.3)
    if title[0] is not None:
        ax.set_title(title[0], loc='left', fontdict=plotSideTitle)
    if title[1] is not None:
        ax.set_title(title[1], fontdict=plotTitle)
    if title[2] is not None:
        ax.set_title(title[2], loc='right', fontdict=plotSideTitle)
    ax.set_xticks([0, 60, 120, 180, 240, 300, 359.99], crs=ccrs.PlateCarree())
    # ax.set_xticks([-180, -120, -60, 0, 60, 120, 180], crs=ccrs.PlateCarree())
    ax.set_yticks([-90, -60, -30, 0, 30, 60, 90], crs=ccrs.PlateCarree())
    lon_formatter = LongitudeFormatter(
        zero_direction_label=True, number_format='.0f')
    lat_formatter = LatitudeFormatter()
    ax.xaxis.set_major_formatter(lon_formatter)
    ax.yaxis.set_major_formatter(lat_formatter)
    ax.tick_params(labelsize=8.0, direction='out', width=1)
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    # Color bar
    cbax = fig.add_axes(
        (panel[n][0] + 0.6635, panel[n][1] + 0.0215, 0.0326, 0.1792))
    cbar = fig.colorbar(p1, cax=cbax)
    w, h = get_ax_size(fig, cbax)

    if levels is None:
        cbar.ax.tick_params(labelsize=9.0, length=0)

    else:
        maxval = np.amax(np.absolute(levels[1:-1]))
        if maxval < 10.0:
            fmt = "%5.2f"
            pad = 25
        elif maxval < 100.0:
            fmt = "%5.1f"
            pad = 25
        else:
            fmt = "%6.1f"
            pad = 30
        cbar.set_ticks(levels[1:-1])
        labels = [fmt % l for l in levels[1:-1]]
        cbar.ax.set_yticklabels(labels, ha='right')
        cbar.ax.tick_params(labelsize=9.0, pad=pad, length=0)

    # Min, Mean, Max
    fig.text(panel[n][0] + 0.6635, panel[n][1] + 0.2107,
             "Max\nMean\nMin", ha='left', fontdict=plotSideTitle)
    fig.text(panel[n][0] + 0.7635, panel[n][1] + 0.2107, "%.2f\n%.2f\n%.2f" %
             stats[0:3], ha='right', fontdict=plotSideTitle)

    # RMSE, CORR
    if len(stats) == 5:
        fig.text(panel[n][0] + 0.6635, panel[n][1] - 0.0105,
                 "RMSE\nCORR", ha='left', fontdict=plotSideTitle)
        fig.text(panel[n][0] + 0.7635, panel[n][1] - 0.0105, "%.2f\n%.2f" %
                 stats[3:5], ha='right', fontdict=plotSideTitle)


def plot(reference, test, diff, metrics_dict, parameter):

    # Create figure, projection
    fig = plt.figure(figsize=parameter.figsize, dpi=parameter.dpi)
    proj = ccrs.PlateCarree(central_longitude=180)

    # First two panels
    min1 = metrics_dict['test']['min']
    mean1 = metrics_dict['test']['mean']
    max1 = metrics_dict['test']['max']

    plot_panel(0, fig, proj, test, parameter.contour_levels, parameter.test_colormap,
               (parameter.test_name_yrs, parameter.test_title, test.units), parameter, stats=(max1, mean1, min1))

    min2 = metrics_dict['ref']['min']
    mean2 = metrics_dict['ref']['mean']
    max2 = metrics_dict['ref']['max']
    plot_panel(1, fig, proj, reference, parameter.contour_levels, parameter.reference_colormap,
               (parameter.ref_name_yrs, parameter.reference_title, reference.units), parameter, stats=(max2, mean2, min2))

    # Third panel
    min3 = metrics_dict['diff']['min']
    mean3 = metrics_dict['diff']['mean']
    max3 = metrics_dict['diff']['max']
    r = metrics_dict['misc']['rmse']
    c = metrics_dict['misc']['corr']
    plot_panel(2, fig, proj, diff, parameter.diff_levels, parameter.diff_colormap,
               (None, parameter.diff_title, None), parameter, stats=(max3, mean3, min3, r, c))

    # Figure title
    fig.suptitle(parameter.main_title, x=0.5, y=0.96, fontsize=18)

    # Save figure
    for f in parameter.output_format:
        f = f.lower().split('.')[-1]
        fnm = os.path.join(get_output_dir(parameter.current_set,
            parameter), parameter.output_file + '.' + f)
        plt.savefig(fnm)
        # Get the filename that the user has passed in and display that.
        # When running in a container, the paths are modified.
        fnm = os.path.join(get_output_dir(parameter.current_set, parameter,
            ignore_container=True), parameter.output_file + '.' + f)
        print('Plot saved in: ' + fnm)

    # Save individual subplots
    for f in parameter.output_format_subplot:
        fnm = os.path.join(get_output_dir(
            parameter.current_set, parameter), parameter.output_file)
        page = fig.get_size_inches()
        i = 0
        for p in panel:
            # Extent of subplot
            subpage = np.array(p).reshape(2,2)
            subpage[1,:] = subpage[0,:] + subpage[1,:]
            subpage = subpage + np.array(border).reshape(2,2)
            subpage = list(((subpage)*page).flatten())
            extent = matplotlib.transforms.Bbox.from_extents(*subpage)
            # Save subplot
            fname = fnm + '.%i.' %(i) + f
            plt.savefig(fname, bbox_inches=extent)

            orig_fnm = os.path.join(get_output_dir(parameter.current_set, parameter,
                ignore_container=True), parameter.output_file)
            fname = orig_fnm + '.%i.' %(i) + f
            print('Sub-plot saved in: ' + fname)

            i += 1

    plt.close()




