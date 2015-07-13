#!/usr/bin/env python

import sys
import psana
import numpy as np
from Detector.PyDetector import PyDetector

import pyimgalgos.GlobalGraphics as gg

dsname, src = 'exp=sxri0414:run=88', psana.Source('DetInfo(SxrEndstation.0:Acqiris.2)')
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Use non-standard calib directory
#opts = {'psana.calib-dir':'./calib',}
#psana.setOptions(opts)
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt1= ds.events().next()
evt = ds.events().next()
env = ds.env()

for key in evt.keys() : print key

det = PyDetector(src, env, pbits=0)
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
##-----------------------------
##-----------------------------

sys.exit(0)

##-----------------------------
