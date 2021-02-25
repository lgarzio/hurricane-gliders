#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: aristizabal on 9/14/2020
Last modified: Lori Garzio on 2/25/2021
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


def add_sst_plot(figure, axis, longitude, latitude, data):
    h = axis.pcolormesh(longitude, latitude, data, cmap=cmo.cm.thermal, transform=ccrs.PlateCarree())

    # format the spacing of the colorbar
    divider = make_axes_locatable(axis)
    cax = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    figure.add_axes(cax)

    cb = plt.colorbar(h, cax=cax)
    cb.set_label(label='SST ($^oC$)', fontsize=12)  # add the label on the colorbar
    cb.ax.tick_params(labelsize=12)  # format the size of the tick labels


def return_ibtracs_data(nc, variables):
    # remove fill values and append data to dictionary
    d = dict()
    for v in variables:
        vv = nc[v]
        if v == 'time':
            fv = cftime.DatetimeGregorian(-25518, 1, 28, 0, 0, 0, 0)
        else:
            fv = vv._FillValue
        d[v] = vv.values[vv != fv]
    return d


def main(stime, etime, region, sDir):
    lims = cf.define_region_limits(region)

    # download CMEMS data
    # cmems.download_ds(stime, etime, lims, '500')
    cmems_file = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/CMEMS/cmems20200823.nc'

    CMEMSsst = cmems.return_sst(stime, etime, lims)

    # IBTrACS dataset
    ib = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibnc = xr.open_dataset(ib, mask_and_scale=False)
    ncf = ibnc.sel(storm=276)  # Hurricane Laura

    ibvars = ['time', 'lat', 'lon']
    ibdata = return_ibtracs_data(ncf, ibvars)

    fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))

    # plot entire track
    ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=1, transform=ccrs.PlateCarree(),
            label='Full Track')

    # plot the portion of the track for which model comparisons will be made
    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]

    targetlon = np.array([])
    targetlat = np.array([])
    for ii, tl in enumerate(tlon):
        if ii > 0:
            x1 = tl
            x2 = tlon[ii - 1]
            y1 = tlat[ii]
            y2 = tlat[ii - 1]
            m = (y1-y2)/(x1-x2)
            b = y1 - m * x1
            X = np.arange(x1, x2, 0.1)
            Y = b + m * X
            if ii == 1:
                targetlon = np.append(targetlon, x2)
                targetlat = np.append(targetlat, y2)
            targetlon = np.append(targetlon, X[::-1])
            targetlat = np.append(targetlat, Y[::-1])

    ax.plot(targetlon, targetlat, c='k', marker='o', ms=3, linestyle='none', transform=ccrs.PlateCarree(),
            label='Model Comparison')

    ax.legend(fontsize=8)

    # add GOFS SST to map
    print('\nPlotting GOFS SST')
    GOFSsst = gofs.return_sst(stime, etime, lims)
    savefile = os.path.join(sDir, '202102_Hurricane_Laura', 'Laura_GOFS_track_sst.png')
    plt.title('GOFS SST: {}'.format(stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)
    GOFSsst_lonconvert = gofs.convert_gofs_target_lon(GOFSsst.lon.values)

    add_sst_plot(fig, ax, GOFSsst_lonconvert, GOFSsst.lat.values, GOFSsst.values)

    pf.add_map_features(ax, lims, landcolor='lightgray')

    plt.savefig(savefile, dpi=300)
    plt.close()

    # # add RTOFS SST to map
    # print('\nPlotting RTOFS SST')
    # RTOFSsst = rtofs.return_sst(stime, etime, lims)
    # savefile = os.path.join(sDir, '202102_Hurricane_Laura', 'Laura_RTOFS_track_sst.png')
    # plt.title('RTOFS SST: {}'.format(stime.strftime('%Y-%m-%d %H:%M')), fontsize=12)
    #
    # add_sst_plot(fig, ax, RTOFSsst.Longitude.values, RTOFSsst.Latitude.values, RTOFSsst.values)
    #
    # pf.add_map_features(ax, lims, landcolor='lightgray')
    #
    # plt.savefig(savefile, dpi=300)
    # plt.close()

    # get data from each model closest to the hurricane track and plot the transect
    min_valt = 6
    max_valt = 32

    min_vals = 33
    max_vals = 37.1

    # plot GOFS transect closest to the hurricane track
    print('\nRetrieving GOFS water temp transect')
    # Convert longitude to GOFS convention
    target_lonGOFS = gofs.convert_target_gofs_lon(targetlon)
    GOFS_targettemp, GOFS_depth, GOFS_lon_subset, GOFS_lat_subset = gofs.return_transect('water_temp', stime, etime,
                                                                                         target_lonGOFS, targetlat)

    fig, ax = plt.subplots(figsize=(12, 6))
    kw = dict(levels=np.arange(min_valt, max_valt))

    cs = plt.contourf(GOFS_lon_subset, GOFS_depth, GOFS_targettemp, cmap=cmo.cm.thermal, **kw)
    plt.colorbar(cs, ax=ax, label='Temperature ($^oC$)', pad=0.02)
    plt.contour(GOFS_lon_subset, GOFS_depth, GOFS_targettemp, [26], colors='k')
    plt.title('GOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M'))
    ax.set_ylim(0, 500)
    ax.invert_yaxis()
    ax.set_ylabel('Depth (m)')
    ax.set_xlabel('Longitude')

    savefile = os.path.join(sDir, '202102_Hurricane_Laura', 'Laura_GOFS_transect_temp.png')
    plt.savefig(savefile, dpi=300)
    plt.close()

    # # plot RTOFS transect closest to the hurricane track
    # print('\nRetrieving RTOFS water temp transect')
    # RTOFS_targettemp, RTOFS_depth, RTOFS_lon_subset, RTOFS_lat_subset = rtofs.return_transect('temperature', stime,
    #                                                                                           etime, targetlon,
    #                                                                                           targetlat)
    #
    # fig, ax = plt.subplots(figsize=(12, 6))
    # kw = dict(levels=np.arange(min_valt, max_valt))
    #
    # cs = plt.contourf(RTOFS_lon_subset, RTOFS_depth, RTOFS_targettemp, cmap=cmo.cm.thermal, **kw)
    # plt.colorbar(cs, ax=ax, label='Temperature ($^oC$)', pad=0.02)
    # plt.contour(RTOFS_lon_subset, RTOFS_depth, RTOFS_targettemp, [26], colors='k')
    # plt.title('RTOFS Transect on ' + stime.strftime('%Y-%m-%d %H:%M'))
    # ax.set_ylim(0, 500)
    # ax.invert_yaxis()
    # ax.set_ylabel('Depth (m)')
    # ax.set_xlabel('Longitude')
    #
    # savefile = os.path.join(sDir, '202102_Hurricane_Laura', 'Laura_RTOFS_transect_temp.png')
    # plt.savefig(savefile, dpi=300)
    # plt.close()


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 23, 12)
    end_time = dt.datetime(2020, 8, 23, 12)
    region = 'GoMex'
    save_dir = '/Users/lgarzio/Documents/rucool/hurricane_glider_project'
    main(start_time, end_time, region, save_dir)
