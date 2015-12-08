#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.AreaDetector import AreaDetector
from Detector.GlobalUtils import print_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
if ntest==2 : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()

#for key in evt.keys() : print key

##-----------------------------

det = AreaDetector(src, env, pbits=0)
det.print_attributes()
mask = det.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True)
print_ndarr(mask, 'mask')

##-----------------------------

img_arr = mask
img = det.image(evt, img_arr)
print_ndarr(img, 'img')
print 80*'_'

##-----------------------------

if img is None :
    print 'Image is not available'
    sys.exit('FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
