#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/24/2021
Last modified: 3/29/2021
"""
import numpy as np
import xarray as xr
import datetime as dt
import netCDF4

# urls for GOFS 3.1
# url_gofs = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z'  # temperature and salinity
# url_gofs = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/uv3z'  # u and v


def convert_target_gofs_lon(target_lon):
    target_convert = np.array([])
    if np.logical_or(isinstance(target_lon, float), isinstance(target_lon, int)):
        target_lon = np.array([target_lon])
    for tc in target_lon:
        if tc < 0:
            target_convert = np.append(target_convert, 360 + tc)
        else:
            target_convert = np.append(target_convert, tc)
    return target_convert


def convert_gofs_target_lon(gofs_lon):
    gofslon_convert = np.array([])
    if np.logical_or(isinstance(gofs_lon, float), isinstance(gofs_lon, int)):
        gofs_lon = np.array([gofs_lon])
    for gl in gofs_lon:
        if gl > 180:
            gofslon_convert = np.append(gofslon_convert, gl - 360)
        else:
            gofslon_convert = np.append(gofslon_convert, gl)
    return gofslon_convert


def get_ds(varname, st, et):
    if varname in ['tau', 'water_temp', 'water_temp_bottom', 'salinity', 'salinity_bottom']:
        url = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/ts3z'  # temperature and salinity
    else:
        url = 'https://tds.hycom.org/thredds/dodsC/GLBy0.08/expt_93.0/uv3z'  # u and v

    ds = xr.open_dataset(url, decode_times=False)
    if et - st == dt.timedelta(0):
        ds = ds.sel(time=netCDF4.date2num(st, ds.time.units), method='nearest')
    else:
        print('figure out time slicing')

    return ds


def return_gridded_ds(varname, start_time, end_time, coordlims, depth_slice=None):
    ds = get_ds(varname, start_time, end_time)
    if depth_slice:
        ds = ds.sel(depth=slice(depth_slice[0], depth_slice[1]))

    lon = ds.lon.values
    lat = ds.lat.values

    lon_convert = convert_gofs_target_lon(lon)
    lon_ind = np.logical_and(lon_convert > coordlims[0], lon_convert < coordlims[1])
    lat_ind = np.logical_and(lat > coordlims[2], lat < coordlims[3])
    vardata = np.squeeze(ds[varname])[:, lat_ind, lon_ind]

    return vardata


def return_point(varname, start_time, end_time, target_lon, target_lat):
    ds = get_ds(varname, start_time, end_time)

    lat = ds.lat.values
    lon = ds.lon.values

    # Find the closest model point
    # calculate the absolute value distance between the model location and buoy location
    lat_idx = np.argmin(abs(lat - target_lat))
    lon_idx = np.argmin(abs(lon - target_lon))

    target_ds = np.squeeze(ds[varname])[:, lat_idx, lon_idx]

    return target_ds


def return_surface_variable(varname, start_time, end_time, coordlims, depth):
    """
    :param varname: variable name
    :param start_time: start time (datetime)
    :param end_time: end time (datetime)
    :param coordlims: [lon min, lon max, lat min, lat max]
    :return: GOFS surface data object
    """
    ds = get_ds(varname, start_time, end_time)
    lat = ds.lat.values
    lon = ds.lon.values

    ds_surface = ds[varname].sel(depth=depth)
    lon_convert = convert_gofs_target_lon(lon)
    lon_ind = np.logical_and(lon_convert > coordlims[0], lon_convert < coordlims[1])
    lat_ind = np.logical_and(lat > coordlims[2], lat < coordlims[3])
    ds_surface = np.squeeze(ds_surface)[lat_ind, lon_ind]

    return ds_surface


def return_transect(varname, start_time, end_time, target_lons, target_lats):
    ds = get_ds(varname, start_time, end_time)

    lat = ds.lat.values
    lon = ds.lon.values

    # find the GOFS lat/lon indicies closest to the lats/lons provided
    lon_idx = np.round(np.interp(target_lons, lon, np.arange(0, len(lon)))).astype(int)
    lat_idx = np.round(np.interp(target_lats, lat, np.arange(0, len(lat)))).astype(int)

    lon_subset = lon[lon_idx]
    lon_subset_convert = convert_gofs_target_lon(lon_subset)
    lat_subset = lat[lat_idx]

    depth = ds.depth.values
    # target_var = ds.variables[varname][:, lat_idx, lon_idx]
    target_var = np.empty((len(depth), len(lon_idx)))
    target_var[:] = np.nan

    for pos in range(len(lon_idx)):
        print(len(lon_idx), pos)
        target_var[:, pos] = ds.variables[varname][:, lat_idx[pos], lon_idx[pos]]

    return target_var, depth, lon_subset_convert, lat_subset
