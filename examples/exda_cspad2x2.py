#!/usr/bin/env python

import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr
##-----------------------------

# psana -m EventKeys -n 5 exp=meca1113:run=376

ds  = psana.DataSource('exp=meca1113:run=376')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

src = psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
det = Detector.DetectorAccess(src, env, 0) # , 0xffff)

#print evt.keys()

##-----------------------------
print '\nInstrument: ', det.instrument(env)
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

#det.set_print_bits(255);
det.print_members()
det.print_config(evt,env)

raw_data = det.data_int16_3(evt,env)
print_ndarr(raw_data, 'raw_data')

sys.exit(0)
##-----------------------------
