#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana
#import Detector
from Detector.PyDetectorAccess import PyDetectorAccess
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

ds  = psana.DataSource('exp=sxrg3715:run=119')
#ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0013-SxrEndstation.0-Andor.0.xtc') # exp=sxrb6813:run=34
evt = ds.events().next()
env = ds.env()
rnum = evt.run()
calibdir = env.calibDir()

src = psana.Source('DetInfo(SxrEndstation.0:Andor.1)')
#src = psana.Source('DetInfo(SxrEndstation.0:Andor.0)')
pda = PyDetectorAccess(src, env, pbits=0)

#print evt.keys()

##-----------------------------
t0_sec = time()
print_ndarr(pda.pedestals(rnum),    'pedestals(rnum)')
print('Consumed time = %7.3f sec' % (time()-t0_sec))
print_ndarr(pda.pixel_rms(rnum),    'pixel_rms(rnum)')
print_ndarr(pda.pixel_gain(rnum),   'pixel_gain(rnum)')
print_ndarr(pda.pixel_mask(rnum),   'pixel_mask(rnum)')
print_ndarr(pda.pixel_bkgd(rnum),   'pixel_bkgd(rnum)')
print_ndarr(pda.pixel_status(rnum), 'pixel_status(rnum)')
print_ndarr(pda.common_mode(rnum),  'common_mode(rnum)')

##-----------------------------

print('ndim  = %d' % pda.ndim(rnum))
print('size  = %d' % pda.size(rnum))
print('shape = %s' % str(pda.shape(rnum)))

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
