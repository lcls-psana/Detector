#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.PyDetector import PyDetector
from Detector.GlobalUtils import print_ndarr
import numpy as np

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

#dsname, src = 'exp=amob5114:run=403:idx', psana.Source('DetInfo(Camp.0:pnCCD.0)')
dsname, src = 'exp=amo86615:run=159:idx', psana.Source('DetInfo(Camp.0:pnCCD.1)')

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Non-standard calib directory
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

#tsec, tnsec, fid = 1434301977, 514786085, 44835
#et = psana.EventTime(int((tsec<<32)|tnsec),fid)

ds = psana.DataSource(dsname)

tsecnsec, fid = 6178962762198708138, 0xf762
et = psana.EventTime(int(tsecnsec),fid)

run = ds.runs().next()
evt = run.event(et)
#evt = ds.events().next()
env = ds.env()

for key in evt.keys() : print key

##-----------------------------

det = PyDetector(src, env, pbits=0, iface='C')

ins = det.instrument()

print 80*'_', '\nInstrument: ', ins
#det.set_print_bits(511);
#det.set_def_value(-5.);
#det.set_mode(1);
#det.set_do_offset(True); # works for ex. Opal1000
det.print_attributes()

shape_nda = det.shape(evt)
print_ndarr(shape_nda, 'shape')

print 'size of ndarray: %d' % det.size(evt)
print 'ndim of ndarray: %d' % det.ndim(evt)

peds = det.pedestals(evt)
print_ndarr(peds, 'pedestals')

t0_sec = time()
nda_raw = det.raw(evt)
print '%s\n **** consumed time to get raw data = %f sec' % (80*'_', time()-t0_sec)
print_ndarr(nda_raw, 'raw data')

nda_cdata = det.calib(evt)
print_ndarr(nda_cdata, 'calibrated data')

fname = 'nda-%s-%s-Camp.0:pnCCD.1.txt' % (env.experiment(), evt.run())
print 'Save ndarray in file %s' % fname
nda_cdata.shape = (512*4,512)
np.savetxt(fname, nda_cdata)

img = det.image(evt)
print_ndarr(img, 'img')
##-----------------------------

if img is None :
    print 'Image is not available'
    sys.exit('FURTHER TEST IS TERMINATED')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
gg.plotImageLarge(img, amp_range=(ave-1*rms, ave+2*rms))
gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
