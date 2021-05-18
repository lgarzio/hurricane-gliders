#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Written by Lori Garzio on 3/5/2021
Last modified 4/15/2021
"""

import os
import numpy as np
import datetime as dt
import xarray as xr
from matplotlib import pyplot as plt
import cartopy.crs as ccrs
from mpl_toolkits.axes_grid1 import make_axes_locatable
import cmocean as cmo
import functions.gliders as gliders
import functions.common as cf
import functions.plotting as pf
import functions.gofs as gofs
import functions.rtofs as rtofs
plt.rcParams.update({'font.size': 14})


def surfacevar_plot(figure, axis, longitude, latitude, data, colormap, colorlabel, color_lims=None, color_ticks=None):
    if color_lims:
        h = axis.pcolormesh(longitude, latitude, data, vmin=color_lims[0], vmax=color_lims[1], cmap=colormap,
                            transform=ccrs.PlateCarree())
    else:
        h = axis.pcolormesh(longitude, latitude, data, cmap=colormap, transform=ccrs.PlateCarree())

    # format the spacing of the colorbar
    divider = make_axes_locatable(axis)
    cax = divider.new_horizontal(size='5%', pad=0.1, axes_class=plt.Axes)
    figure.add_axes(cax)

    cb = plt.colorbar(h, cax=cax, extend='both')
    cb.set_label(label=colorlabel, fontsize=12)  # add the label on the colorbar
    cb.ax.tick_params(labelsize=12)  # format the size of the tick labels
    if color_ticks is not None:
        cb.set_ticks(color_ticks)

    plt.subplots_adjust(right=0.88)


def main(stime, etime, region, stm, sDir, profile_loc_models=None, profile_loc_gliders=None):
    lims, xticks = cf.define_region_limits(region)
    lims = [-100, -72, 18, 35]
    xticks = [-96, -92, -88, -84, -80, -76]
    #pltvars = ['temp', 'salt', 'ohc']
    pltvars = ['temp']
    depth = 0
    minfo = {'GOFS': {'temp': 'water_temp', 'salt': 'salinity', 'coords': {'depth': 'depth',
                                                                           'lat': 'lat',
                                                                           'lon': 'lon'}},
             'RTOFS': {'temp': 'temperature', 'salt': 'salinity', 'coords': {'depth': 'Depth',
                                                                             'lat': 'Latitude',
                                                                             'lon': 'Longitude'}},
             'RTOFSDA': {'temp': 'temperature', 'salt': 'salinity', 'coords': {'depth': 'Depth',
                                                                               'lat': 'Latitude',
                                                                               'lon': 'Longitude'}},
             }
    # minfo = {'RTOFS': {'temp': 'temperature', 'salt': 'salinity', 'coords': {'depth': 'Depth',
    #                                                                          'lat': 'Latitude',
    #                                                                          'lon': 'Longitude'}}
    #          }

    # vinfo = {'temp': {'label': 'SST ($^oC$)', 'name': 'SST', 'cmap': cmo.cm.thermal, 'lims': [28, 32],
    #                   'colorticks': np.arange(28, 33, 1), 'savename': 'sst'},
    #          'salt': {'label': 'Salinity', 'name': 'SSS', 'cmap': cmo.cm.haline, 'lims': [33, 37],
    #                   'colorticks': np.arange(33, 38, 1), 'savename': 'sss'},
    #          'ohc': {'label': r'OHC ($\rmKJ / cm^2$)', 'name': 'OHC (integrated 26C)', 'cmap': cmo.cm.thermal,
    #                  'lims': [20, 160], 'savename': 'ohc'}
    #          }

    vinfo = {'temp': {'label': 'SST ($^oC$)', 'name': 'SST', 'cmap': cmo.cm.thermal, 'lims': [28, 32],
                      'colorticks': np.arange(28, 33, 1), 'savename': 'sst'},
             'salt': {'label': 'Salinity', 'name': 'SSS', 'cmap': cmo.cm.haline, 'lims': [35, 37],
                      'colorticks': np.arange(35, 38, .5), 'savename': 'sss'},
             'ohc': {'label': r'OHC ($\rmKJ / cm^2$)', 'name': 'OHC (integrated 26C)', 'cmap': cmo.cm.thermal,
                     'lims': [20, 160], 'savename': 'ohc'}
             }

    # get the IBTrACS dataset
    # define storm indices in IBTrACS file
    stm_idx = {'Laura_2020': 276}
    ib = '/Users/garzio/Documents/rucool/hurricane_glider_project/IBTrACS/IBTrACS.last3years.v04r00.nc'
    ibvars = ['time', 'lat', 'lon', 'usa_sshs', 'landfall']
    ibdata = cf.return_ibtracs_storm(ib, stm_idx[stm], ibvars)

    # find the portion of the track for which model comparisons will be made
    # find the lat/lon index where the storm is in the Gulf of Mexico
    loc_idx = np.logical_and(ibdata['lon'] < -84, ibdata['lat'] < 30)
    tlon = ibdata['lon'][loc_idx]
    tlat = ibdata['lat'][loc_idx]
    cat = ibdata['usa_sshs'][loc_idx]
    ibtime_gom = ibdata['time'][loc_idx]  # time in the Gulf of Mexico

    for pv in pltvars:
        for model in minfo.keys():
            fig, ax = plt.subplots(subplot_kw=dict(projection=ccrs.PlateCarree()))
            # plot entire track
            ax.plot(ibdata['lon'], ibdata['lat'], c='dimgray', marker='None', linewidth=2, transform=ccrs.PlateCarree())

            # plot IBTrACS data points for storm intensity
            cmap, hurr_legend = pf.hurricane_intensity_cmap(cat)
            ax.scatter(tlon, tlat, c=cat, cmap=cmap, marker='o', edgecolor='k', s=40, transform=ccrs.PlateCarree(),
                       zorder=10)

            # plot timestamps
            for tidx in [0, 7, 15]:
                ax.plot(tlon[tidx], tlat[tidx], c='k', marker='None', ms=8, linestyle='none',
                        transform=ccrs.PlateCarree(),
                        zorder=11)
                ax.text(tlon[tidx] + .5, tlat[tidx], ibtime_gom[tidx].strftime('%m%dT%H'),
                        bbox=dict(facecolor='lightgray', alpha=0.7), fontsize=7)

            if profile_loc_models:
                for pm in profile_loc_models:
                    ax.plot(pm[0], pm[1], c='w', marker='s', mec='k', ms=9, linestyle='none',
                            transform=ccrs.PlateCarree(),
                            label='Model Comparisons Only')

            if profile_loc_gliders:
                for glid, pg in profile_loc_gliders.items():
                    ax.plot(pg['loc'][0], pg['loc'][1], c='w', marker='^', mec='k', ms=8, linestyle='none',
                            transform=ccrs.PlateCarree(), label='Glider/Model Comparisons')
                    ax.text(pg['text'][0], pg['text'][1], glid, fontsize=7)

            handles, labels = plt.gca().get_legend_handles_labels()  # only show one set of legend labels
            by_label = dict(zip(labels, handles))

            # add 2 legends
            first_legend = plt.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize=7)
            plt.legend(handles=hurr_legend, loc='upper left', fontsize=7)
            plt.gca().add_artist(first_legend)

            # add model data to map
            print('\nPlotting {} {}'.format(model, pv))
            if model == 'GOFS':
                if pv == 'ohc':
                    #mvar = gofs.return_gridded_ds(minfo[model]['temp'], stime, etime, lims)
                    mvar = xr.open_dataarray('/Users/garzio/Documents/rucool/hurricane_glider_project/Laura_2020/GOFS_data/GOFS_mvar_20200823T12.nc')
                    #mvar = xr.open_dataarray('/Users/garzio/Documents/rucool/hurricane_glider_project/Laura_2020/GOFS_data/GOFS_mvar_20200828T12.nc')
                    ohc = cf.ohc_surface_3d(mvar, minfo[model]['coords'], model)
                    lonvalues = gofs.convert_gofs_target_lon(ohc.lon.values)
                    latvalues = ohc.lat.values
                else:
                    mvar = gofs.return_surface_variable(minfo[model][pv], stime, etime, lims, depth)
                    lonvalues = gofs.convert_gofs_target_lon(mvar.lon.values)
                    latvalues = mvar.lat.values
            elif model in ['RTOFS', 'RTOFSDA']:
                if pv == 'ohc':
                    mvar = rtofs.return_gridded_ds(minfo[model]['temp'], stime, etime, lims, model)
                    ohc = cf.ohc_surface_3d(mvar, minfo[model]['coords'], model)
                    lonvalues = ohc.Longitude.values
                    latvalues = ohc.Latitude.values
                else:
                    mvar = rtofs.return_surface_variable(minfo[model][pv], stime, etime, lims, model, depth)
                    lonvalues = mvar.Longitude.values
                    latvalues = mvar.Latitude.values

            savefile = os.path.join(sDir, '{}_{}_track_{}_{}.png'.format(stm, model, vinfo[pv]['savename'],
                                                                         stime.strftime('%Y%m%dT%H')))
            ttl = ' Hurricane Laura 2020\n{} {} and Gliders on: {}'.format(model, vinfo[pv]['name'],
                                                                           stime.strftime('%Y-%m-%d %H:%M'))
            # ttl = ' Hurricane Laura 2020\nSalinity (150m) {} and Gliders on: {}'.format(model,
            #                                                                stime.strftime('%Y-%m-%d %H:%M'))
            plt.title(ttl, fontsize=12)
            if pv == 'ohc':
                surfacevar_plot(fig, ax, lonvalues, latvalues, ohc.values, vinfo[pv]['cmap'], vinfo[pv]['label'],
                                vinfo[pv]['lims'])
            else:
                surfacevar_plot(fig, ax, lonvalues, latvalues, mvar.values, vinfo[pv]['cmap'], vinfo[pv]['label'],
                                vinfo[pv]['lims'], vinfo[pv]['colorticks'])

            pf.add_map_features(ax, lims, xlocs=xticks, landcolor='lightgray')

            plt.savefig(savefile, dpi=300)
            plt.close()


if __name__ == '__main__':
    start_time = dt.datetime(2020, 8, 22)
    end_time = dt.datetime(2020, 8, 22)
    region = 'GoMex'
    storm_name = 'Laura_2020'
    save_dir = os.path.join('/Users/garzio/Documents/rucool/hurricane_glider_project', storm_name)
    plm = [[-91.5, 26.5], [-85, 22.7]]  # add points for model profile comparisons
    plg = dict(ng314=dict(loc=[-92.97, 27.48], text=[-94.4, 27.55]),
               ng645=dict(loc=[-90.9, 26.56], text=[-90.6, 26.56]),
               Stommel=dict(loc=[-94.63, 26.87], text=[-94.3, 26.5]))  # add points for glider profile comparisons
    main(start_time, end_time, region, storm_name, save_dir, plm, plg)
