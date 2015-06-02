#!/usr/bin/env python

import sys
import psana
import Detector

# psana -m EventKeys -n 5 exp=mecb3114:run=17
# psana -m EventKeys -n 5 exp=sxrg3715:run=46
# psana -m EventKeys -n 5 exp=sxrb6813:run=52

ds, src  = psana.DataSource('exp=sxrb6813:run=52'), psana.Source('DetInfo(SxrEndstation.0:Andor.0)')
#ds, src = psana.DataSource('exp=sxrg3715:run=46'), psana.Source('DetInfo(SxrEndstation.0:Andor.2)')
#ds, src  = psana.DataSource('exp=mecb3114:run=17'), psana.Source('DetInfo(MecTargetChamber.0:Andor.1)')
#ds, src  = psana.DataSource('exp=sxrb6813:run=52'), psana.Source('DetInfo(MecTargetChamber.0:Andor.1)')

evt = ds.events().next()
env = ds.env()

det = Detector.DetectorAccess(src,0) # , 0xffff)

det.set_print_bits(511);

#print evt.keys()
print 80*'_'

#peds = det.pedestals(evt,env)
#print 80*'_', '\npedestals:\n', peds[0:20]

#peds = det.pedestals(evt,env)
#print 80*'_', '\npedestals:\n', peds[0:20]

prms = det.pixel_rms(evt,env)
print 80*'_', '\npixel_rms:\n', prms[0:20]

pgain = det.pixel_gain(evt,env)
print 80*'_', '\npixel_gain:\n', pgain[0:20]

pmask = det.pixel_mask(evt,env)
print 80*'_', '\npixel_mask:\n', pmask[0:20]

pbkgd = det.pixel_bkgd(evt,env)
print 80*'_', '\npixel_bkgd:\n', pbkgd[0:20]

pstat = det.pixel_status(evt,env)
print 80*'_', '\npixel_status:\n', pstat[0:20]

pcmod = det.common_mode(evt,env)
print 80*'_', '\ncommon_mode:\n', pcmod

print 80*'_', '\nInstrument: ', det.instrument(env)
print 80*'_'

#det.set_print_bits(255);
#det.print_members()
#det.print_config(evt,env)

raw_data = det.data_uint16_2(evt,env)
print '\nRaw data:\n', raw_data
print '\nRaw data shape: ', raw_data.shape
print '\nRaw data type: ', raw_data.dtype

sys.exit(0)
