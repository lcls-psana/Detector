#!/usr/bin/env python

import sys
from psana import *
import Detector

# psana -m EventKeys -n 5 exp=sxrf9414:run=72

ds  = DataSource('exp=sxrf9414:run=72')
evt = ds.events().next()
env = ds.env()

src = Source('DetInfo(SxrEndstation.0:Fccd960.0)')
#src = Source('Camp.0:pnCCD.1')

det = Detector.DetectorAccess(src,0) # , 0xffff)
# src)

#print evt.keys()

peds = det.pedestals(evt,env)
print '\npedestals:\n', peds[0:20]

prms = det.pixel_rms(evt,env)
print '\npixel_rms:\n', prms[0:20]

pgain = det.pixel_gain(evt,env)
print '\npixel_gain:\n', pgain[0:20]

pmask = det.pixel_mask(evt,env)
print '\npixel_mask:\n', pmask[0:20]

pbkgd = det.pixel_bkgd(evt,env)
print '\npixel_bkgd:\n', pbkgd[0:20]

pstat = det.pixel_status(evt,env)
print '\npixel_status:\n', pstat[0:20]

pcmod = det.common_mode(evt,env)
print '\ncommon_mode:\n', pcmod

print '\nInstrument: ', det.inst(env)

#det.set_print_bits(255);
#det.set_mode(1);
#det.print_members()
det.print_config(evt,env)

raw_data = det.data_uint16_2(evt,env)
print '\nRaw data:\n', raw_data
print '\nRaw data shape: ', raw_data.shape
print '\nRaw data type: ', raw_data.dtype

sys.exit(0)
