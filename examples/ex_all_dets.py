#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.PyDetector import PyDetector

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

dsname, src                 = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
if   ntest==2 : dsname, src = 'exp=meca1113:run=376', psana.Source('DetInfo(MecTargetChamber.0:Cspad2x2.1)')
elif ntest==3 : dsname, src = 'exp=amob5114:run=403', psana.Source('DetInfo(Camp.0:pnCCD.0)')
elif ntest==4 : dsname, src = 'exp=xppi0614:run=74',  psana.Source('DetInfo(NoDetector.0:Epix100a.0)')
elif ntest==5 : dsname, src = 'exp=sxrg3715:run=46',  psana.Source('DetInfo(SxrEndstation.0:Andor.2)')
elif ntest==6 : dsname, src = 'exp=sxrf9414:run=72',  psana.Source('DetInfo(SxrEndstation.0:Fccd960.0)')
elif ntest==7 : dsname, src = 'exp=xcsi0112:run=15',  psana.Source('DetInfo(XcsBeamline.0:Princeton.0)')
elif ntest==8 : dsname, src = 'exp=amo42112:run=120', psana.Source('DetInfo(AmoBPS.0:Opal1000.0)')
elif ntest==9 : dsname, src = 'exp=cxib2313:run=46',  psana.Source('DetInfo(CxiDg2.0:Tm6740.0)')
#elif ntest==10 : dsname, src = '',  psana.Source('DetInfo()')

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Non-standard calib directory
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()

#for key in evt.keys() : print key

##-----------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s\n%s: %s' % (80*'_', name, nda)
    else           : print '%s\n%s: \n%s...\n shape:%s  size:%d  dtype:%s' % \
         (80*'_', name, nda.flatten()[first:last], str(nda.shape), nda.size, nda.dtype)

##-----------------------------

det = PyDetector(src, env, pbits=0)

ins = det.instrument()

print 80*'_', '\nInstrument: ', ins
#det.set_print_bits(511);
#det.set_def_value(-5.);
#det.set_mode(1);
#det.set_do_offset(True); # works for ex. Opal1000
det.print_attributes()

shape_nda = det.shape(evt)
print_ndarr(shape_nda, 'shape of ndarray')

print 'size of ndarray: %d' % det.size(evt)
print 'ndim of ndarray: %d' % det.ndim(evt)

peds = det.pedestals(evt)
print_ndarr(peds, 'pedestals')

rms = det.rms(evt)
print_ndarr(rms, 'rms')

mask = det.mask(evt)
print_ndarr(mask, 'mask')

gain = det.gain(evt)
print_ndarr(gain, 'gain')

bkgd = det.bkgd(evt)
print_ndarr(bkgd, 'bkgd')

status = det.status(evt)
print_ndarr(status, 'status')

status_mask = det.status_as_mask(evt)
print_ndarr(status_mask, 'status_mask')

cmod = det.common_mode(evt)
print_ndarr(cmod, 'common_mod')

t0_sec = time()
nda_raw = det.raw(evt)
print '%s\n **** consumed time to get raw data = %f sec' % (80*'_', time()-t0_sec)

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

data_sub_peds = nda_raw - peds if peds is not None else nda_raw
print_ndarr(data_sub_peds, 'data - peds')

nda_cdata = det.calib(evt)
print_ndarr(nda_cdata, 'calibrated data')

coords_x = det.coords_x(evt)
print_ndarr(coords_x, 'coords_x')

areas = det.areas(evt)
print_ndarr(areas, 'area')

mask_geo = det.mask_geo(evt)
print_ndarr(mask_geo, 'mask_geo')

pixel_size = det.pixel_size(evt)
print '%s\npixel size: %s' % (80*'_', str(pixel_size))

##-----------------------------

#img_arr = data_sub_peds
img_arr = nda_cdata 
img = None

# Image producer is different for 3-d and 2-d arrays 
if len(nda_raw.shape) > 2 :
    img = det.image(evt)
    #img = det.image(evt, img_arr)
else :
    img = img_arr
    img.shape = nda_raw.shape

print_ndarr(img, 'Image data-peds')

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
