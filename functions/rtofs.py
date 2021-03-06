#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/24/2021
Last modified: 3/29/2021
"""
import os
import numpy as np
import xarray as xr
import datetime as dt
import pandas as pd

# RTOFS folder
# folder_RTOFS = '/home/coolgroup/RTOFS/forecasts/domains/hurricanes/RTOFS_6hourly_North_Atlantic'  # on server
# folder_RTOFS = '/Users/garzio/Documents/rucool/hurricane_glider_project/RTOFS/RTOFS_6hourly_North_Atlantic'  # on local machine

# RTOFS-DA folder
# folder_RTOFS_DA = '/home/lgarzio/hurricane_gliders/RTOFS_DA/data'  # on server
# folder_RTOFS_DA = '/Users/garzio/Documents/rucool/hurricane_glider_project/RTOFS-DA'  # on local machine


def get_files(start_time, end_time, model):
    if model == 'RTOFS':
        rtofs_dir = '/Users/garzio/Documents/rucool/hurricane_glider_project/RTOFS/RTOFS_6hourly_North_Atlantic'
    elif model == 'RTOFSDA':
        rtofs_dir = '/Users/garzio/Documents/rucool/hurricane_glider_project/RTOFS-DA'
    else:
        print('No valid model provided')
    #file_hours = [6, 12, 18, 24]
    file_list = []
    if end_time - start_time == dt.timedelta(0):
        t1 = start_time - dt.timedelta(days=1)
        t0 = start_time + dt.timedelta(days=1)
        daterange = pd.date_range(dt.date(t1.year, t1.month, t1.day), dt.date(t0.year, t0.month, t0.day), freq='6H')
        d_idx = np.argmin([abs(dr - start_time) for dr in daterange])  # find the closest file to the time of interest
        ts = daterange[d_idx]
        if ts.hour == 0:
            tmstr = (ts - dt.timedelta(days=1)).strftime('%Y%m%d')
            hourstr = '024'
        else:
            tmstr = ts.strftime('%Y%m%d')
            hourstr = '{:03d}'.format(ts.hour)
        # fh_idx = np.argmin([abs(fh - start_time.hour) for fh in file_hours])
        fname = os.path.join(rtofs_dir, 'rtofs.{}'.format(tmstr),
                             'rtofs_glo_3dz_f{}_6hrly_hvr_US_east.nc'.format(hourstr))
        file_list.append(fname)
    else:
        print('figure out how to grab multiple files')

    return file_list


def return_gridded_ds(varname, start_time, end_time, coordlims, model, depth_slice=None):
    filenames = get_files(start_time, end_time, model)
    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates

    lon = ds.Longitude.values
    lat = ds.Latitude.values

    if depth_slice:
        ds_var = np.squeeze(ds[varname].sel(Depth=slice(depth_slice[0], depth_slice[1])))
    else:
        ds_var = np.squeeze(ds[varname])

    lon_ind = np.logical_and(lon > coordlims[0], lon < coordlims[1])
    lat_ind = np.logical_and(lat > coordlims[2], lat < coordlims[3])

    # find i and j indices of lon/lat in boundaries
    ind = np.where(np.logical_and(lon_ind, lat_ind))

    # subset data from min i,j lat/lon corner to max i,j lat/lon corner
    vardata = np.squeeze(ds_var)[:, range(np.min(ind[0]), np.max(ind[0]) + 1),
                                 range(np.min(ind[1]), np.max(ind[1]) + 1)]

    return vardata


def return_point(varname, start_time, end_time, target_lon, target_lat, model):
    filenames = get_files(start_time, end_time, model)

    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates
    lat = ds.Latitude.values
    lon = ds.Longitude.values

    # Find the closest model point
    # calculate the sum of the absolute value distance between the model location and selected profile location
    a = abs(lat - target_lat) + abs(lon - target_lon)

    # find the indices of the minimum value in the array calculated above
    i, j = np.unravel_index(a.argmin(), a.shape)

    target_ds = np.squeeze(ds[varname])[:, i, j]

    return target_ds


def return_surface_variable(varname, start_time, end_time, coordlims, model, depth):
    """
    :param varname: variable name
    :param start_time: start time (datetime)
    :param end_time: end time (datetime)
    :param coordlims: [lon min, lon max, lat min, lat max]
    :return: RTOFS surface data object
    """
    filenames = get_files(start_time, end_time, model)

    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates
    lat = ds.Latitude.values
    lon = ds.Longitude.values

    ds_surface = np.squeeze(ds[varname].sel(Depth=depth))
    lon_ind = np.logical_and(lon > coordlims[0], lon < coordlims[1])
    lat_ind = np.logical_and(lat > coordlims[2], lat < coordlims[3])

    # find i and j indices of lon/lat in boundaries
    ind = np.where(np.logical_and(lon_ind, lat_ind))

    # subset data from min i,j lat/lon corner to max i,j lat/lon corner
    ds_surface = np.squeeze(ds_surface)[range(np.min(ind[0]), np.max(ind[0]) + 1),
                                        range(np.min(ind[1]), np.max(ind[1]) + 1)]

    return ds_surface


def return_transect(varname, start_time, end_time, target_lons, target_lats, model):
    filenames = get_files(start_time, end_time, model)

    ds = xr.open_dataset(filenames[0])
    ds = ds.drop('Date')  # drop unnecessary coordinates
    lat = ds.Latitude.values
    lon = ds.Longitude.values

    # find the RTOFS lat/lon indicies closest to the lats/lons provided
    lon_idx = np.round(np.interp(target_lons, lon[0, :], np.arange(0, len(lon[0, :])))).astype(int)
    lat_idx = np.round(np.interp(target_lats, lat[:, 0], np.arange(0, len(lat[:, 0])))).astype(int)

    lon_subset = lon[0, lon_idx]
    lat_subset = lat[lat_idx, 0]

    depth = ds.Depth.values
    # target_var = ds.variables[varname][:, lat_idx, lon_idx]
    target_var = np.empty((len(depth), len(lon_idx)))
    target_var[:] = np.nan

    for pos in range(len(lon_idx)):
        print(len(lon_idx), pos)
        target_var[:, pos] = ds.variables[varname][0, :, lat_idx[pos], lon_idx[pos]]

    return target_var, depth, lon_subset, lat_subset
