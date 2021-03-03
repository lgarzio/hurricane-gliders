#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: aristizabal on 9/14/2020
Last modified: Lori Garzio on 3/3/2021
"""

import os
import numpy as np
import datetime as dt
from matplotlib import pyplot as plt
import cmocean as cmo
import functions.cmems as cmems
import functions.common as cf
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


def plot_xsection(xdata, ydata, cdata, colormap, ttl, ylab, xlab, clab, savefile, kwargs=None, ylims=None):
    fig, ax = plt.subplots(figsize=(12, 6))

    if kwargs:
        cs = plt.contourf(xdata, ydata, cdata, cmap=colormap, **kwargs)
    else:
        cs = plt.contourf(xdata, ydata, cdata, cmap=colormap)
    plt.colorbar(cs, ax=ax, label=clab, pad=0.02)
    plt.contour(xdata, ydata, cdata, [26], colors='k')
    plt.title(ttl)
    if ylims:
        ax.set_ylim(ylims)
    ax.invert_yaxis()
    ax.set_ylabel(ylab)
    ax.set_xlabel(xlab)

    plt.savefig(savefile, dpi=300)
    plt.close()


def main(stime, etime, stm, sDir):
    # get the IBTrACS dataset
    # define storm indices in IBTrACS file
    stm_idx = {'Laura_2020': 276}
    ib = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibvars = ['time', 'lat', 'lon']
    ibdata = cf.return_ibtracs_storm(ib, stm_idx[stm], ibvars)

    # plot the portion of the track for which model comparisons will be made
    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]

    targetlon, targetlat = cf.return_target_transect(tlon, tlat)

    # get data from each model closest to the hurricane track and plot the transect
    # PLOT TEMPERATURE
    min_valt = 6
    max_valt = 32

    # plot GOFS transect closest to the hurricane track
    print('\nRetrieving GOFS water temp transect')
    # Convert longitude to GOFS convention
    target_lonGOFS = gofs.convert_target_gofs_lon(targetlon)
    GOFS_targettemp, GOFS_depth, GOFS_lon_subset, GOFS_lat_subset = gofs.return_transect('water_temp', stime, etime,
                                                                                         target_lonGOFS, targetlat)
    color = cmo.cm.thermal
    kw = dict(levels=np.arange(min_valt, max_valt))
    plt_ttl = 'GOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylabel = 'Depth (m)'
    xlabel = 'Longitude'
    clabel = 'Temperature ($^oC$)'

    # plot GOFS cross section 0-300m
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_GOFS_transect_temp_300.png'.format(stm))
    plot_xsection(GOFS_lon_subset, GOFS_depth, GOFS_targettemp, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    # plot GOFS cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_GOFS_transect_temp_500.png'.format(stm))
    plot_xsection(GOFS_lon_subset, GOFS_depth, GOFS_targettemp, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    # plot RTOFS transect closest to the hurricane track
    print('\nRetrieving RTOFS water temp transect')
    RTOFS_targettemp, RTOFS_depth, RTOFS_lon_subset, RTOFS_lat_subset = rtofs.return_transect('temperature', stime,
                                                                                              etime, targetlon,
                                                                                              targetlat, 'RTOFS')
    # plot RTOFS cross section 0-300m
    plt_ttl = 'RTOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_RTOFS_transect_temp_300.png'.format(stm))
    plot_xsection(RTOFS_lon_subset, RTOFS_depth, RTOFS_targettemp, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    # plot RTOFS cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_RTOFS_transect_temp_500.png'.format(stm))
    plot_xsection(RTOFS_lon_subset, RTOFS_depth, RTOFS_targettemp, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    ## plot RTOFS-DA transect closest to the hurricane track
    print('\nRetrieving RTOFS-DA water temp transect')
    RTOFSDA_targettemp, RTOFSDA_depth, RTOFSDA_lon_subset, RTOFSDA_lat_subset = rtofs.return_transect('temperature',
                                                                                                      stime, etime,
                                                                                                      targetlon,
                                                                                                      targetlat,
                                                                                                      'RTOFS-DA')
    # plot RTOFS-DA cross section 0-300m
    plt_ttl = 'RTOFS-DA Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_RTOFSDA_transect_temp_300.png'.format(stm))
    plot_xsection(RTOFSDA_lon_subset, RTOFSDA_depth, RTOFSDA_targettemp, color, plt_ttl, ylabel, xlabel, clabel,
                  savefile, kw, ylimits)

    # plot RTOFS-DA cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_RTOFSDA_transect_temp_500.png'.format(stm))
    plot_xsection(RTOFSDA_lon_subset, RTOFSDA_depth, RTOFSDA_targettemp, color, plt_ttl, ylabel, xlabel, clabel,
                  savefile, kw, ylimits)

    # PLOT SALINITY
    min_vals = 30
    max_vals = 38

    # plot GOFS transect closest to the hurricane track
    print('\nRetrieving GOFS salinity transect')
    # Convert longitude to GOFS convention
    GOFS_targetsalt, GOFS_depth, GOFS_lon_subset, GOFS_lat_subset = gofs.return_transect('salinity', stime, etime,
                                                                                         target_lonGOFS, targetlat)
    color = cmo.cm.haline
    kw = dict(levels=np.arange(min_vals, max_vals))
    plt_ttl = 'GOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylabel = 'Depth (m)'
    xlabel = 'Longitude'
    clabel = 'Salinity'

    # plot GOFS cross section 0-300m
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_GOFS_transect_salt_300.png'.format(stm))
    plot_xsection(GOFS_lon_subset, GOFS_depth, GOFS_targetsalt, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    # plot GOFS cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_GOFS_transect_salt_500.png'.format(stm))
    plot_xsection(GOFS_lon_subset, GOFS_depth, GOFS_targetsalt, color, plt_ttl, ylabel, xlabel, clabel, savefile, kw,
                  ylimits)

    # plot RTOFS transect closest to the hurricane track
    print('\nRetrieving RTOFS salinity transect')
    RTOFS_targetsalt, RTOFS_depth, RTOFS_lon_subset, RTOFS_lat_subset = rtofs.return_transect('salinity', stime,
                                                                                              etime, targetlon,
                                                                                              targetlat, 'RTOFS')
    # plot RTOFS cross section 0-300m
    plt_ttl = 'RTOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_RTOFS_transect_salt_300.png'.format(stm))
    plot_xsection(RTOFS_lon_subset, RTOFS_depth, RTOFS_targetsalt, color, plt_ttl, ylabel, xlabel, clabel, savefile,
                  kw, ylimits)

    # plot RTOFS cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_RTOFS_transect_salt_500.png'.format(stm))
    plot_xsection(RTOFS_lon_subset, RTOFS_depth, RTOFS_targetsalt, color, plt_ttl, ylabel, xlabel, clabel, savefile,
                  kw, ylimits)

    ## plot RTOFS-DA transect closest to the hurricane track
    print('\nRetrieving RTOFS-DA salinity transect')
    RTOFSDA_targetsalt, RTOFSDA_depth, RTOFSDA_lon_subset, RTOFSDA_lat_subset = rtofs.return_transect('salinity',
                                                                                                      stime, etime,
                                                                                                      targetlon,
                                                                                                      targetlat,
                                                                                                      'RTOFS-DA')
    # plot RTOFS-DA cross section 0-300m
    plt_ttl = 'RTOFS-DA Transect on ' + stime.strftime('%Y-%m-%d %H:%M')
    ylimits = [0, 300]
    savefile = os.path.join(sDir, '{}_RTOFSDA_transect_salt_300.png'.format(stm))
    plot_xsection(RTOFSDA_lon_subset, RTOFSDA_depth, RTOFSDA_targetsalt, color, plt_ttl, ylabel, xlabel, clabel,
                  savefile, kw, ylimits)

    # plot RTOFS-DA cross section 0-500m
    ylimits = [0, 500]
    savefile = os.path.join(sDir, '{}_RTOFSDA_transect_salt_500.png'.format(stm))
    plot_xsection(RTOFSDA_lon_subset, RTOFSDA_depth, RTOFSDA_targetsalt, color, plt_ttl, ylabel, xlabel, clabel,
                  savefile, kw, ylimits)


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 23, 12)
    end_time = dt.datetime(2020, 8, 23, 12)
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    main(start_time, end_time, storm_name, save_dir)
