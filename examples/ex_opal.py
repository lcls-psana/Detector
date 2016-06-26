#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu
from Detector.AreaDetector import AreaDetector

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------
dsname, src = None, None

#if ntest==4 : #dsname, src = 'exp=sxrm2016:run=40',  'OPAL3'

if ntest==1 :
    dsname, src = 'exp=sxrm2016:run=40',  'OPAL3'
    #psana.setOption('psana.calib-dir', './calib')

print 'Example for\n dataset: %s\n source : %s' % (dsname, src)

#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()
print 'Run number %d' % nrun

for key in evt.keys() : print key

##-----------------------------

par = nrun # evt or nrun
#det = psana.Detector(src, env)
#det = AreaDetector(src, env, pbits=0177777)
det = AreaDetector(src, env, pbits=0)

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

det.print_attributes()

shape_nda = det.shape(par)
print_ndarr(shape_nda, 'shape of ndarray')

print 'size of ndarray: %d' % det.size(par)
print 'ndim of ndarray: %d' % det.ndim(par)

peds = det.pedestals(par)
print_ndarr(peds, 'pedestals')

rms = det.rms(par)
print_ndarr(rms, 'rms')

mask = det.mask(par, calib=False, status=True, edges=False, central=False, unbond=False, unbondnbrs=False)
print_ndarr(mask, 'mask')

gain = det.gain(par)
print_ndarr(gain, 'gain')

bkgd = det.bkgd(par)
print_ndarr(bkgd, 'bkgd')

status = det.status(par)
print_ndarr(status, 'status')

status_mask = det.status_as_mask(par)
print_ndarr(status_mask, 'status_mask')

cmod = det.common_mode(par)
print_ndarr(cmod, 'common_mod')

i=0
nda_raw = None
evt = None
for i, evt in enumerate(ds.events()) :
    t0_sec = time()
    nda_raw = det.raw(evt)
    if nda_raw is not None :
        dt_sec = time()-t0_sec
        print 'Detector data found in event %d'\
              ' consumed time for det.raw(evt) = %7.3f sec' % (i, time()-t0_sec)
        if i==8 : break

print_ndarr(nda_raw, 'raw data')

if nda_raw is None :
    print 'Detector data IS NOT FOUND in %d events' % i
    sys.exit('FURTHER TEST IS TERMINATED')

##-----------------------------

if peds is not None and nda_raw is not None : peds.shape = nda_raw.shape 

data_sub_peds = nda_raw - peds if peds is not None else nda_raw
print_ndarr(data_sub_peds, 'data - peds')

nda_cdata = det.calib(evt, cmpars=(4, 6, 30, 10))
#nda_cdata = det.calib(evt)
print_ndarr(nda_cdata, 'calibrated data')

##-----------------------------
#sys.exit('TEST EXIT')
##-----------------------------

#img = data_sub_peds
#img = nda_cdata if nda_cdata is not None else nda_raw
#img.shape = nda_raw.shape

img = det.image(evt)

print_ndarr(img, 'image (calibrated data or raw)')

print 80*'_'

##-----------------------------

if img is None :
    sys.exit('Image is not available. FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
amp_range=(ave-1*rms, ave+2*rms)
#amp_range=(-10, 25)
gg.plotImageLarge(img, amp_range=amp_range)
gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
