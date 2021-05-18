#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/19/2021
Last modified: 2/19/2021
"""
import xarray as xr
import numpy as np
import matplotlib.ticker as mticker
import matplotlib as mpl
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import cmocean


def add_map_features(axis, axes_limits=None, xlocs=None, landcolor=None, ecolor=None, bath_file=None):
    """
    Adds latitude and longitude gridlines and labels, coastlines, and optional bathymetry to a cartopy map
    object
    :param axis: plotting axis object
    :param axes_limits: optional list of axis limits [min lon, max lon, min lat, max lat]
    :param axes_limits: optional list of x axis locations
    :param landcolor: optional land color, default is none
    :param ecolor: optional edge color, default is black
    :param bath_file: optional bathymetry file
    """
    gl = axis.gridlines(draw_labels=True, linewidth=.5, color='gray', alpha=0.5, linestyle='dotted', x_inline=False)
    gl.top_labels = False
    gl.right_labels = False
    gl.xlabel_style = {'size': 12}
    gl.ylabel_style = {'size': 12}
    if xlocs:
        gl.xlocator = mticker.FixedLocator(xlocs)

    # add some space between the grid labels and bottom of plot
    gl.xpadding = 12
    gl.ypadding = 12

    if axes_limits:
        axis.set_extent(axes_limits)

    land = cfeature.NaturalEarthFeature('physical', 'land', '10m')

    if landcolor is not None:
        lc = landcolor
    else:
        lc = 'none'

    if ecolor is not None:
        ec = ecolor
    else:
        ec = 'black'

    axis.add_feature(land, edgecolor=ec, facecolor=lc)

    coast = cfeature.NaturalEarthFeature('physical', 'coastline', '10m')
    axis.add_feature(coast, edgecolor='black', facecolor='none')

    axis.add_feature(cfeature.BORDERS)

    # add optional bathymetry
    if bath_file:
        ncbath = xr.open_dataset(bath_file)
        bath_lat = ncbath.variables['lat'][:]
        bath_lon = ncbath.variables['lon'][:]
        bath_elev = ncbath.variables['elevation'][:]

        #lon_lim = [-100.0, 0]
        lon_lim = [-100.0, -10.0]
        lat_lim = [0.0, 60.0]

        oklatbath = np.logical_and(bath_lat >= lat_lim[0], bath_lat <= lat_lim[-1])
        oklonbath = np.logical_and(bath_lon >= lon_lim[0], bath_lon <= lon_lim[-1])

        bath_latsub = bath_lat[oklatbath]
        bath_lonsub = bath_lon[oklonbath]
        bath_elevs = bath_elev[oklatbath, :]
        bath_elevsub = bath_elevs[:, oklonbath]

        lev = np.arange(-9000, 9100, 100)
        axis.contourf(bath_lonsub, bath_latsub, bath_elevsub, lev, cmap=cmocean.cm.topo)


def hurricane_intensity_cmap(categories):
    intensity_colors = [
        "#efefef",  # TS
        "#ffffb2",  # cat 1
        "#fed976",  # cat 2 "#feb24c"
        "#e69138",  # cat 3 "#fd8d3c"
        "#cc0000",  # cat 4 "#f03b20"
        "#990000",  # cat 5 "#bd0026"
    ]
    mincat = np.nanmin(categories)
    maxcat = np.nanmax(categories)
    custom_colors = intensity_colors[mincat: maxcat + 1]  # make the colors span the range of data
    hurricane_colormap = mpl.colors.ListedColormap(custom_colors)

    # make custom legend
    le = [Line2D([0], [0], marker='o', markerfacecolor='#efefef', mec='k', linestyle='none', label='TS'),
          Line2D([0], [0], marker='o', markerfacecolor='#ffffb2', mec='k', linestyle='none', label='Cat 1'),
          Line2D([0], [0], marker='o', markerfacecolor='#fed976', mec='k', linestyle='none', label='Cat 2'),
          Line2D([0], [0], marker='o', markerfacecolor='#e69138', mec='k', linestyle='none', label='Cat 3'),
          Line2D([0], [0], marker='o', markerfacecolor='#cc0000', mec='k', linestyle='none', label='Cat 4'),
          Line2D([0], [0], marker='o', markerfacecolor='#990000', mec='k', linestyle='none', label='Cat 5')]
    le_custom = le[mincat: maxcat + 1]  # make the legend handles span the range of data

    return hurricane_colormap, le_custom
