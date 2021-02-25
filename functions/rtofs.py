#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/24/2021
Last modified: 2/25/2021
"""
import os
import numpy as np
import xarray as xr
import datetime as dt

# RTOFS folder
# folder_RTOFS = '/home/coolgroup/RTOFS/forecasts/domains/hurricanes/RTOFS_6hourly_North_Atlantic'  # on server
# folder_RTOFS = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/RTOFS/RTOFS_6hourly_North_Atlantic'  # on local machine


def get_files(start_time, end_time):
    rtofs_dir = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/RTOFS/RTOFS_6hourly_North_Atlantic'
    file_hours = [6, 12, 18, 24]
    file_list = []
    if end_time - start_time == dt.timedelta(0):
        tmstr = start_time.strftime('%Y%m%d')
        fh_idx = np.argmin([abs(fh - start_time.hour) for fh in file_hours])
        hourstr = '{:03d}'.format(file_hours[fh_idx])
        fname = os.path.join(rtofs_dir, 'rtofs.{}'.format(tmstr),
                             'rtofs_glo_3dz_f{}_6hrly_hvr_US_east.nc'.format(hourstr))
        file_list.append(fname)
    else:
        print('figure out how to grab multiple files')

    return file_list


def return_sst(start_time, end_time, coordlims):
    """
    :param start_time: start time (datetime)
    :param end_time: end time (datetime)
    :param coordlims: [lon min, lon max, lat min, lat max]
    :return: GOFS SST object
    """
    filenames = get_files(start_time, end_time)

    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates
    lat = ds.Latitude.values
    lon = ds.Longitude.values

    sst = np.squeeze(ds.temperature.sel(Depth=0.0))
    lon_ind = np.logical_and(lon > coordlims[0], lon < coordlims[1])
    lat_ind = np.logical_and(lat > coordlims[2], lat < coordlims[3])

    # find i and j indices of lon/lat in boundaries
    ind = np.where(np.logical_and(lon_ind, lat_ind))

    # subset data from min i,j lat/lon corner to max i,j lat/lon corner
    sst = np.squeeze(sst)[range(np.min(ind[0]), np.max(ind[0]) + 1),
                          range(np.min(ind[1]), np.max(ind[1]) + 1)]

    return sst


def return_transect(varname, start_time, end_time, target_lons, target_lats):
    filenames = get_files(start_time, end_time)

    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates
    lat = ds.Latitude.values
    lon = ds.Longitude.values

    # find the RTOFS lat/lon indicies closest to the lats/lons provided
    lon_idx = np.round(np.interp(target_lons, lon[0, :], np.arange(0, len(lon[0, :])))).astype(int)
    lat_idx = np.round(np.interp(target_lats, lat[:, 0], np.arange(0, len(lat[:, 0])))).astype(int)

    lon_subset = lon[0, lon_idx]
    lat_subset = lat[0, lat_idx]

    depth = ds.Depth.values
    # target_var = ds.variables[varname][:, lat_idx, lon_idx]
    target_var = np.empty((len(depth), len(lon_idx)))
    target_var[:] = np.nan

    for pos in range(len(lon_idx)):
        print(len(lon_idx), pos)
        target_var[:, pos] = ds.variables[varname][0, :, lat_idx[pos], lon_idx[pos]]

    return target_var, depth, lon_subset, lat_subset
