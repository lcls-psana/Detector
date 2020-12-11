#!/usr/bin/env python

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d : %(message)s', level=logging.INFO) # INFO) #DEBUG

import sys
import psana
import numpy as np
from time import time
from Detector.AreaDetector import AreaDetector
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 2
print('Test # %d' % ntest)

##-----------------------------
dsname, src = None, None

if ntest==1 :
    #dsname, src = '/reg/d/psdm/det/detdaq18/xtc/detdaq18-r0023-s00-c00.xtc', 'DetLab.0:Epix10ka2M.0'
    dsname, src = 'exp=detdaq18:run=23', 'DetLab.0:Epix10ka2M.0'
    psana.setOption('psana.calib-dir', '/reg/d/psdm/det/detdaq18/calib')

elif ntest==2 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0007-NoDetector.0-Epix100a.0.xtc', 'NoDetector.0:Epix100a.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/epix100/xpp-epix100a-2014-12-04/calib')

elif ntest==3 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0020-XppGon.0-Epix100a.1.xtc', 'XppGon.0:Epix100a.1'
    psana.setOption('psana.calib-dir', '/reg/d/psdm/XPP/xppn4116/calib')
    #psana.setOption('psana.calib-dir', './calib')
    #dsname, src = 'exp=xppn4116:run=137', 'XppGon.0:Epix100a.1'

elif ntest==4 :
    #dsname, src = 'exp=xpplv3818:run=88', 'XppGon.0:Epix10ka2M.0'
    #dsname, src = 'exp=xpplv3818:run=160', 'XppGon.0:Epix10ka2M.0'
    dsname, src = 'exp=xpplv3818:run=170', 'XppGon.0:Epix10ka2M.0'
    #dsname, src = '/reg/d/psdm/xpp/xpplv3818/xtc/xpplv3818-r0088-s00-c00.xtc', 'XppGon.0:Epix10ka2M.0'
    psana.setOption('psana.calib-dir', '/reg/d/psdm/XPP/xpplv3818/calib')

print('Example for\n dataset: %s\n source : %s' % (dsname, src))

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()
print('Run number %d' % nrun)
print('calib directory: %s' % env.calibDir())

for key in evt.keys() : print(key)

##-----------------------------

par = nrun # evt or nrun
#det = psana.Detector(src, env)
#det = AreaDetector(src, env, pbits=0177777)
det = AreaDetector(src, env, pbits=0)

ins = det.instrument()
print(80*'_', '\nInstrument: ', ins)

det.print_attributes()

shape_nda = det.shape(par)
print_ndarr(shape_nda, 'shape of ndarray')

print('size of ndarray: %d' % det.size(par))
print('ndim of ndarray: %d' % det.ndim(par))

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
        print('Detector data found in event %d'\
              ' consumed time for det.raw(evt) = %7.3f sec' % (i, time()-t0_sec))
        if i==8 : break

print_ndarr(nda_raw, 'raw data')

if nda_raw is None :
    print('Detector data IS NOT FOUND in %d events' % i)
    sys.exit('FURTHER TEST IS TERMINATED')

##-----------------------------

#if peds is not None and nda_raw is not None : peds.shape = nda_raw.shape 
#data_sub_peds = nda_raw - peds if peds is not None else nda_raw

print_ndarr(peds, 'peds')
print_ndarr(nda_raw, 'raw')

#cmpars=None        # cm pars from calib directory
#cmpars=(0, 0, 100) # use cmpars, do not apply cm correction
cmpars=(0, 2, 100) # use cmpars, apply correction in columns

nda_cdata = det.calib(evt, cmpars=cmpars)  # cm pars from calib directory

print_ndarr(nda_cdata, 'calibrated data')

##-----------------------------
#sys.exit('TEST EXIT')
##-----------------------------

#img = nda_raw
#img = data_sub_peds
nda = nda_cdata if nda_cdata is not None else nda_raw

print_ndarr(nda, 'nda')
#img = nda[0,:] if nda.ndim>2 else nda
#img = nda_cdata[0,:]

img = det.image(evt,nda)

#img.shape = nda_raw.shape

print_ndarr(img, 'image (calibrated data or raw)')

print(80*'_')

##-----------------------------

if img is None :
    sys.exit('Image is not available. FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

med = np.median(nda)
spr = np.median(np.abs(nda-med))
print('median, spread:', med, spr)
amp_range=(med-3*spr, med+3*spr)
#ave, rms = img.mean(), img.std()
#print 'ave=%.3f rms=%.3f' % (ave, rms)
#amp_range=(ave-1*rms, ave+2*rms)
#amp_range=(-10, 25)
#amp_range=(-5, 5)
   
gg.plotImageLarge(img, amp_range=amp_range, cmap='jet')

scmpars = str(None if cmpars is None else cmpars[1])
#fname = 'img-%s-%s-cmpars-%s.png' % (dsname.replace('=','-').replace(':','-'), src.replace(':','-').replace('.','-'), cmpars[1])
fname = 'img.png'
gg.save(fname=fname, do_save=True, pbits=0377)

gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
