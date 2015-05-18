#!/usr/bin/env python

import sys
#from psana import *
import psana

#from Detector.DetPyAccess import DetPyAccess
import Detector.DetPyAccess
#from Detector import DetPyAccess

ds  = psana.DataSource('exp=cxif5315:run=169')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')


#for key in env.keys() : print key


for key in evt.keys() : print key

#d = evt.get(psana.CsPad.DataV2, src)
#print 'd.TypeId: ', d.TypeId
#q0 = d.quads(0)
#q0_data = q0.data()
#print 'q0_data.shape: ', q0_data.shape


det = Detector.DetPyAccess(src)











#det = Detector.DetectorAccess(src,0) # , 0xffff)
# src)

#print evt.keys()

#peds = det.pedestals(evt,env)
#print '\npedestals:\n', peds[0:20]

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

#print '\nInstrument: ', det.inst(env)


#det.set_print_bits(255);
#det.set_def_value(-5.);
#det.set_mode(1);
#raw_data = det.data_int16_3(evt,env)
#print '\nRaw data:\n', raw_data
#print '\nRaw data shape:\n', raw_data.shape

sys.exit(0)
