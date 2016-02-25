#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr

#------------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

#------------------------------

src = 'SxrEndstation.0:DualAndor.0' # or alias='andorDual'

# (2,512,512)
#dsname = 'exp=sxrk4816:run=7'
dsname = '/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc'

if ntest == 2 :
    # (2,2048,2048)
    #dsname = 'exp=sxrk4816:run=3'
    dsname = '/reg/g/psdm/detector/data_test/types/0005-SxrEndstation.0-DualAndor.0.xtc'

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')

ds  = psana.DataSource(dsname)
env = ds.env()
nrun = ds.runs().next().run()

print 'Example for\n  dataset: %s\n  source : %s\n  run number : %d\n  calib dir : %s'%\
      (dsname, src, nrun, env.calibDir())

#------------------------------

det = psana.Detector(src, env)

print_ndarr(det.pedestals(nrun), '%s\npedestals' % (80*'_'))
print 80*'_'

i, evt, nda = 0, None, None

for i, evt in enumerate(ds.events()) :
    #nda = det.raw(evt)
    nda = det.calib(evt)
    if nda is not None :
        for key in evt.keys() : print key
        print 'Detector data found in the event # %d' % i
        break

print_ndarr(nda, 'nda')

if nda is None :
    print 'Detector data IS NOT FOUND in %d events' % i
    sys.exit('FURTHER TEST IS TERMINATED')

#------------------------------
#print 'env.experiment(): ', env.experiment()
#print 'env.instrument(): ', env.instrument()

fname = 'nda-andor3d-%s-r%04d-%s.txt' % (env.experiment(), nrun, src.replace(":","-").replace(".","-"))
det.save_txtnda(fname, nda, verbos=True)

img = det.image(evt, nda)
print_ndarr(img, '%s\nimage (calibrated data or raw)' % (80*'_') )

#------------------------------
import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms), figsize=(16,7), window=(0.05,  0.05, 0.94, 0.92))
gg.show()

#------------------------------

sys.exit('End of test.')

#------------------------------
