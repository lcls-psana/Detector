#!/usr/bin/env python
##-----------------------------

import sys
import psana
import Detector

##-----------------------------

ds  = psana.DataSource('exp=cxif5315:run=169')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
#src = Source('Camp.0:pnCCD.1')

det = Detector.DetectorAccess(src,0) # , 0xffff)
# src)

#print evt.keys()

##-----------------------------

peds = det.pedestals(evt,env)
print '\npedestals:\n', peds[0:20]

prms = det.pixel_rms(evt,env)
print '\npixel_rms:\n', prms[0:20]

pgain = det.pixel_gain(evt,env)
print '\npixel_gain:\n', pgain[0:20]

pmask = det.pixel_mask(evt,env)
print '\npixel_mask:\n', pmask[0:20]

pbkgd = det.pixel_bkgd(evt,env)
print '\npixel_bkgd:\n', pbkgd[0:20]

pstat = det.pixel_status(evt,env)
print '\npixel_status:\n', pstat[0:20]

pcmod = det.common_mode(evt,env)
print '\ncommon_mode:\n', pcmod

print '\nInstrument: ', det.inst(env)

##-----------------------------

#det.set_print_bits(255);
det.set_def_value(-5.);
det.set_mode(1);
raw_data = det.data_int16_3(evt,env)
print '\nraw_data:\n', raw_data
print 'raw_data type: %s shape: %s' % (raw_data.dtype, raw_data.shape)

pixel_x = det.pixel_coords_x(evt,env)
print '\npixel_x:\n', pixel_x
print 'pixel_x type: %s shape: %s' % (pixel_x.dtype, pixel_x.shape)

pixel_y = det.pixel_coords_y(evt,env)
print '\npixel_y:\n', pixel_y
print 'pixel_y type: %s shape: %s' % (pixel_y.dtype, pixel_y.shape)

pixel_a = det.pixel_areas(evt,env)
print '\npixel_a:\n', pixel_a
print 'pixel_a type: %s shape: %s' % (pixel_a.dtype, pixel_a.shape)

pixel_m = det.pixel_mask_geo(evt,env)
print '\npixel_m:\n', pixel_m
print 'pixel_m type: %s shape: %s' % (pixel_m.dtype, pixel_m.shape)

print '\npixel_scale_size: ', det.pixel_scale_size(evt,env)

pixel_ix = det.pixel_indexes_x(evt,env)
print '\npixel_ix:\n', pixel_ix
print 'pixel_ix type: %s shape: %s' % (pixel_ix.dtype, pixel_ix.shape)

pixel_iy = det.pixel_indexes_y(evt,env)
print '\npixel_iy:\n', pixel_iy
print 'pixel_iy type: %s shape: %s' % (pixel_iy.dtype, pixel_iy.shape)


##-----------------------------
import numpy as np

nda_img = np.array(raw_data.flatten()-peds, dtype=np.double)
print '\nnda_img:\n', nda_img
print 'nda_img type: %s shape: %s' % (nda_img.dtype, nda_img.shape)

img = det.get_image(evt, env, nda_img)
print '\nimg:\n', img
print 'img type: %s shape: %s' % (img.dtype, img.shape)


##-----------------------------
import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

sys.exit(0)
##-----------------------------
