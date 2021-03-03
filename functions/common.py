#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/19/2021
Last modified: 3/3/2021
"""
import numpy as np
import xarray as xr
import cftime


def define_region_limits(region):
    """
    :param region: region of interest
    :return: [lon min, lon max, lat min, lat max]
    """

    if region == 'GoMex':
        limits = [-100, -80, 18, 32]
    return limits


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
        d[v] = vv.values[vv != fv]
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
