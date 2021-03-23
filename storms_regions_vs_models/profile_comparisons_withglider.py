#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Lori Garzio on 3/3/2021
Last modified: 3/23/2021
"""

import os
import datetime as dt
import xarray as xr
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import functions.cmems as cmems
import functions.gliders as gliders
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


def main(stime, etime, stm, sDir, glider_deploy):
    pltvars = ['temp', 'salt']
    max_depth = [500, 300]
    minfo = {'GOFS': {'temp': 'water_temp', 'salt': 'salinity', 'color': 'tab:blue'},
             'RTOFS': {'temp': 'temperature', 'salt': 'salinity', 'color': 'tab:orange'},
             'RTOFSDA': {'temp': 'temperature', 'salt': 'salinity', 'color': 'tab:purple'},
             'glider': {'temp': 'temperature', 'salt': 'salinity', 'color': 'k'}
             }
    xlabels = {'temp': 'Temperature ($^oC$)',
               'salt': 'Salinity'}

    xticks = {500: {'temp': np.arange(10, 35, 5), 'salt': np.arange(35, 36.8, .2)},
              300: {'temp': np.arange(10, 35, 5), 'salt': np.arange(35.6, 36.6, .2)}}

    # get glider data
    dac_server = 'https://data.ioos.us/gliders/erddap'
    id = glider_deploy
    glider_vars = ['time', 'latitude', 'longitude', 'depth', 'conductivity', 'density', 'salinity', 'pressure',
                   'temperature']
    glider_ds = gliders.get_erddap_nc(dac_server, id, glider_vars)
    gtime0 = stime - dt.timedelta(hours=.5)
    gtime1 = etime + dt.timedelta(hours=.5)

    glider_ds = glider_ds.swap_dims({'row': 'time'})
    glider_tm = pd.to_datetime(glider_ds.time.values)
    gl_timeidx = np.logical_and(glider_tm > gtime0, glider_tm < gtime1)

    gltm = np.unique(glider_ds.time.values[gl_timeidx])
    gllat = np.unique(glider_ds.latitude.values[gl_timeidx])
    gllon = np.unique(glider_ds.longitude.values[gl_timeidx])
    gldepth = glider_ds.depth.values[gl_timeidx]
    #gltemp = glider_ds.temperature.values[gl_timeidx]
    #glsalt = glider_ds.salinity.values[gl_timeidx]

    for md in max_depth:
        for pv in pltvars:
            fig, ax = plt.subplots(figsize=(8, 9))
            plt.subplots_adjust(right=0.88, left=0.15)
            plt.grid()

            # get GOFS data
            target_lonGOFS = gofs.convert_target_gofs_lon(gllon[0])
            GOFS_targetvar = gofs.return_point(minfo['GOFS'][pv], stime, etime, target_lonGOFS[0], gllat[0])
            GOFS_targetvar = GOFS_targetvar.sel(depth=slice(0, md))
            ax.plot(GOFS_targetvar.values, GOFS_targetvar.depth.values, lw=3, c=minfo['GOFS']['color'], label='GOFS')

            # get RTOFS data
            RTOFS_targetvar = rtofs.return_point(minfo['RTOFS'][pv], stime, etime, gllon[0], gllat[0], 'RTOFS')
            RTOFS_targetvar = RTOFS_targetvar.sel(Depth=slice(0, md))
            ax.plot(RTOFS_targetvar.values, RTOFS_targetvar.Depth.values, lw=3, c=minfo['RTOFS']['color'],
                    label='RTOFS')

            # get RTOFS-DA data
            RTOFSDA_targetvar = rtofs.return_point(minfo['RTOFSDA'][pv], stime, etime, gllon[0], gllat[0], 'RTOFSDA')
            RTOFSDA_targetvar = RTOFSDA_targetvar.sel(Depth=slice(0, md))
            ax.plot(RTOFSDA_targetvar.values, RTOFSDA_targetvar.Depth.values, lw=3, c=minfo['RTOFSDA']['color'],
                    label='RTOFSDA')

            # plot glider data
            gl_varname = minfo['glider'][pv]
            gldepth_idx = gldepth <= md
            gldepth_sel = gldepth[gldepth_idx]
            glider_data = glider_ds[gl_varname].values[gl_timeidx][gldepth_idx]
            ax.plot(glider_data, gldepth_sel, lw=3, c=minfo['glider']['color'], label='ng314')

            ax.set_xticks(xticks[md][pv])
            ax.set_xlabel(xlabels[pv])
            ax.set_ylabel('Depth (m)')
            ax.invert_yaxis()
            ax.legend(fontsize=12)
            pl = [np.round(gllon[0], 2), np.round(gllat[0], 2)]

            gl_timestr = pd.to_datetime(gltm[0]).strftime('%Y-%m-%d %H:%M')
            ttl = 'Comparison at coordinates: {}\nModels: {} Glider: {}'.format(str(pl),
                                                                                stime.strftime('%Y-%m-%d %H:%M'),
                                                                                gl_timestr)
            ax.set_title(ttl)

            savefile = os.path.join(sDir, '{}_profiles_{}_{}m_withglider_{}.png'.format(stm, pv, str(md),
                                                                                        stime.strftime('%Y%m%dT%H')))
            plt.savefig(savefile, dpi=300)
            plt.close()


if __name__ == '__main__':
    # start_time = dt.datetime(2020, 8, 23, 12)
    # end_time = dt.datetime(2020, 8, 23, 12)
    start_time = dt.datetime(2020, 8, 28, 12)
    end_time = dt.datetime(2020, 8, 28, 12)
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    glider = 'ng314-20200806T2040'
    main(start_time, end_time, storm_name, save_dir, glider)
