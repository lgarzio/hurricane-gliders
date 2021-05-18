#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/19/2021
Last modified: 4/15/2021
"""
import numpy as np
import xarray as xr
import cftime
import seawater as sw


def define_region_limits(region):
    """
    :param region: region of interest
    :return: [lon min, lon max, lat min, lat max]
    """

    if region == 'GoMex':
        limits = [-100, -80, 18, 32]
        xticks = [-96, -92, -88, -84]
    return limits, xticks


def ohc_surface_2d(temp, depth):
    """
    Calculate ocean heat content integrated to the 26C isotherm
    :param temp: 2D array of seawater temperature at depths for a specific lat/lon transect
    :param depth: 1D array of corresponding depths
    """
    print('\nCalculating OHC')
    cp = 3985  # Heat capacity of salt water in J/(kg K)
    rho0 = 1025
    ohc = np.array([])
    for i in range(len(temp)):
        tempi = temp[i]
        ok26 = tempi >= 26
        if np.sum(ok26) > 0:
            if np.nanmin(depth[ok26]) > 10:    # if the warm pool isn't at the surface, skip
                ohc = np.append(ohc, np.nan)
            else:
                hc = cp * rho0 * np.trapz(tempi[ok26] - 26, depth[ok26]) * 10 ** -7  # KJ/cm2
                ohc = np.append(ohc, hc)
        else:
            ohc = np.append(ohc, np.nan)

    return ohc


def ohc_surface_3d(temp, coordnames, model):
    """
    Calculate ocean heat content integrated to the 26C isotherm
    :param temp: xarray dataset of seawater temperature with depth, latitude and longitude as dims
    :param coordnames: dictionary containing names of coordinates with keys: depth, lat, lon
    :param model: model (e.g. GOFS, RTOFS)
    """
    print('\nCalculating OHC')
    cp = 3985  # Heat capacity in J/(kg K)
    rho0 = 1025
    if model == 'GOFS':
        ohc = np.empty((len(temp[coordnames['lat']]), len(temp[coordnames['lon']])))
    else:
        ohc = np.empty(np.shape(temp[coordnames['lat']]))
    ohc[:] = np.nan
    lats = np.array([])
    lons = np.array([])
    for i, j in enumerate(ohc):
        for ii, jj in enumerate(j):
            tempi = temp[:, i, ii]
            if i == 0:
                lons = np.append(lons, tempi[coordnames['lon']].values)
            if ii == 0:
                lats = np.append(lats, tempi[coordnames['lat']].values)
            ok26 = tempi >= 26
            if np.sum(ok26) > 0:
                if np.nanmin(tempi[coordnames['depth']][ok26]) < 10:  # if the warm pool is at the surface
                    hc = cp * rho0 * np.trapz(tempi[ok26] - 26, tempi[coordnames['depth']][ok26]) * 10 ** -7  # KJ/cm2
                    ohc[i, ii] = hc

    ohc_ds = xr.DataArray(ohc, coords=[lats, lons], dims=[coordnames['lat'], coordnames['lon']])
    return ohc_ds


# def ohc_surface(temp):
#     """
#     calculate ocean heat content integrated to the 26C isotherm
#     :param temp: xarray dataset
#     """
#     cp = 3985  # Heat capacity in J/(kg K)
#
#     rho0 = 1025
#
#     temp26 = temp.where(temp >= 26, np.nan)  # convert temperatures < 26 to nan
#     test = np.trapz(temp26, axis=0)
#     ohc = cp * rho0 * np.trapz(temp26, axis=0) * 10 ** -7  # KJ/cm2
#
#     return ohc


def return_ibtracs_storm(fname, storm_idx, variables):
    ibnc = xr.open_dataset(fname, mask_and_scale=False)
    nc = ibnc.sel(storm=storm_idx)  # Hurricane Laura

    # remove fill values and append data to dictionary
    d = dict()
    for v in variables:
        vv = nc[v]
        if v == 'time':
            fv = cftime.DatetimeGregorian(-25518, 1, 28, 0, 0, 0, 0)
        else:
            fv = vv._FillValue
        data = vv.values[vv != fv]
        if v == 'landfall':  # there is always one less landfall value, replace with last value
            data = np.append(data, data[-1])
        d[v] = data
    return d


def return_target_transect(target_lons, target_lats):
    targetlon = np.array([])
    targetlat = np.array([])
    for ii, tl in enumerate(target_lons):
        if ii > 0:
            x1 = tl
            x2 = target_lons[ii - 1]
            y1 = target_lats[ii]
            y2 = target_lats[ii - 1]
            m = (y1 - y2) / (x1 - x2)
            b = y1 - m * x1
            X = np.arange(x1, x2, 0.1)
            Y = b + m * X
            if ii == 1:
                targetlon = np.append(targetlon, x2)
                targetlat = np.append(targetlat, y2)
            targetlon = np.append(targetlon, X[::-1])
            targetlat = np.append(targetlat, Y[::-1])
    return targetlon, targetlat


def calculate_density_3d(salinity, temperature, depth):
    depth_broadcast = np.tile(depth, (temperature.shape[2], temperature.shape[1], 1)).T
    density = sw.dens(salinity, temperature, depth_broadcast)
    return density
