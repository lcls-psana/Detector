#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

dsname = '/reg/g/psdm/data_test/types/FCCD_FccdConfigV2.xtc' # sxr61612-r0332
src = 'SxrEndstation.0:Fccd.0' # Camera.FrameV1. Fccd.ConfigV2

if ntest==2 :
    #dsname = '/reg/g/psdm/data_test/types/Timepix_ConfigV3.xtc' # xcsi0113-r0030
    dsname = '/reg/g/psdm/data_test/types/Timepix_DataV2.xtc'    # xcsi0113-r0030
    src = 'XcsEndstation.0:Timepix.0' # Timepix.DataV2 Timepix.ConfigV3

elif ntest==3 :
    dsname = '/reg/g/psdm/data_test/types/Fli_ConfigV1.xtc' # meca6013-r0009
    dsname = '/reg/g/psdm/data_test/types/Fli_FrameV1.xtc'  # meca6013-r0009
    src = 'MecTargetChamber.0:Fli.0' # Fli.FrameV1, Fli.ConfigV1

elif ntest==4 :
    #dsname = '/reg/g/psdm/data_test/types/Pimax_ConfigV1.xtc' # amob5114-r0549
    dsname = '/reg/g/psdm/data_test/types/Pimax_FrameV1.xtc'   # amob5114-r0480
    src = 'AmoEndstation.0:Pimax.0' # Pimax.ConfigV1, Pimax.FrameV1

elif ntest==5 :
    #dsname = 'exp=cxi11216:run=40' # (1, 1024, 512)
    dsname = '/reg/g/psdm/detector/data_test/types/0024-CxiEndstation.0-Jungfrau.0.xtc'
    src = 'CxiEndstation.0:Jungfrau.0'

elif ntest==6 :
    #dsname = 'exp=xppx23615:run=75' # (2160, 2560)
    dsname = '/reg/g/psdm/detector/data_test/types/0025-XppEndstation.0-Zyla.0.xtc'
    src = 'XppEndstation.0:Zyla.0' # 'zyla'

#dsname, src = 'exp=cxii8715:run=15', 'CxiEndstation.0:Quartz4A150.0' # alias='Sc1Questar'

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()

for key in evt.keys() : print key

##-----------------------------
#sys.exit('Test exit')
##-----------------------------

from Detector.AreaDetector import AreaDetector

par = nrun # evt or nrun
det = AreaDetector(src, env, pbits=0)

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins
#det.set_print_bits(511);
#det.set_def_value(-5.);
#det.set_mode(1);
#det.set_do_offset(True); # works for ex. Opal1000

#det.print_attributes()

#shape_nda = det.shape(par)
#print_ndarr(shape_nda, 'shape of ndarray')

#print 'size of ndarray: %d' % det.size(par)
#print 'ndim of ndarray: %d' % det.ndim(par)

#peds = det.pedestals(par)
#print_ndarr(peds, 'pedestals')

#rms = det.rms(par)
#print_ndarr(rms, 'rms')

#mask = det.mask(par)
#print_ndarr(mask, 'mask')

#gain = det.gain(par)
#print_ndarr(gain, 'gain')

#bkgd = det.bkgd(par)
#print_ndarr(bkgd, 'bkgd')

#status = det.status(par)
#print_ndarr(status, 'status')

#status_mask = det.status_as_mask(par)
#print_ndarr(status_mask, 'status_mask')

#cmod = det.common_mode(par)
#print_ndarr(cmod, 'common_mod')

t0_sec = time()
nda_raw = det.raw(evt)
print_ndarr(nda_raw, 'nda_raw')

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

#if peds is not None and nda_raw is not None : peds.shape = nda_raw.shape 

#data_sub_peds = nda_raw - peds if peds is not None else nda_raw
#print_ndarr(data_sub_peds, 'data - peds')

#nda_cdata = det.calib(evt)
#print_ndarr(nda_cdata, 'calibrated data')

#nda_cdata_ub = det.calib(evt, cmpars=(5,50))
#print_ndarr(nda_cdata_ub, 'calibrated data for cspad unbond pixels')

#coords_x = det.coords_x(par)
#print_ndarr(coords_x, 'coords_x')

#areas = det.areas(par)
#print_ndarr(areas, 'area')

#mask_geo = det.mask_geo(par)
#print_ndarr(mask_geo, 'mask_geo')

#mask_geo.shape = (32,185,388)
#print mask_geo

#pixel_size = det.pixel_size(par)
#print '%s\npixel size: %s' % (80*'_', str(pixel_size))

##-----------------------------
img_arr = nda_raw
#img_arr = data_sub_peds
#img_arr = nda_cdata if nda_cdata is not None else nda_raw
img = None

# Image producer is different for 3-d and 2-d arrays 
if len(nda_raw.shape) > 2 :
    img = det.image(evt)
    #img = det(evt) # alias for det.image(evt) implemented in __call__
    #img = det.image(evt, img_arr)
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
