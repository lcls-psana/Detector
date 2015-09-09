#!/usr/bin/env python

import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr
from time import time
##-----------------------------

# psana -m EventKeys -n 5 exp=mecb3114:run=17
# psana -m EventKeys -n 5 exp=sxrg3715:run=46
# psana -m EventKeys -n 5 exp=sxrb6813:run=52

ds, src  = psana.DataSource('exp=sxrb6813:run=52'), psana.Source('DetInfo(SxrEndstation.0:Andor.0)')
#ds, src = psana.DataSource('exp=sxrg3715:run=46'), psana.Source('DetInfo(SxrEndstation.0:Andor.2)')
#ds, src  = psana.DataSource('exp=mecb3114:run=17'), psana.Source('DetInfo(MecTargetChamber.0:Andor.1)')
#ds, src  = psana.DataSource('exp=sxrb6813:run=52'), psana.Source('DetInfo(MecTargetChamber.0:Andor.1)')

evt = ds.events().next()
env = ds.env()
rnum = evt.run()

det = Detector.DetectorAccess(src, env, 0) # , 0xffff)
det.set_print_bits(511);

#print evt.keys()
print 80*'_'

##-----------------------------
print '\nInstrument: ', det.instrument(env)
print_ndarr(det.pedestals(evt,env),    'pedestals(evt,env)')
print_ndarr(det.pedestals_v0(rnum),    'pedestals_v0(rnum)')
print_ndarr(det.pixel_rms(evt,env),    'pixel_rms(evt,env)')
print_ndarr(det.pixel_gain(evt,env),   'pixel_gain(evt,env)')
print_ndarr(det.pixel_mask(evt,env),   'pixel_mask(evt,env)')
print_ndarr(det.pixel_bkgd(evt,env),   'pixel_bkgd(evt,env)')
print_ndarr(det.pixel_status(evt,env), 'pixel_status(evt,env)')
t0_sec = time()
print_ndarr(det.common_mode(evt,env),  'common_mode(evt,env)')
print 'Consumed time = %7.6f sec' % (time()-t0_sec)
t0_sec = time()
print_ndarr(det.common_mode_v0(rnum),  'common_mode_v0(rnum)')
print 'Consumed time = %7.6f sec' % (time()-t0_sec)
##-----------------------------

raw_data = det.data_uint16_2(evt,env)
print_ndarr(raw_data, 'raw_data')

sys.exit(0)

##-----------------------------
