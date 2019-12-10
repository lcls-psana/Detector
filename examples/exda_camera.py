#!/usr/bin/env python

from __future__ import print_function
import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

# psana -m EventKeys -n 5 exp=sxrf9414:run=72

ds  = psana.DataSource('exp=sxrf9414:run=72')
evt = next(ds.events())
env = ds.env()
rnum = evt.run()

src = psana.Source('DetInfo(SxrEndstation.0:Fccd960.0)')
det = Detector.DetectorAccess(src, env, 0) # , 0xffff)

##-----------------------------
t0_sec = time()
print('\nInstrument: ', det.instrument(env))
print_ndarr(det.pedestals(evt,env),    'pedestals(evt,env)')
print_ndarr(det.pedestals_v0(rnum),    'pedestals_v0(rnum)')
print_ndarr(det.pixel_rms(evt,env),    'pixel_rms(evt,env)')
print_ndarr(det.pixel_gain(evt,env),   'pixel_gain(evt,env)')
print_ndarr(det.pixel_mask(evt,env),   'pixel_mask(evt,env)')
print_ndarr(det.pixel_bkgd(evt,env),   'pixel_bkgd(evt,env)')
print_ndarr(det.pixel_status(evt,env), 'pixel_status(evt,env)')
print_ndarr(det.common_mode(evt,env),  'common_mode(evt,env)')
print_ndarr(det.common_mode_v0(rnum),  'common_mode_v0(rnum)')
##-----------------------------

raw_data = det.data_uint16_2(evt,env)
print_ndarr(raw_data, 'raw_data')

det.print_config(evt,env)

print('Consumed time = %7.6f sec' % (time()-t0_sec))

sys.exit(0)
##-----------------------------
