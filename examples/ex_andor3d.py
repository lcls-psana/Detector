#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr
from PSCalib.GlobalUtils import reshape_nda_to_2d

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------
#dsname = 'exp=sxrk4816:run=1'
dsname = '/reg/g/psdm/detector/data_test/types/0005-SxrEndstation.0-DualAndor.0.xtc' # exp=sxrk4816:run=1
src = 'SxrEndstation.0:DualAndor.0' # or alias='andorDual'

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')

ds  = psana.DataSource(dsname)
env = ds.env()
nrun = ds.runs().next()

#evt = ds.events().next()
#nrun = evt.run()

##-----------------------------
from Detector.AreaDetector import AreaDetector

det = AreaDetector(src, env, pbits=0, iface='P') # iface='P' or 'C'

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

nda=None
i=0
for i, evt in enumerate(ds.events()) :
    #for key in evt.keys() : print key
    nda = det.image(evt)
    #nda = det.raw(evt)
    if nda is not None :
        print 'Detector data found in event %d' % i
        break

print_ndarr(nda, 'nda')

if nda is None :
    print 'Detector data IS NOT FOUND in %d events' % i
    sys.exit('FURTHER TEST IS TERMINATED')

##-----------------------------

img = nda if len(nda.shape)==2 else reshape_nda_to_2d(nda)
print_ndarr(img, '%s  image (calibrated data or raw)' % (80*'_') )

##-----------------------------
import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
