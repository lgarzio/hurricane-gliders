#! /usr/bin/env python3

"""
Author: Lori Garzio on 3/16/2021
Last modified: 3/16/2021
"""
import pandas as pd
from erddapy import ERDDAP


def get_erddap_nc(server, ds_id, var_list=None, constraints=None):
    """
    Returns a netcdf dataset for a specified dataset ID
    :param server: e.g. 'https://data.ioos.us/gliders/erddap'
    :param ds_id: dataset ID e.g. ng314-20200806T2040
    :param var_list: optional list of variables
    :param constraints: optional list of constraints
    :return: netcdf dataset
    """
    e = ERDDAP(server=server,
               protocol='tabledap',
               response='nc')
    e.dataset_id = ds_id
    if constraints:
        e.constraints = constraints
    if var_list:
        e.variables = var_list
    try:
        ds = e.to_xarray()
        ds = ds.sortby(ds.time)
    except OSError:
        print('No dataset available for specified constraints: {}'.format(ds_id))
        ds = None

    return ds


def return_glider_ids(server, kwargs):
    """
    Searches an ERDDAP server for datasets and returns dataset IDs
    :param server: e.g. 'https://data.ioos.us/gliders/erddap'
    :param kwargs: dictionary containing coordinate and time limits
    :return: array containing dataset IDs
    """
    e = ERDDAP(server=server)
    search_url = e.get_search_url(response='csv', **kwargs)
    search = pd.read_csv(search_url)
    ds_ids = search['Dataset ID'].values

    return ds_ids
