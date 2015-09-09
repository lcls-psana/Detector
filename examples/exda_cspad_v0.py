#!/usr/bin/env python
##-----------------------------

import sys
import psana
import Detector
from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

ds  = psana.DataSource('exp=cxif5315:run=169')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
det = Detector.DetectorAccess(src, env, 0) # , 0xffff)
calibdir = env.calibDir()

#print evt.keys()

###-----------------------------
print '\nInstrument: ', det.instrument(env)
t0_sec = time()
print_ndarr(det.pedestals(evt,env),    'pedestals(evt,env)')
t0_sec = time()
print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(det.pedestals_v0(rnum),    'pedestals_v0(rnum)')
print 'Consumed time = %7.3f sec' % (time()-t0_sec)
print_ndarr(det.pixel_rms(evt,env),    'pixel_rms(evt,env)')
print_ndarr(det.pixel_rms_v0(rnum),    'pixel_rms_v0(rnum)')
print_ndarr(det.pixel_gain(evt,env),   'pixel_gain(evt,env)')
print_ndarr(det.pixel_gain_v0(rnum),   'pixel_gain_v0(rnum)')
print_ndarr(det.pixel_mask(evt,env),   'pixel_mask(evt,env)')
print_ndarr(det.pixel_mask_v0(rnum),   'pixel_mask_v0(rnum)')
print_ndarr(det.pixel_bkgd(evt,env),   'pixel_bkgd(evt,env)')
print_ndarr(det.pixel_bkgd_v0(rnum),   'pixel_bkgd_v0(rnum)')
print_ndarr(det.pixel_status(evt,env), 'pixel_status(evt,env)')
print_ndarr(det.pixel_status_v0(rnum), 'pixel_status_v0(rnum)')
print_ndarr(det.common_mode(evt,env),  'common_mode(evt,env)')
print_ndarr(det.common_mode_v0(rnum),  'common_mode_v0(rnum)')
##-----------------------------

print_ndarr(det.pixel_coords_x(evt,env),      'pixel_coords_x(evt,env)')
print_ndarr(det.pixel_coords_x_v0(rnum),      'pixel_coords_x_v0(rnum)')
print_ndarr(det.pixel_coords_y(evt,env),      'pixel_coords_y(evt,env)')
print_ndarr(det.pixel_coords_y_v0(rnum),      'pixel_coords_y_v0(rnum)')
print_ndarr(det.pixel_areas(evt,env),         'pixel_areas(evt,env)')
print_ndarr(det.pixel_areas_v0(rnum),         'pixel_areas_v0(rnum)')
print_ndarr(det.pixel_mask_geo(evt,env, 255), 'pixel_mask_geo(evt,env, 255)')
print_ndarr(det.pixel_mask_geo_v0(rnum, 255), 'pixel_mask_geo_v0(rnum, 255)')
print_ndarr(det.pixel_mask_geo(evt,env, 255), 'pixel_mask_geo(evt,env, 255)')
print_ndarr(det.pixel_indexes_x(evt,env),     'pixel_indexes_x(evt,env)')
print_ndarr(det.pixel_indexes_x_v0(rnum),     'pixel_indexes_x_v0(rnum)')

print_ndarr(det.pixel_indexes_y(evt,env),     'pixel_indexes_y(evt,env)')
print_ndarr(det.pixel_indexes_y_v0(rnum),     'pixel_indexes_y_v0(rnum)')

##-----------------------------
import numpy as np

#det.set_print_bits(255);
#det.set_def_value(-5.);
#det.set_mode(1);
raw_data = det.data_int16_3(evt,env)
print_ndarr(raw_data, 'raw_data')

nda_img = np.array(raw_data, dtype=np.double)

img = det.get_image(evt, env, nda_img.flatten())
print_ndarr(img, 'get_image')

img = det.get_image_v0(rnum, nda_img.flatten())
print_ndarr(img, 'get_image_v0')

##-----------------------------
import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+1*rms))
gg.show()

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
