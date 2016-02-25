#!/usr/bin/env python

import psana
from time import time
from Detector.GlobalUtils import print_ndarr

##-----------------------------

dsname = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc'
src = 'MecTargetChamber.0:Cspad2x2.1'
psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad2x2/calib-cspad2x2-01-2013-02-13/calib')

ds  = psana.DataSource(dsname)
env = ds.env()
runnum = ds.runs().next().run()

det = psana.Detector(src, env)
#det.print_attributes()

nda = det.mask_calib(runnum)
print_ndarr(nda, '%s\nmask'%(80*'_'))

##-----------------------------

import tempfile
tmp_file = tempfile.NamedTemporaryFile(mode='r+b',suffix='.txt')
fname = tmp_file.name

#fname = 'test_save_txtnda_pedestals.txt'

t0_sec=time()
#det.save_txtnda(fname, nda, cmts=('comment1', 'comment2'), fmt='%.2f', verbos=True)
det.save_asdaq(fname, nda, cmts=('comment1', 'comment2'), fmt='%.2f', verbos=True)
print 'Time to save %s n-d array in file = %9.6f sec' % (src, time()-t0_sec)

print '%s\nATTENTION HERE: cspad2x2 array originally shaped as (2, 185, 388) is saved as in DAQ (185, 388, 2)' % (100*'!')

f = open(fname)
for i,line in enumerate(f) :
    if i>20 : f.close(); break
    print line.rstrip('\n')

t0_sec=time()
nda_loaded = det.load_txtnda(fname)
print 'Time to load %s n-d array from file = %9.6f sec' % (src, time()-t0_sec)
print_ndarr(nda_loaded, '%s\nnda loaded'%(80*'_'))

print 'End of test'

##-----------------------------
