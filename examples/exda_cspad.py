#!/usr/bin/env python
##-----------------------------

import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr

##-----------------------------

ds  = psana.DataSource('exp=cxif5315:run=169')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
det = Detector.DetectorAccess(src, env, 0) # , 0xffff)

#print evt.keys()

##-----------------------------
print '\nInstrument: ', det.instrument(env)
print_ndarr(det.pedestals(evt,env),    'pedestals(evt,env)')
print_ndarr(det.pedestals_v0(rnum),    'pedestals_v0(rnum)')
print_ndarr(det.pixel_rms(evt,env),    'pixel_rms(evt,env)')
print_ndarr(det.pixel_gain(evt,env),   'pixel_gain(evt,env)')
print_ndarr(det.pixel_mask(evt,env),   'pixel_mask(evt,env)')
print_ndarr(det.pixel_bkgd(evt,env),   'pixel_bkgd(evt,env)')
print_ndarr(det.pixel_status(evt,env), 'pixel_status(evt,env)')
print_ndarr(det.common_mode(evt,env),  'common_mode(evt,env)')
print_ndarr(det.common_mode_v0(rnum),  'common_mode_v0(rnum)')
##-----------------------------

#det.set_print_bits(255);
det.set_def_value(-5.);
det.set_mode(1);
raw_data = det.data_int16_3(evt,env)

print_ndarr(raw_data, 'raw_data')
print_ndarr(det.pixel_coords_x(evt,env),     'pixel_coords_x(evt,env)')
print_ndarr(det.pixel_coords_x_v0(rnum),     'pixel_coords_x_v0(rnum)')
print_ndarr(det.pixel_coords_y(evt,env),     'pixel_coords_y(evt,env)')
print_ndarr(det.pixel_coords_z(evt,env),     'pixel_coords_z(evt,env)')
print_ndarr(det.pixel_areas(evt,env),        'pixel_areas(evt,env)')
print_ndarr(det.pixel_mask_geo_v0(rnum,255), 'pixel_mask_geo_v0(rnum,255)')
print_ndarr(det.pixel_mask_geo(evt,env,255), 'pixel_mask_geo(evt,env,255)')
print_ndarr(det.pixel_indexes_x(evt,env),    'pixel_indexes_x(evt,env)')
print_ndarr(det.pixel_indexes_y(evt,env),    'pixel_indexes_y(evt,env)')
print '\n pixel_scale_size(evt,env): ', det.pixel_scale_size(evt,env)
print '\n pixel_scale_size_v0(rnum): ', det.pixel_scale_size_v0(rnum)

#print_ndarr(, '')

##-----------------------------
import numpy as np

nda_img = np.array(raw_data.flatten()-det.pedestals(evt,env).flatten(), dtype=np.double)
print_ndarr(nda_img, 'nda_img')

img = det.get_image(evt, env, nda_img)
print_ndarr(img, 'img')

##-----------------------------
import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+6*rms))
gg.show()

sys.exit(0)

##-----------------------------
##-----------------------------
##-----------------------------
