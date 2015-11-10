#!/usr/bin/env python

##-----------------------------

import psana
import numpy as np
from Detector.WFDetector import WFDetector
from Detector.GlobalUtils import print_ndarr

import pyimgalgos.GlobalGraphics as gg

dsname, src = 'exp=cxii0215:run=49', psana.Source('DetInfo(CxiEndstation.0:Imp.1)')
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()
nrun = evt.run()

for key in evt.keys() : print key

##-----------------------------

det = WFDetector(src, env, pbits=4, iface='P')

ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

##-----------------------------
#det.set_calib_imp(do_calib_imp=True)

wf = det.raw(evt)

print_ndarr(wf, 'Imp waveform')
print 'wf:\n', wf

x = range(wf.shape[1])
fig, ax = gg.plotGraph(x, wf[0], figsize=(15,5))
ax.plot(x,wf[1],'r-')
ax.plot(x,wf[2],'g-')
ax.plot(x,wf[3],'m-')

gg.show()

##-----------------------------
##-----------------------------
##-----------------------------
##-----------------------------
