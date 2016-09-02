#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.AreaDetector import AreaDetector
from Detector.GlobalUtils import print_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

#dsname, src = 'exp=cxi86715:run=112:idx', psana.Source('DetInfo(CxiDg2.0:Cspad2x2.0)')
#dsname, src = 'exp=cxi86715:run=112', psana.Source('DetInfo(CxiDg2.0:Cspad2x2.0)')
dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad2x2.1.xtc', 'MecTargetChamber.0:Cspad2x2.1'

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Non-standard calib directory
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

#tsec, tnsec, fid = 1434301977, 514786085, 44835
#et = psana.EventTime(int((tsec<<32)|tnsec),fid)

ds  = psana.DataSource(dsname)
run = ds.runs().next()
#evt = run.event(et)
evt = ds.events().next()
env = ds.env()

for key in evt.keys() : print key

##-----------------------------

det = AreaDetector(src, env, pbits=0, iface='C')

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

##-----------------------------

sys.exit(0)

##-----------------------------
