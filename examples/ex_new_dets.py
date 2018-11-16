#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr

# supress matplotlib deprication warnings
import warnings
warnings.filterwarnings("ignore",".*GUI is implemented.*")

##-----------------------------

import logging
logger = logging.getLogger(__name__)

logging.basicConfig(format='%(levelname)s: %(name)s %(message)s', level=logging.INFO) # INFO) #DEBUG)

##-----------------------------

tname = sys.argv[1] if len(sys.argv)>1 else '1'
print 'Test "%s"' % tname

##-----------------------------

dsname, src = None, None

if tname=='1' :
    dsname = '/reg/g/psdm/data_test/types/FCCD_FccdConfigV2.xtc' # sxr61612-r0332
    src = 'SxrEndstation.0:Fccd.0' # Camera.FrameV1. Fccd.ConfigV2

if tname=='2' :
    #dsname = '/reg/g/psdm/data_test/types/Timepix_ConfigV3.xtc' # xcsi0113-r0030
    dsname = '/reg/g/psdm/data_test/types/Timepix_DataV2.xtc'    # xcsi0113-r0030
    src = 'XcsEndstation.0:Timepix.0' # Timepix.DataV2 Timepix.ConfigV3

elif tname=='3' :
    dsname = '/reg/g/psdm/data_test/types/Fli_ConfigV1.xtc' # meca6013-r0009
    dsname = '/reg/g/psdm/data_test/types/Fli_FrameV1.xtc'  # meca6013-r0009
    src = 'MecTargetChamber.0:Fli.0' # Fli.FrameV1, Fli.ConfigV1

elif tname=='4' :
    #dsname = '/reg/g/psdm/data_test/types/Pimax_ConfigV1.xtc' # amob5114-r0549
    dsname = '/reg/g/psdm/data_test/types/Pimax_FrameV1.xtc'   # amob5114-r0480
    src = 'AmoEndstation.0:Pimax.0' # Pimax.ConfigV1, Pimax.FrameV1

elif tname=='5' :
    #dsname = 'exp=cxi11216:run=40' # (1, 512, 1024)
    dsname = '/reg/g/psdm/detector/data_test/types/0024-CxiEndstation.0-Jungfrau.0.xtc'
    src = 'CxiEndstation.0:Jungfrau.0'

elif tname=='6' :
    #dsname = 'exp=xppx23615:run=75' # (2160, 2560)
    dsname = '/reg/g/psdm/detector/data_test/types/0025-XppEndstation.0-Zyla.0.xtc'
    src = 'XppEndstation.0:Zyla.0' # 'zyla'

elif tname=='7' :
    dsname = '/reg/g/psdm/detector/data_test/types/0026-MecTargetChamber.0-Pixis.1.xtc'
    src = 'MecTargetChamber.0:Pixis.1'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/') # '/reg/d/psdm/det/mecdaq115/calib'

elif tname=='8' :
    dsname = '/reg/g/psdm/detector/data_test/types/0027-DetLab.0-Uxi.0.xtc'
    src = 'DetLab.0:Uxi.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/') # '/reg/d/psdm/det/detdaq17/calib'

elif tname=='9' :
    #dsname = 'exp=detdaq17:run=121'
    dsname = '/reg/g/psdm/detector/data_test/types/0030-DetLab.0-StreakC7700.0.xtc' # (1024, 1344)
    src = 'DetLab.0:StreakC7700.0'
    #psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/') # '/reg/d/psdm/det/detdaq17/calib'
    #/reg/d/psdm/DET/detdaq17/calib/Camera::CalibV1/DetLab.0:StreakC7700.0/pedestals/121-end.data

elif tname=='10' :
    #dsname = 'exp=sxrx35317:run=1'
    dsname = '/reg/g/psdm/detector/data_test/types/0029-SxrEndstation.0-Archon.0.xtc' # (300, 4800)
    src = 'SxrEndstation.0:Archon.0'
    psana.setOption('psana.calib-dir', '/reg/neh/home/dubrovin/LCLS/con-detector/calib/') # '/reg/d/psdm/det/detdaq17/calib'

elif tname=='11' :
    dsname = '/reg/g/psdm/detector/data_test/types/0028-NoDetector.0-Epix10ka2M.0.xtc' # (16, 352, 384)
    src = 'NoDetector.0:Epix10ka2M.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/')

elif tname=='12' :
    # fgeo = '/reg/g/psdm/detector/data_test/calib/Epix10kaQuad::CalibV1/NoDetector.0:Epix10kaQuad.0/geometry/0-end.data'
    dsname = '/reg/g/psdm/detector/data_test/types/0032-NoDetector.0-Epix10kaQuad.0.xtc' # (4, 352, 384)
    src = 'NoDetector.0:Epix10kaQuad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib')

elif tname=='13' : # exp=mecx32917:run=0076 'MecTargetChamber.0-Epix10ka.1' # alias='Epix10kTender_1'
    #dsname = 'exp=mecx32917:run=0076'
    dsname = '/reg/g/psdm/detector/data_test/types/0033-MecTargetChamber.0-Epix10ka.1.xtc'
    src = 'MecTargetChamber.0:Epix10ka.1' # alias='Epix10kTender_1'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib')

elif tname=='14' : #dsname, src = 'exp=mfxn8316:run=11',  'MfxEndstation.0:Epix100a.0'
    # fgeo = '/reg/g/psdm/detector/data_test/calib/Epix10ka::CalibV1/MecTargetChamber.0:Epix10ka.1/geometry/0-end.data'
    dsname = '/reg/g/psdm/detector/data_test/types/0021-MfxEndstation.0-Epix100a.0.xtc'
    src = 'MfxEndstation.0:Epix100a.0'
    psana.setOption('psana.calib-dir', './calib') # dark exp=mfxn8316:run=9

elif tname=='15' :
#    # fgeo = '/reg/g/psdm/detector/data_test/calib/Epix10kaQuad::CalibV1/NoDetector.0:Epix10kaQuad.0/geometry/0-end.data'
    dsname = 'exp=mecx32917:run=106' # (4, 352, 384)
    src = 'MecTargetChamber.0:Epix10kaQuad.2'
#    #src = 'MecTargetChamber.0:Epix10kaQuad.3'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib')

elif tname=='16' :
    dsname = '/reg/g/psdm/detector/data_test/types/0034-NoDetector.0-Epix10ka2M.0.xtc' # (16, 352, 384)
    src = 'NoDetector.0:Epix10ka2M.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/')

elif tname=='101' :
    dsname = 'exp=meclu5717:run=3'
    src = 'MecTargetChamber.0:Jungfrau.0'
    #psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/')

#dsname, src = 'exp=cxii8715:run=15', 'CxiEndstation.0:Quartz4A150.0' # alias='Sc1Questar'

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')
#psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()

print 'experiment %s' % env.experiment()
print 'Run number %d' % nrun
print 'dataset exp=%s:run=%d' % (env.experiment(),nrun) 
print 'calibDir:', env.calibDir()

for key in evt.keys() : print key

##-----------------------------
#sys.exit('Test exit')
##-----------------------------

from Detector.AreaDetector import AreaDetector

par = nrun # evt or nrun
det = AreaDetector(src, env, pbits=0)

#det.set_print_bits(511);

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

#det.set_def_value(-5.);
#det.set_mode(1);
#det.set_do_offset(True); # works for ex. Opal1000

#det.print_attributes()

#shape_nda = det.shape(par)
#print_ndarr(shape_nda, 'shape of ndarray')

#print 'size of ndarray: %d' % det.size(par)
#print 'ndim of ndarray: %d' % det.ndim(par)

peds = det.pedestals(par)
print_ndarr(peds, 'pedestals')

gain = det.gain(par)
print_ndarr(gain, 'pixel_gain')

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

calib = det.calib(evt)
print_ndarr(calib, 'calib')

t0_sec = time()
nda_raw = det.raw(evt)
print_ndarr(nda_raw, 'nda_raw')

##-----------------------------

EVSKIP = 20000
i=0
#if nda_raw is None :
if True :
    for i, evt in enumerate(ds.events()) :
        if i<EVSKIP: continue
        print 'Event %d' % i
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

coords_x = det.coords_x(par)
print_ndarr(coords_x, 'coords_x')

##-----------------------------
#sys.exit('TEST EXIT')
##-----------------------------

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

img = det.image(evt)
print_ndarr(img, 'img')

# Image producer is different for 3-d and 2-d arrays 
if img is None :
  if len(nda_raw.shape) > 2 :
    if 'Jungfrau' in src : 
        img = nda_raw
        sh = nda_raw.shape
        img.shape = (img.size/sh[-1],sh[-1])

    elif 'Uxi' in src : # 3-d like (<n-frames>, 1024, 512)
        img = nda_raw # det.calib(evt)
        sh = img.shape # (2, 1024, 512)
        img.shape = (img.size/sh[-1],sh[-1])

    else :
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
