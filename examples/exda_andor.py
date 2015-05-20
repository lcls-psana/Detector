#!/usr/bin/env python

import sys
import psana
import Detector

# psana -m EventKeys -n 5 exp=mecb3114:run=17
# psana -m EventKeys -n 5 exp=sxrg3715:run=46

ds, src = psana.DataSource('exp=sxrg3715:run=46'), psana.Source('DetInfo(SxrEndstation.0:Andor.2)')
#ds, src  = DataSource('exp=mecb3114:run=17'), Source('DetInfo(MecTargetChamber.0:Andor.1)')
evt = ds.events().next()
env = ds.env()

det = Detector.DetectorAccess(src,0) # , 0xffff)

det.set_print_bits(511);

#print evt.keys()

peds = det.pedestals(evt,env)
print '\npedestals:\n', peds[0:20]

#prms = det.pixel_rms(evt,env)
#print '\npixel_rms:\n', prms[0:20]

#pgain = det.pixel_gain(evt,env)
#print '\npixel_gain:\n', pgain[0:20]

#pmask = det.pixel_mask(evt,env)
#print '\npixel_mask:\n', pmask[0:20]

#pbkgd = det.pixel_bkgd(evt,env)
#print '\npixel_bkgd:\n', pbkgd[0:20]

#pstat = det.pixel_status(evt,env)
#print '\npixel_status:\n', pstat[0:20]

#pcmod = det.common_mode(evt,env)
#print '\ncommon_mode:\n', pcmod

print '\nInstrument: ', det.inst(env)

#det.set_print_bits(255);
#det.print_members()
#det.print_config(evt,env)

raw_data = det.data_uint16_2(evt,env)
print '\nRaw data:\n', raw_data
print '\nRaw data shape: ', raw_data.shape
print '\nRaw data type: ', raw_data.dtype

sys.exit(0)
