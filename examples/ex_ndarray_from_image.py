#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.AreaDetector import AreaDetector
from Detector.GlobalUtils import print_ndarr, table_from_cspad_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

#The same as 'exp=cxif5315:run=169'
#dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'CxiDs2.0:Cspad.0'
psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

#for key in evt.keys() : print key

##-----------------------------

det = AreaDetector(src, env, pbits=0)
#det.print_attributes()
mask = det.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True)
print_ndarr(mask, 'input n-d array of mask')

##-----------------------------

image = det.image(evt, mask)
print_ndarr(image, 'image from mask n-d array')

##-----------------------------

nda = det.ndarray_from_image(rnum, image)
print_ndarr(nda, 'n-d array of mask retreived from image')

##-----------------------------

tmask0 = table_from_cspad_ndarr(mask)
tmask1 = table_from_cspad_ndarr(nda)

import pyimgalgos.GlobalGraphics as gg

#img = image
#ave, rms = img.mean(), img.std()
#d = (ave-1*rms, ave+2*rms)
d = (-1,2)
gg.plotImageLarge(tmask0, amp_range=d, title='input n-d array of mask')
gg.plotImageLarge(tmask1, amp_range=d, title='n-d array of mask retreived from image')
gg.plotImageLarge(tmask1-tmask1, amp_range=d, title='difference between input and reconstructed from image n-d arrays')

gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
