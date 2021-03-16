#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by Lori Garzio on 3/5/2021
Last modified 3/5/2021
"""

import os
import numpy as np
import datetime as dt
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cmocean as cmo
import functions.cmems as cmems
import functions.common as cf
import functions.plotting as pf
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


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


def surfacevar_plot(figure, axis, longitude, latitude, data, colormap, colorlabel, color_lims=None, color_ticks=None):
    if color_lims:
        h = axis.pcolormesh(longitude, latitude, data, vmin=color_lims[0], vmax=color_lims[1], cmap=colormap,
                            transform=ccrs.PlateCarree())
    else:
        h = axis.pcolormesh(longitude, latitude, data, cmap=colormap, transform=ccrs.PlateCarree())

    # format the spacing of the colorbar
    divider = make_axes_locatable(axis)
    cax = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    figure.add_axes(cax)

    cb = plt.colorbar(h, cax=cax, extend='both')
    cb.set_label(label=colorlabel, fontsize=12)  # add the label on the colorbar
    cb.ax.tick_params(labelsize=12)  # format the size of the tick labels
    if color_ticks is not None:
        cb.set_ticks(color_ticks)


def main(stime, etime, region, stm, sDir):
    lims, xticks = cf.define_region_limits(region)
    pltvars = ['temp', 'salt']
    #pltvars = ['salt']
    minfo = {'GOFS': {'temp': 'water_temp', 'salt': 'salinity'},
             'RTOFS': {'temp': 'temperature', 'salt': 'salinity'},
             'RTOFSDA': {'temp': 'temperature', 'salt': 'salinity'}
             }

    # add points for profile comparisons
    profile_locs = [[-91.5, 26.5], [-85, 22.7]]
    #profile_locs = [[-92.97, 27.48]]

    vinfo = {'temp': {'label': 'SST ($^oC$)', 'name': 'SST', 'cmap': cmo.cm.thermal, 'lims': [28, 32],
                      'colorticks': np.arange(28, 33, 1), 'savename': 'sst'},
             'salt': {'label': 'Salinity', 'name': 'SSS', 'cmap': cmo.cm.haline, 'lims': [33, 37],
                      'colorticks': np.arange(33, 38, 1), 'savename': 'sss'}
             }

    # get the IBTrACS dataset
    # define storm indices in IBTrACS file
    stm_idx = {'Laura_2020': 276}
    ib = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibvars = ['time', 'lat', 'lon', 'usa_sshs']
    ibdata = cf.return_ibtracs_storm(ib, stm_idx[stm], ibvars)

    # find the portion of the track for which model comparisons will be made
    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]
    cat = ibdata['usa_sshs'][loc_idx]

    targetlon, targetlat = cf.return_target_transect(tlon, tlat)

    for pv in pltvars:
        for model in minfo.keys():
            fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
            # plot entire track
            ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=2, transform=ccrs.PlateCarree(),
                    label='Full Track')

            # plot part of track for model comparison
            ax.plot(targetlon, targetlat, c='k', marker='None', linewidth=2, transform=ccrs.PlateCarree(),
                    label='Model Transect')

            # plot IBTrACS data points for storm intensity
            cmap, hurr_legend = hurricane_intensity_cmap(cat)
            ax.scatter(tlon, tlat, c=cat, cmap=cmap, marker='o', edgecolor='k', s=40, transform=ccrs.PlateCarree(), zorder=10)

            for pl in profile_locs:
                ax.plot(pl[0], pl[1], c='w', marker='s', mec='k', ms=8, linestyle='none', transform=ccrs.PlateCarree(),
                        label='Profile Comparison')

            handles, labels = plt.gca().get_legend_handles_labels()  # only show one set of legend labels
            by_label = dict(zip(labels, handles))

            # add 2 legends
            first_legend = plt.legend(by_label.values(), by_label.keys(), fontsize=8)
            plt.legend(handles=hurr_legend, loc='upper left', fontsize=8)
            plt.gca().add_artist(first_legend)

            # add model data to map
            print('\nPlotting {} {}'.format(model, pv))
            if model == 'GOFS':
                mvar = gofs.return_surface_variable(minfo[model][pv], stime, etime, lims)
                lonvalues = gofs.convert_gofs_target_lon(mvar.lon.values)
                latvalues = mvar.lat.values
            elif model in ['RTOFS', 'RTOFSDA']:
                mvar = rtofs.return_surface_variable(minfo[model][pv], stime, etime, lims, model)
                lonvalues = mvar.Longitude.values
                latvalues = mvar.Latitude.values
            savefile = os.path.join(sDir, '{}_{}_track_{}.png'.format(stm, model, vinfo[pv]['savename']))
            plt.title('{} {}: {}'.format(model, vinfo[pv]['name'], stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)
            surfacevar_plot(fig, ax, lonvalues, latvalues, mvar.values, vinfo[pv]['cmap'], vinfo[pv]['label'],
                            vinfo[pv]['lims'], vinfo[pv]['colorticks'])

            pf.add_map_features(ax, lims, xlocs=xticks, landcolor='lightgray')

            plt.savefig(savefile, dpi=300)
            plt.close()


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 23, 12)
    end_time = dt.datetime(2020, 8, 23, 12)
    region = 'GoMex'
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    main(start_time, end_time, region, storm_name, save_dir)
