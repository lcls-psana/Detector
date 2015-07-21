#!/usr/bin/env python

import sys
import psana
from time import time
from Detector.PyDetector import PyDetector

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest

##-----------------------------

dsname, src = 'exp=cxi86715:run=112:idx', psana.Source('DetInfo(CxiDg2.0:Cspad2x2.0)')
#dsname, src = 'exp=cxi86715:run=112', psana.Source('DetInfo(CxiDg2.0:Cspad2x2.0)')

print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Non-standard calib directory
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

tsec, tnsec, fid = 1434301977, 514786085,  44835
et = psana.EventTime(int((tsec<<32)|tnsec),fid)

ds  = psana.DataSource(dsname)
run = ds.runs().next()
evt = run.event(et)

#evt = ds.events().next()
env = ds.env()

#for key in evt.keys() : print key

##-----------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s\n%s: %s' % (80*'_', name, nda)
    else           : print '%s\n%s: \n%s...\n shape:%s  size:%d  dtype:%s' % \
         (80*'_', name, nda.flatten()[first:last], str(nda.shape), nda.size, nda.dtype)

##-----------------------------

det = PyDetector(src, env, pbits=0)

ins = det.instrument()

print 80*'_', '\nInstrument: ', ins
#det.set_print_bits(511);
#det.set_def_value(-5.);
#det.set_mode(1);
#det.set_do_offset(True); # works for ex. Opal1000
det.print_attributes()

shape_nda = det.shape(evt)
print_ndarr(shape_nda, 'shape of ndarray')

print 'size of ndarray: %d' % det.size(evt)
print 'ndim of ndarray: %d' % det.ndim(evt)

peds = det.pedestals(evt)
print_ndarr(peds, 'pedestals')

t0_sec = time()
nda_raw = det.raw(evt)
print '%s\n **** consumed time to get raw data = %f sec' % (80*'_', time()-t0_sec)

#i=0
#if nda_raw is None :
#    for i, evt in enumerate(ds.events()) :
#        nda_raw = det.raw(evt)
#        if nda_raw is not None :
#            print 'Detector data found in event %d' % i
#            break

print_ndarr(nda_raw, 'raw data')

#if nda_raw is None :
#    print 'Detector data IS NOT FOUND in %d events' % i
#    sys.exit('FURTHER TEST IS TERMINATED')

##-----------------------------

#data_sub_peds = nda_raw - peds if peds is not None else nda_raw
#print_ndarr(data_sub_peds, 'data - peds')

nda_cdata = det.calib(evt)
print_ndarr(nda_cdata, 'calibrated data')

##-----------------------------

sys.exit(0)

##-----------------------------
