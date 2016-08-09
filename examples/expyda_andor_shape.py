#!/usr/bin/env python
##-----------------------------

from Detector.PyDetectorAccess import PyDetectorAccess
from Detector.PyDataAccess import * # get_andor_config_object

import sys
import psana

##-----------------------------

ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0005-SxrEndstation.0-DualAndor.0.xtc')
#ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

source = 'SxrEndstation.0:DualAndor.0'
src = psana.Source(source)

#o = get_andor_config_object(env, src)

pda = PyDetectorAccess(src, env, pbits=0)
sh = pda.shape_config_andor(env)

print 'shape_config_andor(3d).shape', sh

##-----------------------------

det = psana.Detector(source, env)
print 'det.raw(evt).shape:', det.raw(evt).shape

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
