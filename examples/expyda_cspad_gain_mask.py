#!/usr/bin/env python
##-----------------------------

import sys
import psana

from Detector.PyDetectorAccess import PyDetectorAccess
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')
ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/cspad-gain-map.xtc')

#ds = psana.DataSource('exp=cxid9114:run=96')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()
calibdir = env.calibDir()

src = psana.Source('CxiDs2.0:Cspad.0')
pda = PyDetectorAccess(src, env, pbits=0)

#print evt.keys()

##-----------------------------

t0_sec = time()
gm = pda.cspad_gain_mask()  # gain=6.87526
print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(gm, 'cspad_gain_map')

img = pda.image(rnum, gm)

import pyimgalgos.GlobalGraphics as gg
ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
