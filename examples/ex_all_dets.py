#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.GlobalUtils import print_ndarr
import PSCalib.GlobalUtils as gu

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------
dsname, src = None, None

if ntest==1 : # dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'
    dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'CxiDs2.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

if ntest==2 : # dsname, src = 'exp=meca1113:run=376', 'MecTargetChamber.0:Cspad2x2.1'
    dsname = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc'
    src = 'MecTargetChamber.0:Cspad2x2.1'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad2x2/calib-cspad2x2-01-2013-02-13/calib')

elif ntest==3 : #dsname, src = 'exp=amob5114:run=403', 'Camp.0:pnCCD.0'
    dsname, src = '/reg/g/psdm/detector/data_test/types/0010-Camp.0-pnCCD.0.xtc', 'Camp.0:pnCCD.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/pnccd/amo86615-pnccd-2015-09-09/calib')

elif ntest==4 : #dsname, src = 'exp=xppi0614:run=74',  'NoDetector.0:Epix100a.0'
    dsname, src = '/reg/g/psdm/detector/data_test/types/0007-NoDetector.0-Epix100a.0.xtc', 'NoDetector.0:Epix100a.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/epix100/xpp-epix100a-2014-12-04/calib')
    #psana.setOption('psana.calib-dir', './calib')

elif ntest==5 : dsname, src = 'exp=sxrg3715:run=46',  'SxrEndstation.0:Andor.2'
elif ntest==6 : dsname, src = 'exp=sxrf9414:run=72',  'SxrEndstation.0:Fccd960.0'
elif ntest==7 : dsname, src = 'exp=xcsi0112:run=15',  'XcsBeamline.0:Princeton.0'
elif ntest==8 : dsname, src = 'exp=amo42112:run=120', 'AmoBPS.0:Opal1000.0'
elif ntest==9 : dsname, src = 'exp=cxib2313:run=46',  'CxiDg2.0:Tm6740.0'

elif ntest==10 : # dsname, src = 'exp=amo86615:run=4',   'Camp.0:pnCCD.0'
    dsname, src = '/reg/g/psdm/detector/data_test/types/0008-Camp.0-pnCCD.1.xtc', 'Camp.0:pnCCD.1'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/pnccd/amo86615-pnccd-2015-09-09/calib')

elif ntest==11 : # dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0' # string
    dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'CxiDs2.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

elif ntest==12 : # dsname, src = 'exp=cxif5315:run=169', 'DsaCsPad'  # alias
    dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'DsaCsPad'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')


elif ntest==15 : dsname, src = 'exp=cxii8715:run=14',  'CxiEndstation.0:Quartz4A150.0' # alias='Sc1Questar'
#elif ntest==16 : #dsname, src = 'exp=xppc0115:run=305', 'XppEndstation.0:Rayonix.0' # alias='rayonix'
#elif ntest==16 : #dsname, src = 'exp=xppc0115:run=335', 'XppEndstation.0:Rayonix.0' # alias='rayonix'
#    dsname, src = '/reg/g/psdm/detector/data_test/types/0011-XppEndstation.0-Rayonix.0.xtc', 'XppEndstation.0:Rayonix.0'
#    # JUST A SUBSTITUTE FOR calib directory
#    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

elif ntest==16 : #dsname, src = 'exp=xppc0115:run=335', 'XppEndstation.0:Rayonix.0' # alias='rayonix'
    #dsname, src = '/reg/g/psdm/detector/data_test/types/0011-XppEndstation.0-Rayonix.0.xtc', 'XppEndstation.0:Rayonix.0'
    dsname, src = 'exp=xppc0115:run=335', 'XppEndstation.0:Rayonix.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/ryonix/calib')

#elif ntest==17 : dsname, src = 'exp=amoj5415:run=49',  'pnccdFront'
elif ntest==17 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0009-pnccdFront.xtc', 'pnccdFront'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/pnccd/amo06516-pnccd-2016-04-14/calib')

elif ntest==18 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0002-MecTargetChamber.0-Cspad.0-two-quads.xtc', 'MecTargetChamber.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')

elif ntest==19 :
    dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc', 'MecTargetChamber.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')

elif ntest==20 :   #The same as 'exp=cxif5315:run=169' but geometry is different
    dsname, src = '/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc',  'CxiDs2.0:Cspad.0'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-cxi-camera2-2015-01-20/calib')

elif ntest==21 : # dsname, src = 'exp=sxrk4816:run=3',  'SxrEndstation.0:DualAndor.0'
    dsname = '/reg/g/psdm/detector/data_test/types/0005-SxrEndstation.0-DualAndor.0.xtc' # exp=sxrk4816:run=3
    src = 'SxrEndstation.0:DualAndor.0'# or alias='andorDual'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')

elif ntest==22 : # dsname, src = 'exp=sxrk4816:run=7',  'SxrEndstation.0:DualAndor.0'
    dsname = '/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc' # exp=sxrk4816:run=7
    src = 'SxrEndstation.0:DualAndor.0'# or alias='andorDual'
    psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')

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

if det.dettype == gu.CSPAD \
or det.dettype == gu.CSPAD2X2 :
    t0_sec = time()
    nda_cdata_ub = det.calib(evt, cmpars=(5,50))
    print_ndarr(nda_cdata_ub, 'calibrated cspad(2x2) data with unbond pixel common mode correction')
    print 'Consumed time for det.calib(evt) = %7.3f sec' % (time()-t0_sec)

coords_x = det.coords_x(par)
print_ndarr(coords_x, 'coords_x')

##-----------------------------
#sys.exit('TEST EXIT')
##-----------------------------

areas = det.areas(par)
print_ndarr(areas, 'area')

mask_geo = det.mask_geo(par)
print_ndarr(mask_geo, 'mask_geo')

#mask_geo.shape = (32,185,388)
#print mask_geo

pixel_size = det.pixel_size(par)
print '%s\npixel size: %s' % (80*'_', str(pixel_size))

ipx, ipy = det.point_indexes(par) # , pxy_um=(0,0)) 
print 'Detector origin indexes: ix, iy:', ipx, ipy
##-----------------------------

img_arr = data_sub_peds
#img_arr = nda_cdata if nda_cdata is not None else nda_raw
img = None

# Image producer is different for 3-d and 2-d arrays 
if len(nda_raw.shape) > 2 :
    #img = det.image(evt)
    
    t0_sec = time()
    #img = det.image(evt)
    img = det.image(evt, img_arr)
    print 'Consumed time for det.image(evt) = %7.3f sec (for 1st event!)' % (time()-t0_sec)
else :
    img = img_arr
    img.shape = nda_raw.shape

print_ndarr(img, 'image (calibrated data or raw)')

print 80*'_'

##-----------------------------

if img is None :
    sys.exit('Image is not available. FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
gg.show()

##-----------------------------

print_ndarr(det.image_xaxis(par), 'image_xaxis')
print_ndarr(det.image_yaxis(par), 'image_yaxis')

##-----------------------------
print 80*'_','\nTest do_reshape_2d_to_3d'

print_ndarr(det.pedestals(par), 'pedestals w/o reshape')
det.do_reshape_2d_to_3d(flag=True)
print_ndarr(det.pedestals(par), 'pedestals reshaped to 3d')

##-----------------------------

sys.exit(0)

##-----------------------------
