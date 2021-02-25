#! /usr/bin/env python3

"""
Author: Lori Garzio on 2/25/2021
Last modified: 2/25/2021
"""
import datetime as dt
import os

# COPERNICUS MARINE ENVIRONMENT MONITORING SERVICE (CMEMS)
# ncCOP_global = '/home/lgarzio/cmems/global-analysis-forecast-phy-001-024_1565877333169.nc'  # on server
# ncCOP_global = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/CMEMS/global-analysis-forecast-phy-001-024_1565877333169.nc'  # on local machine


def download_ds(st, et, coordlims, depth_max):
    url = 'http://nrt.cmems-du.eu/motu-web/Motu'
    service_id = 'GLOBAL_ANALYSIS_FORECAST_PHY_001_024-TDS'
    product_id = 'global-analysis-forecast-phy-001-024'
    out_dir = '/Users/lgarzio/Documents/rucool/hurricane_glider_project/CMEMS'
    out_name = 'cmems{}.nc'.format(st.strftime('%Y%m%d'))

    motuc = 'python -m motuclient --motu ' + url + \
            ' --service-id ' + service_id + \
            ' --product-id ' + product_id + \
            ' --longitude-min ' + str(coordlims[0] - 1/6) + \
            ' --longitude-max ' + str(coordlims[1] + 1/6) + \
            ' --latitude-min ' + str(coordlims[2] - 1/6) + \
            ' --latitude-max ' + str(coordlims[3] + 1/6) + \
            ' --date-min ' + str(st - dt.timedelta(0.5)) + '"' + \
            ' --date-max ' + str(et + dt.timedelta(0.5)) + '"' + \
            ' --depth-min ' + '0.493' + \
            ' --depth-max ' + depth_max + \
            ' --variable ' + 'thetao' + ' ' + \
            ' --variable ' + 'so' + ' ' + \
            ' --out-dir ' + out_dir + \
            ' --out-name ' + out_name + ' ' + \
            ' --user ' + 'lgarzio' + ' ' + \
            ' --pwd ' + 'Lori_CMEMS2021'

    os.system(motuc)
    print('\nCMEMS file: {}'.format('/Users/lgarzio/Documents/rucool/hurricane_glider_project/CMEMS/cmems20200823.nc'))
