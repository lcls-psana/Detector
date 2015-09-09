#!/usr/bin/env python

import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

# psana -m EventKeys -n 5 exp=amob5114:run=403

# ds  = psana.DataSource('exp=amob5114:run=403')
ds  = psana.DataSource('exp=amo86615:run=4')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

src = psana.Source('DetInfo(Camp.0:pnCCD.1)')
det = Detector.DetectorAccess(src, env, 0) # , 0xffff)

##-----------------------------

#print evt.keys()

###-----------------------------
print '\nInstrument: ', det.instrument(env)
t0_sec = time()
print_ndarr(det.pedestals(evt,env),    'pedestals(evt,env)')
t0_sec = time()
print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(det.pedestals_v0(rnum),    'pedestals_v0(rnum)')
print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(det.pixel_rms(evt,env),    'pixel_rms(evt,env)')
print_ndarr(det.pixel_rms_v0(rnum),    'pixel_rms_v0(rnum)')
print_ndarr(det.pixel_gain(evt,env),   'pixel_gain(evt,env)')
print_ndarr(det.pixel_gain_v0(rnum),   'pixel_gain_v0(rnum)')
print_ndarr(det.pixel_mask(evt,env),   'pixel_mask(evt,env)')
print_ndarr(det.pixel_mask_v0(rnum),   'pixel_mask_v0(rnum)')
print_ndarr(det.pixel_bkgd(evt,env),   'pixel_bkgd(evt,env)')
print_ndarr(det.pixel_bkgd_v0(rnum),   'pixel_bkgd_v0(rnum)')
print_ndarr(det.pixel_status(evt,env), 'pixel_status(evt,env)')
print_ndarr(det.pixel_status_v0(rnum), 'pixel_status_v0(rnum)')
print_ndarr(det.common_mode(evt,env),  'common_mode(evt,env)')
print_ndarr(det.common_mode_v0(rnum),  'common_mode_v0(rnum)')
##-----------------------------

##-----------------------------
#det.set_print_bits(255);
det.print_members()
det.print_config(evt,env)

raw_data = det.data_uint16_3(evt,env)
print_ndarr(raw_data, 'raw_data')

sys.exit(0)

##-----------------------------
