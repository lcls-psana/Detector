#!/usr/bin/env python
##-----------------------------

import sys
import psana

from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

#ds  = psana.DataSource('exp=cx/reg/g/psdm/detector/data_test/types/cspad-gain-map.xtc@')
ds  = psana.DataSource('exp=cxid9114:run=96')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()
calibdir = env.calibDir()

det = psana.Detector('CxiDs2.0:Cspad.0', env)

#print evt.keys()

##-----------------------------

t0_sec = time()
gm = det.gain_map() #gain=6.87526)
print_ndarr(gm, 'gain_map')
print 'Consumed time = %7.3f sec' % (time()-t0_sec)

img = det.image(rnum, gm)

import pyimgalgos.GlobalGraphics as gg
ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
