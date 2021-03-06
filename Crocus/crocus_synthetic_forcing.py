#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function

from datetime import datetime, timedelta

import numpy as np
from netCDF4 import date2num

from Crocus.crocus_forcing_nc import CrocusForcing

'''
Create a simple forcing data set to test snow routines

TODO: Make a function for each forcing parameter and the creation of the data set.

Cloned from create_dummy_forcing

__author__ = 'kmu'
'''


class SyntheticForcing:
    def __init__(self, t_start, t_stop):
        # TODO: refactor self.t_start/stop to selt.start_time / .stop_time
        # TODO: make time input as string of iso-format YYYY-MM-DDTHH:MM:SS
        # Create the time line
        t_start = datetime(2014, 1, 21)
        t_stop = datetime(2014, 2, 10)
        dt = timedelta(hours=1)
        t_ref = 'hours since 2014-01-21 00:00:00'  # TODO: match to t_start or fix to Crocus default 1900-01-01 00:00:00
        self.time_arr = np.arange(t_start, t_stop, dt)  # array of datetime objects
        self.time_v = date2num(self.time_arr.tolist(),
                               t_ref)  # time_arr converted to seconds since reference time 't_ref'

        self.masks = {}

    def create_mask(self, mask_name, t_start, t_stop):
        self.masks[mask_name] = np.where(
            (self.time_arr >= datetime(2014, 1, 26)) & ((self.time_arr <= datetime(2014, 1, 27))))


# Create artificial parameters

# TODO: set time frame in the self__init_ routine
# Create the time line
t_start = datetime(2014, 1, 21)
t_stop = datetime(2014, 2, 10)
dt = timedelta(hours=1)
t_units = 'hours since 2014-01-21 00:00:00'  # TODO: match to t_start or fix to Crocus default 1900-01-01 00:00:00
time_arr = np.arange(t_start, t_stop, dt)
time_v = date2num(time_arr.tolist(), t_units)

n = len(time_arr)
n_arr = np.arange(n, dtype=float)


# TODO: make a method for mask generation self.masks - probably of type dict
# self.masks = {}
# self.masks['accumulate'] = np.where(self.time_arr < datetime(2014, 2, 3))
mask1 = np.where(time_arr < datetime(2014, 2, 3))  # accumulate
mask2 = np.where(time_arr >= datetime(2014, 2, 3))  # melt
mask3 = np.where((time_arr >= datetime(2014, 1, 26)) & ((time_arr <= datetime(2014, 1, 27))))
mask4 = np.where((time_arr >= datetime(2013, 9, 5)) & ((time_arr <= datetime(2013, 9, 10))))
mask5 = np.where(((time_arr >= datetime(2014, 1, 26)) & (time_arr <= datetime(2013, 9, 10))) | (
(time_arr >= datetime(2013, 11, 1)) & (time_arr <= datetime(2013, 11, 5))))
'''
tair = np.zeros_like(time_arr, dtype=float)
tair[mask1] += 270.0 # in Kelvin
tair[mask2] += 275.0
'''
tair = np.zeros_like(time_arr, dtype=float)
tair[mask1[0]] = np.linspace(265.0, 273.0, len(mask1[0]), dtype=float)
tair[mask2[0]] = np.linspace(273.0, 280.0, len(mask2[0]), dtype=float)

p_surf = np.zeros_like(time_arr, dtype=float)
p_surf += 90000.0  # Pa

q_air = np.zeros_like(time_arr, dtype=float)
q_air += 3.0e-03

rainf = np.zeros_like(time_arr, dtype=float)
# rainf[mask3[0]] += 1.0e-03

snowf = np.zeros_like(time_arr, dtype=float)
snowf[mask3[0]] += 1.0e-03

# Short-wave signal with an exponential increase towards the melting season
sw_amp = 50.  # amplitude of the short-wave signal
dir_sw_down = ((np.sin(2 * np.pi * 1 / 24. * n_arr) + 1.) * sw_amp) * np.exp(n_arr / (max(n_arr)))  # W/m2

# Long-wave radiation
lw_amp = 75.  # amplitude of the long-wave signal
lw_offset = - (2 * np.pi * 3. / 24.)  # offset of the daily LW maximum wrt the SW maximum
lw_mean = 275.  # LW minimum in W/m2
lw_down = (np.sin(2 * np.pi * 1 / 24. * n_arr + lw_offset) * lw_amp) + lw_mean  # W/m2

sca_sw_down = np.zeros_like(time_arr, dtype=float)

wind = np.zeros_like(time_arr, dtype=float)
wind += 2.0  # m/s

wind_dir = np.zeros_like(time_arr, dtype=float)

co2_air = np.zeros_like(time_arr, dtype=float)

cnc = CrocusForcing(opt_param=['Wind_DIR', 'CO2air'])  # init Crocus forcing file

# Set some properties
cnc.forc_time_step_v[:] = dt.seconds
# cnc.aspect_v[:] = 0.0
cnc.uref_v[:] = 10.0
cnc.zref_v[:] = 2.0
cnc.zs_v[:] = 1000.0
cnc.lat_v[:] = 60.0
cnc.lon_v[:] = 10.0

# TODO: use date2num to get the time right
cnc.time_v[:] = time_v
cnc.time_v.units = t_units

# Set the created forcing parameters

# PTH
cnc.q_air_v[:, 0] = q_air[:]
cnc.tair_v[:, 0] = tair[:]
cnc.ps_surf_v[:, 0] = p_surf[:]
# Precip
cnc.rain_fall_v[:, 0] = rainf[:]
cnc.snow_fall_v[:, 0] = snowf[:]
# Radiation
cnc.dir_sw_down_v[:, 0] = dir_sw_down[:]
cnc.sca_sw_down_v[:, 0] = sca_sw_down[:]
cnc.lw_down_v[:, 0] = lw_down[:]
# Wind
cnc.wind_v[:, 0] = wind[:]
cnc.wind_dir_v[:, 0] = wind_dir[:]
# Others
cnc.co2_air_v[:, 0] = co2_air

cnc.create_options_nam()
cnc.close()
