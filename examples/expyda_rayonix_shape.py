#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
from Detector.PyDetectorAccess import PyDetectorAccess

import sys
import psana

##-----------------------------

ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0011-XppEndstation.0-Rayonix.0.xtc')
evt = next(ds.events())
env = ds.env()
rnum = evt.run()

source = 'XppEndstation.0:Rayonix.0'
src = psana.Source(source)

pda = PyDetectorAccess(src, env, pbits=0)

sh = pda.shape_config_rayonix(env)

print('shape_config_rayonix:', sh)

##-----------------------------

det = psana.Detector(source, env)
print('det.raw(evt).shape:', det.raw(evt).shape)

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
