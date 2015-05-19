#!/usr/bin/env python

import sys
import psana
import Detector

# psana -m EventKeys -n 5 exp=xppi0614:run=74

ds  = psana.DataSource('exp=xppi0614:run=74')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DetInfo(NoDetector.0:Epix100a.0)')

det = Detector.DetectorAccess(src,0) # , 0xffff)

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
det.print_members()
det.print_config(evt,env)

raw_data = det.data_uint16_2(evt,env)
print '\nRaw data:\n', raw_data
print '\nRaw data shape: ', raw_data.shape
print '\nRaw data type: ', raw_data.dtype


#import numpy as np
#np.save('img-test-epix.npy', raw_data)

sys.exit(0)
