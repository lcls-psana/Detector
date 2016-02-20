#!/usr/bin/env python

import sys
import psana
from time import time
import pyimgalgos.GlobalGraphics as gg
from Detector.GlobalUtils import print_ndarr

##-----------------------------
psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')
ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc') # exp=sxrk4816:run=7
#ds  = psana.DataSource('exp=sxrk4816:run=7')
env = ds.env()

#nrun = ds.runs().next()
#evt = ds.events().next()
#nrun = evt.run()

##-----------------------------

from Detector.AreaDetector import AreaDetector
det = AreaDetector('SxrEndstation.0:DualAndor.0', env, pbits=4) # or alias='andorDual'
#det = psana.Detector('SxrEndstation.0:DualAndor.0', env) # or alias='andorDual'

img=None
for i, evt in enumerate(ds.events()) :
    #img = det.image(evt)
    img = det.raw(evt)
    #img = det.calib(evt)
    if img is not None :
        print 'Detector data found in event %d' % i
        break
counter=i

if img is None :
    print 'Detector data IS NOT FOUND in %d events' % counter
    sys.exit('FURTHER TEST IS TERMINATED')

print_ndarr(img, 'andor3d raw')

##-----------------------------

if False :
    ave, rms = img.mean(), img.std()
    gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
    gg.show()

##-----------------------------
