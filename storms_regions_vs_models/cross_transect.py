#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Lori Garzio on 3/3/2021
Last modified: Lori Garzio on 3/23/2021
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


def plot_xsection(axis, xdata, ydata, cdata, colormap, ttl, ylab, xlab, clab, kwargs=None, ylims=None):
    if kwargs:
        cs = plt.contourf(xdata, ydata, cdata, cmap=colormap, **kwargs)
    else:
        cs = plt.contourf(xdata, ydata, cdata, cmap=colormap)
    plt.colorbar(cs, ax=axis, label=clab, pad=0.02, extend='both')
    plt.contour(xdata, ydata, cdata, [26], colors='k')
    plt.title(ttl)
    if ylims:
        axis.set_ylim(ylims)
    axis.invert_yaxis()
    axis.set_ylabel(ylab)
    axis.set_xlabel(xlab)


def main(stime, etime, stm, sDir):
    pltvars = ['temp', 'salt']
    ylimits = [[0, 300], [0, 500]]
    minfo = {'GOFS': {'temp': 'water_temp', 'salt': 'salinity'},
             'RTOFS': {'temp': 'temperature', 'salt': 'salinity'},
             'RTOFSDA': {'temp': 'temperature', 'salt': 'salinity'}
             }
    vinfo = {'temp': {'label': 'SST ($^oC$)', 'name': 'SST', 'cmap': cmo.cm.thermal, 'lims': [6, 32],
                      'colorticks': np.arange(6, 32), 'savename': 'sst'},
             'salt': {'label': 'Salinity', 'name': 'SSS', 'cmap': cmo.cm.haline, 'lims': [31.2, 37.2],
                      'colorticks': np.arange(31.2, 37.2, .2), 'savename': 'sss'}
             }

    # get the IBTrACS dataset
    # define storm indices in IBTrACS file
    stm_idx = {'Laura_2020': 276}
    ib = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibvars = ['time', 'lat', 'lon']
    ibdata = cf.return_ibtracs_storm(ib, stm_idx[stm], ibvars)

    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]

    targetlon, targetlat = cf.return_target_transect(tlon, tlat)

    for pv in pltvars:
        for model in minfo.keys():
            for yl in ylimits:
                if model == 'GOFS':
                    target_lonGOFS = gofs.convert_target_gofs_lon(targetlon)
                    m_targetvar, m_depth, m_lon_subset, m_lat_subset = gofs.return_transect(minfo[model][pv], stime,
                                                                                            etime,
                                                                                            target_lonGOFS, targetlat)
                elif model == 'RTOFS':
                    m_targetvar, m_depth, m_lon_subset, m_lat_subset = rtofs.return_transect(minfo[model][pv], stime,
                                                                                             etime, targetlon,
                                                                                             targetlat, 'RTOFS')

                elif model == 'RTOFSDA':
                    m_targetvar, m_depth, m_lon_subset, m_lat_subset = rtofs.return_transect(minfo[model][pv], stime,
                                                                                             etime, targetlon,
                                                                                             targetlat, 'RTOFSDA')

                fig, ax = plt.subplots(figsize=(12, 6))
                kw = dict(levels=vinfo[pv]['colorticks'])
                plt_ttl = '{} Transect on {}'.format(model, stime.strftime('%Y-%m-%d %H:%M'))
                ylabel = 'Depth (m)'
                xlabel = 'Longitude'
                clabel = vinfo[pv]['label']
                color = vinfo[pv]['cmap']
                plot_xsection(ax, m_lon_subset, m_depth, m_targetvar, color, plt_ttl, ylabel, xlabel, clabel, kw, yl)

                savefile = os.path.join(sDir, '{}_{}_transect_{}_{}m_{}.png'.format(stm, model, pv, yl[1],
                                                                                    stime.strftime('%Y%m%dT%H')))

                plt.savefig(savefile, dpi=300)
                plt.close()


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 23, 12)
    end_time = dt.datetime(2020, 8, 23, 12)
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    main(start_time, end_time, storm_name, save_dir)

