#!/usr/bin/env python
"""
Test method det.ndarray_from_image(rnum, image):

1. get cspad n-d array of mask with shape:(32, 185, 388)
2. create image from n-d array of mask with shape:(1731, 1738)
3. convert image back to n-d array using method det.ndarray_from_image
4. compare initial and final n-d arrays
"""

import sys
import psana
from time import time
from Detector.AreaDetector import AreaDetector
from pyimgalgos.GlobalUtils import print_ndarr, table_from_cspad_ndarr, cspad_ndarr_from_table
#from Detector.GlobalUtils import print_ndarr, table_from_cspad_ndarr, cspad_ndarr_from_table

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
det.print_attributes()
mask = det.mask(evt, calib=True, status=True, edges=True, central=True, unbond=True, unbondnbrs=True) #, unbondnbrs8=True)
print_ndarr(mask, 'input n-d array of mask')

##-----------------------------

image = det.image(evt, mask)
print_ndarr(image, 'image from mask n-d array')

##-----------------------------

t0_sec = time()
nda = det.ndarray_from_image(rnum, image)
print 'det.ndarray_from_image consumed time %.6f sec' % (time()-t0_sec)
print_ndarr(nda, 'n-d array of mask retreived from image')

##-----------------------------

t0_sec = time()
tmask0 = table_from_cspad_ndarr(mask)
print 'table creation time %.6f sec' % (time()-t0_sec)
tmask1 = table_from_cspad_ndarr(nda)
print_ndarr(tmask0, 'table  of mask0')

##-----------------------------

t0_sec = time()
nda_cspad = cspad_ndarr_from_table(tmask0)
print_ndarr(nda_cspad, 'cspad_ndarr_from_table')
print 'cspad_ndarr_from_table consumed time %.6f sec' % (time()-t0_sec)
nda_cspad.shape = (32*185,388)

##-----------------------------

import pyimgalgos.GlobalGraphics as gg

#img = image
#ave, rms = img.mean(), img.std()
#d = (ave-1*rms, ave+2*rms)
d = (-1,2)
gg.plotImageLarge(tmask0, amp_range=d, title='input n-d array of mask')
gg.plotImageLarge(tmask1, amp_range=d, title='n-d array of mask retreived from image')
gg.plotImageLarge(tmask1-tmask1, amp_range=d, title='difference between input and reconstructed from image n-d arrays')
gg.plotImageLarge(nda_cspad, amp_range=d, title='test cspad_ndarr_from_table')

gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
