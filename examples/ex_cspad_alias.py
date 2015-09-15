#!/usr/bin/env python

#------------------------------
import sys
import psana
from Detector.PyDetector import PyDetector

ds  = psana.DataSource('exp=cxi86715:run=99')
evt = ds.events().next()
env = ds.env()

src = psana.Source('DetInfo(DsaCsPad)')
if len(sys.argv)>1 and sys.argv[1] == '2' : src = psana.Source('DetInfo(CxiDs2.0:Cspad.0)')

print '%s: src: %s' % (sys.argv[0], src)

#print evt.get(psana.CsPad.DataV2,src)

det = PyDetector(src, env, pbits=0, iface='P')
img = det.image(evt)
print img[510:515,510:515]

#------------------------------
