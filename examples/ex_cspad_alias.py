#!/usr/bin/env python

#------------------------------
from __future__ import print_function
import sys
import psana
from Detector.AreaDetector import AreaDetector
from Detector.GlobalUtils import print_ndarr
 
#ds  = psana.DataSource('exp=cxi86715:run=99')
#src = 'CxiDs2.0:Cspad.0'
ds  = psana.DataSource('/reg/g/psdm/detector/data_test/types/0003-CxiDs2.0-Cspad.0-fiber-data.xtc')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DsaCsPad')
if len(sys.argv)>1 and sys.argv[1] == '2' : src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

print('%s: src: %s' % (sys.argv[0], src))

#print evt.get(psana.CsPad.DataV2,src)

det = AreaDetector(src, env, pbits=0, iface='P')
print_ndarr(det.raw(evt), '%s\nraw'%(80*'_'))

#img = det.image(evt, raw)
#print img[510:515,510:515]

#------------------------------
