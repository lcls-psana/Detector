#!/usr/bin/env python

##-----------------------------

import sys
import psana
import numpy as np
from Detector.WFDetector import WFDetector

import pyimgalgos.GlobalGraphics as gg

#dsname, src = 'exp=sxri0414:run=88', 'SxrEndstation.0:Acqiris.2'
#dsname, src = 'exp=sxri0414:run=88', 'acq02'
dsname, src = '/reg/g/psdm/detector/data_test/types/0013-SxrEndstation.0-Acqiris.0.xtc', 'acq02'

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

#opts = {'psana.calib-dir':'./calib',}
#psana.setOptions(opts)
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt1= ds.events().next()
evt = ds.events().next()
env = ds.env()
nrun = evt.run()

for key in evt.keys() : print key

det = WFDetector(src, env, pbits=1022, iface='P')
ins = det.instrument()
print 80*'_', '\nInstrument: ', ins

det.print_attributes()

##-----------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s\n%s: %s' % (80*'_', name, nda)
    else           : print '%s\n%s: \n%s...\n shape:%s  size:%d  dtype:%s' % \
         (80*'_', name, nda.flatten()[first:last], str(nda.shape), nda.size, nda.dtype)

##-----------------------------

wf,wt = det.raw(evt)

print_ndarr(wf, 'acqiris waveform')
print_ndarr(wt, 'acqiris wavetime')

ch=0
fig, ax = gg.plotGraph(wt[ch,:-1], wf[ch,:-1], figsize=(15,5))
gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
