#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana

from Detector.PyDetectorAccess import PyDetectorAccess

##-----------------------------

ds = psana.DataSource('/reg/g/psdm/detector/data_test/types/0001-CxiDs2.0-Cspad.0-config-gain-mask.xtc')
#ds = psana.DataSource('exp=cxid9114:run=96')
evt = ds.events().next()
env = ds.env()
rnum = evt.run()

src = psana.Source('CxiDs2.0:Cspad.0')
pda = PyDetectorAccess(src, env, pbits=0)

sh = pda.shape_config_cspad(env)

print('shape_config_cspad:', pda.shape_config_cspad(env))


##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
