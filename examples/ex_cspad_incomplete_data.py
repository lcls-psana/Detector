#!/usr/bin/env python
##-----------------------------

import sys
import psana

from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

#dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
#dsname, src ='/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc', 'CxiDs2.0:Cspad.0'
#psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

#dsname, src = 'exp=cxid9114:run=96', 'CxiDs2.0:Cspad.0'
#dsname, src ='/reg/g/psdm/detector/data_test/types/0001-CxiDs2.0-Cspad.0-config-gain-mask.xtc', 'CxiDs2.0:Cspad.0'
#psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

#dsname, src = 'exp=mecj5515:run=16', 'MecTargetChamber.0:Cspad.0'
#dsname, src = '/reg/g/psdm/detector/data_test/types/0002-MecTargetChamber.0-Cspad.0-two-quads.xtc', 'MecTargetChamber.0:Cspad.0'
dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc', 'MecTargetChamber.0:Cspad.0'
psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')

ds  = psana.DataSource(dsname)
env = ds.env()

#evt = ds.events().next()
#rnum = evt.run()
#calibdir = env.calibDir()

det = psana.Detector(src, env)
#det.set_print_bits(8)

#print ds.events().next().keys()

##-----------------------------

t0_sec = time()

nda=None
for i, evt in enumerate(ds.events()) :
    nda = det.raw(evt)
    if nda is not None :
        print 'Detector data found in event %d' % i
        break

rnum = evt.run()

print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(nda, 'raw')

if nda is None :
    sys.exit('Exit: DO NOT plot anything for nda=None...')

img = det.image(rnum, nda)

import pyimgalgos.GlobalGraphics as gg
ave, rms = nda.mean(), nda.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
