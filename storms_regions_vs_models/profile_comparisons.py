#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: Lori Garzio on 3/3/2021
Last modified: 3/3/2021
"""

import os
import datetime as dt
import numpy as np
from matplotlib import pyplot as plt
import functions.cmems as cmems
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


def main(stime, etime, stm, sDir, profile_locs):
    pltvars = ['temp', 'salt']
    max_depth = [500, 300]
    minfo = {'GOFS': {'temp': 'water_temp', 'salt': 'salinity', 'color': 'tab:blue'},
             'RTOFS': {'temp': 'temperature', 'salt': 'salinity', 'color': 'tab:orange'},
             'RTOFSDA': {'temp': 'temperature', 'salt': 'salinity', 'color': 'tab:purple'}
             }
    vinfo = {'temp': {'label': 'Temperature ($^oC$)'},
             'salt': {'label': 'Salinity'}
             }

    xticks0 = {500: {'temp': np.arange(10, 35, 5), 'salt': np.arange(35.6, 37, .2)},
               300: {'temp': np.arange(18, 32, 2), 'salt': np.arange(36.2, 37, .2)}}

    xticks1 = {500: {'temp': np.arange(10, 35, 5), 'salt': np.arange(35.2, 37, .2)},
               300: {'temp': np.arange(10, 35, 5), 'salt': np.arange(35.6, 37, .2)}}

    for i, pl in enumerate(profile_locs):
        for md in max_depth:
            for pv in pltvars:
                print('\nPlotting {} {}m'.format(pv, str(md)))
                fig, ax = plt.subplots(figsize=(8, 9))
                plt.subplots_adjust(right=0.88, left=0.15)
                plt.grid()

                # get GOFS data
                print('\nPlotting GOFS')
                target_lonGOFS = gofs.convert_target_gofs_lon(pl[0])
                GOFS_targetvar = gofs.return_point(minfo['GOFS'][pv], stime, etime, target_lonGOFS[0], pl[1])
                GOFS_targetvar = GOFS_targetvar.sel(depth=slice(0, md))
                ax.plot(GOFS_targetvar.values, GOFS_targetvar.depth.values, lw=3, c=minfo['GOFS']['color'], label='GOFS')

                # get RTOFS data
                print('\nPlotting RTOFS')
                RTOFS_targetvar = rtofs.return_point(minfo['RTOFS'][pv], stime, etime, pl[0], pl[1], 'RTOFS')
                RTOFS_targetvar = RTOFS_targetvar.sel(Depth=slice(0, md))
                ax.plot(RTOFS_targetvar.values, RTOFS_targetvar.Depth.values, lw=3, c=minfo['RTOFS']['color'],
                        label='RTOFS')

                # get RTOFS-DA data
                print('\nPlotting RTOFS-DA')
                RTOFSDA_targetvar = rtofs.return_point(minfo['RTOFSDA'][pv], stime, etime, pl[0], pl[1], 'RTOFSDA')
                RTOFSDA_targetvar = RTOFSDA_targetvar.sel(Depth=slice(0, md))
                ax.plot(RTOFSDA_targetvar.values, RTOFSDA_targetvar.Depth.values, lw=3, c=minfo['RTOFSDA']['color'],
                        label='RTOFSDA')

                if i == 0:
                    xticks = xticks0[md][pv]
                else:
                    xticks = xticks1[md][pv]
                ax.set_xticks(xticks)
                ax.set_xlabel(vinfo[pv]['label'])
                ax.set_ylabel('Depth (m)')
                ax.invert_yaxis()
                ax.legend(fontsize=12)
                ax.set_title('Model comparison at coordinates: {}\n{}: {}'.format(str(pl), stm.split('_')[0],
                                                                                  stime.strftime('%Y-%m-%d %H:%M')))

                savefile = os.path.join(sDir, '{}_profiles_{}_loc{}_{}m_{}.png'.format(stm, pv, i, str(md),
                                                                                       stime.strftime('%Y%m%dT%H')))
                plt.savefig(savefile, dpi=300)


if __name__ == '__main__':
    # start_time = dt.datetime(2020, 8, 23, 12)
    # end_time = dt.datetime(2020, 8, 23, 12)
    start_time = dt.datetime(2020, 8, 28, 12)
    end_time = dt.datetime(2020, 8, 28, 12)
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    profile_locations = [[-85, 22.7], [-91.5, 26.5]]
    main(start_time, end_time, storm_name, save_dir, profile_locations)
