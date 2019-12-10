#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana

from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')
ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0001-CxiDs2.0-Cspad.0-config-gain-mask.xtc')
#ds  = psana.DataSource('exp=cxid9114:run=96')

env = ds.env()
evt = ds.events().next()
rnum = evt.run()
#calibdir = env.calibDir()

det = psana.Detector('CxiDs2.0:Cspad.0', env)

#print evt.keys()

##-----------------------------

gm=None

for i, evt in enumerate(ds.events()) :

  t0_sec = time()
  #gm = det.gain_mask()
  #gm = det.gain_mask(gain=8)
  #gm = det.raw(evt)
  gm = det.calib(evt)
  print('Event: %d  consumed time = %7.3f sec' % (i, time()-t0_sec))
  print_ndarr(gm, 'gain_map')
  if gm is not None : break

img = det.image(rnum, gm)

import pyimgalgos.GlobalGraphics as gg
ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
