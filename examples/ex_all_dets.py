#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

dsname, src                  = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
if   ntest==2  : dsname, src = 'exp=meca1113:run=376', 'MecTargetChamber.0:Cspad2x2.1'
elif ntest==3  : dsname, src = 'exp=amob5114:run=403', 'Camp.0:pnCCD.0'
elif ntest==4  : dsname, src = 'exp=xppi0614:run=74',  'NoDetector.0:Epix100a.0'
elif ntest==5  : dsname, src = 'exp=sxrg3715:run=46',  'SxrEndstation.0:Andor.2'
elif ntest==6  : dsname, src = 'exp=sxrf9414:run=72',  'SxrEndstation.0:Fccd960.0'
elif ntest==7  : dsname, src = 'exp=xcsi0112:run=15',  'XcsBeamline.0:Princeton.0'
elif ntest==8  : dsname, src = 'exp=amo42112:run=120', 'AmoBPS.0:Opal1000.0'
elif ntest==9  : dsname, src = 'exp=cxib2313:run=46',  'CxiDg2.0:Tm6740.0'
elif ntest==10 : dsname, src = 'exp=amo86615:run=4',   'Camp.0:pnCCD.0'
elif ntest==11 : dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0' # NO Detinfo
elif ntest==12 : dsname, src = 'exp=cxif5315:run=169', 'DsaCsPad'  # alias
elif ntest==13 : dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0' # string
elif ntest==14 : dsname, src = 'exp=cxif5315:run=169', 'DsaCsPad' # string of alias
elif ntest==15 : dsname, src = 'exp=cxii8715:run=14',  'CxiEndstation.0:Quartz4A150.0' # alias='Sc1Questar'
elif ntest==16 : dsname, src = 'exp=xppc0115:run=305', 'XppEndstation.0:Rayonix.0' # alias='rayonix'
elif ntest==17 : dsname, src = 'exp=amoj5415:run=49',  'pnccdFront'

elif ntest==18 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0002-MecTargetChamber.0-Cspad.0-two-quads.xtc',  'MecTargetChamber.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')

elif ntest==19 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc',  'MecTargetChamber.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')

elif ntest==20 :   #The same as 'exp=cxif5315:run=169' but geometry is different
    dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'CxiDs2.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib/')

print 'Example for\n dataset: %s\n source : %s' % (dsname, src)

#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()

for key in evt.keys() : print key

##-----------------------------

par = nrun # evt or nrun
det = psana.Detector(src, env)

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

#det.set_print_bits(511)
#det.set_def_value(-5.)
#det.set_mode(1)
#det.set_do_offset(True) # works for ex. Opal1000
det.print_attributes()

shape_nda = det.shape(par)
print_ndarr(shape_nda, 'shape of ndarray')

print 'size of ndarray: %d' % det.size(par)
print 'ndim of ndarray: %d' % det.ndim(par)

peds = det.pedestals(par)
print_ndarr(peds, 'pedestals')

rms = det.rms(par)
print_ndarr(rms, 'rms')

mask = det.mask(par)
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

t0_sec = time()
nda_raw = det.raw(evt)
print_ndarr(nda_raw, 'nda_raw')
print 'Consumed time for det.raw(evt) = %7.3f sec' % (time()-t0_sec)

i=0
if nda_raw is None :
    for i, evt in enumerate(ds.events()) :
        nda_raw = det.raw(evt)
        if nda_raw is not None :
            print 'Detector data found in event %d' % i
            break

print_ndarr(nda_raw, 'raw data')

if nda_raw is None :
    print 'Detector data IS NOT FOUND in %d events' % i
    sys.exit('FURTHER TEST IS TERMINATED')

##-----------------------------

if peds is not None and nda_raw is not None : peds.shape = nda_raw.shape 

data_sub_peds = nda_raw - peds if peds is not None else nda_raw
print_ndarr(data_sub_peds, 'data - peds')

nda_cdata = det.calib(evt)
print_ndarr(nda_cdata, 'calibrated data')

t0_sec = time()
nda_cdata_ub = det.calib(evt) # , cmpars=(5,50))
print_ndarr(nda_cdata_ub, 'calibrated data for cspad unbond pixels')
print 'Consumed time for det.calib(evt) = %7.3f sec' % (time()-t0_sec)

coords_x = det.coords_x(par)
print_ndarr(coords_x, 'coords_x')

areas = det.areas(par)
print_ndarr(areas, 'area')

mask_geo = det.mask_geo(par)
print_ndarr(mask_geo, 'mask_geo')

#mask_geo.shape = (32,185,388)
#print mask_geo


pixel_size = det.pixel_size(par)
print '%s\npixel size: %s' % (80*'_', str(pixel_size))

##-----------------------------

img_arr = data_sub_peds
#img_arr = nda_cdata if nda_cdata is not None else nda_raw
img = None

# Image producer is different for 3-d and 2-d arrays 
if len(nda_raw.shape) > 2 :
    #img = det.image(evt)
    
    t0_sec = time()
    img = det(evt) # alias for det.image(evt) implemented in __call__
    #img = det.image(evt, img_arr)
    print 'Consumed time for det.image(evt) = %7.3f sec (for 1st event!)' % (time()-t0_sec)
else :
    img = img_arr
    img.shape = nda_raw.shape

print_ndarr(img, 'image (calibrated data or raw)')

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
