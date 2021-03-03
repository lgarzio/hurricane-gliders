#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: aristizabal on 9/14/2020
Last modified: Lori Garzio on 3/3/2021
"""

import os
import numpy as np
import xarray as xr
import datetime as dt
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cmocean as cmo
import cftime
import functions.cmems as cmems
import functions.common as cf
import functions.plotting as pf
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


def add_sst_plot(figure, axis, longitude, latitude, data, color_lims):
    h = axis.pcolormesh(longitude, latitude, data, vmin=color_lims[0], vmax=color_lims[1], cmap=cmo.cm.thermal,
                        transform=ccrs.PlateCarree())

    # format the spacing of the colorbar
    divider = make_axes_locatable(axis)
    cax = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    figure.add_axes(cax)

    cb = plt.colorbar(h, cax=cax)
    cb.set_label(label='SST ($^oC$)', fontsize=12)  # add the label on the colorbar
    cb.ax.tick_params(labelsize=12)  # format the size of the tick labels


def main(stime, etime, region, stm, sDir):
    lims = cf.define_region_limits(region)

    # download CMEMS data
    # # cmems.download_ds(stime, etime, lims, '500')
    # cmems_file = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/CMEMS/cmems20200823.nc'
    #
    # CMEMSsst = cmems.return_sst(stime, etime, lims)

    # get the IBTrACS dataset
    # define storm indices in IBTrACS file
    stm_idx = {'Laura_2020': 276}
    ib = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibvars = ['time', 'lat', 'lon']
    ibdata = cf.return_ibtracs_storm(ib, stm_idx[stm], ibvars)

    # find the portion of the track for which model comparisons will be made
    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]

    targetlon, targetlat = cf.return_target_transect(tlon, tlat)

    sst_lims = [27, 33]

    # GOFS
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
    # plot entire track
    ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=1, transform=ccrs.PlateCarree(),
            label='Full Track')

    # plot part of track for model comparison
    ax.plot(targetlon, targetlat, c='k', marker='o', ms=3, linestyle='none', transform=ccrs.PlateCarree(),
            label='Model Comparison')

    # add points for profile comparisons
    profile_locs = [[-91.5, 26.5], [-85, 22.7]]
    for pl in profile_locs:
        ax.plot(pl[0], pl[1], c='w', marker='s', mec='k', ms=5, linestyle='none', transform=ccrs.PlateCarree(),
                label='Profile Comparison')

    handles, labels = plt.gca().get_legend_handles_labels()  # only show one set of legend labels
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=8)
    # ax.legend(fontsize=8)

    # add GOFS SST to map
    print('\nPlotting GOFS SST')
    GOFSsst = gofs.return_sst(stime, etime, lims)
    savefile = os.path.join(sDir, '{}_GOFS_track_sst.png'.format(stm))
    plt.title('GOFS SST: {}'.format(stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)
    GOFSsst_lonconvert = gofs.convert_gofs_target_lon(GOFSsst.lon.values)

    add_sst_plot(fig, ax, GOFSsst_lonconvert, GOFSsst.lat.values, GOFSsst.values, sst_lims)

    pf.add_map_features(ax, lims, landcolor='lightgray')

    plt.savefig(savefile, dpi=300)
    plt.close()

    # RTOFS
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
    # plot entire track
    ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=1, transform=ccrs.PlateCarree(),
            label='Full Track')

    # plot part of track for model comparison
    ax.plot(targetlon, targetlat, c='k', marker='o', ms=3, linestyle='none', transform=ccrs.PlateCarree(),
            label='Model Comparison')

    # add points for profile comparisons
    for pl in profile_locs:
        ax.plot(pl[0], pl[1], c='w', marker='s', mec='k', ms=5, linestyle='none', transform=ccrs.PlateCarree(),
                label='Profile Comparison')

    handles, labels = plt.gca().get_legend_handles_labels()  # only show one set of legend labels
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=8)
    # ax.legend(fontsize=8)

    # add RTOFS SST to map
    print('\nPlotting RTOFS SST')
    RTOFSsst = rtofs.return_sst(stime, etime, lims, 'RTOFS')
    savefile = os.path.join(sDir, '{}_RTOFS_track_sst.png'.format(stm))
    plt.title('RTOFS SST: {}'.format(stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)

    add_sst_plot(fig, ax, RTOFSsst.Longitude.values, RTOFSsst.Latitude.values, RTOFSsst.values, sst_lims)

    pf.add_map_features(ax, lims, landcolor='lightgray')

    plt.savefig(savefile, dpi=300)
    plt.close()

    #RTOFS-DA
    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
    # plot entire track
    ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=1, transform=ccrs.PlateCarree(),
            label='Full Track')

    # plot part of track for model comparison
    ax.plot(targetlon, targetlat, c='k', marker='o', ms=3, linestyle='none', transform=ccrs.PlateCarree(),
            label='Model Comparison')

    # add points for profile comparisons
    for pl in profile_locs:
        ax.plot(pl[0], pl[1], c='w', marker='s', mec='k', ms=5, linestyle='none', transform=ccrs.PlateCarree(),
                label='Profile Comparison')

    handles, labels = plt.gca().get_legend_handles_labels()  # only show one set of legend labels
    by_label = dict(zip(labels, handles))
    ax.legend(by_label.values(), by_label.keys(), fontsize=8)
    # ax.legend(fontsize=8)

    # add RTOFS-DA SST to map
    print('\nPlotting RTOFS-DA SST')
    RTOFSDAsst = rtofs.return_sst(stime, etime, lims, 'RTOFS-DA')
    savefile = os.path.join(sDir, '{}_RTOFSDA_track_sst.png'.format(stm))
    plt.title('RTOFS-DA SST: {}'.format(stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)

    add_sst_plot(fig, ax, RTOFSDAsst.Longitude.values, RTOFSDAsst.Latitude.values, RTOFSDAsst.values, sst_lims)

    pf.add_map_features(ax, lims, landcolor='lightgray')

    plt.savefig(savefile, dpi=300)
    plt.close()


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 23, 12)
    end_time = dt.datetime(2020, 8, 23, 12)
    region = 'GoMex'
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/lgarzio/Documents/rucool/hurricane_glider_project', storm_name)
    main(start_time, end_time, region, storm_name, save_dir)
