#!/usr/bin/env python

from __future__ import print_function
import psana
from time import time
from Detector.GlobalUtils import print_ndarr

##-----------------------------

#dsname, src = 'exp=cxif5315:run=169', 'CxiDs2.0:Cspad.0'

dsname = '/reg/g/psdm/detector/data_test/types/0006-SxrEndstation.0-DualAndor.0.xtc' # exp=sxrk4816:run=7
src = 'SxrEndstation.0:DualAndor.0'# or alias='andorDual'
psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/andor3d/calib-andor3d-2016-02-09/calib')

ds  = psana.DataSource(dsname)
env = ds.env()
runnum = ds.runs().next().run()

det = psana.Detector(src, env)
#det.print_attributes()

peds = det.pedestals(runnum)
print_ndarr(peds, '%s\npedestals'%(80*'_'))

##-----------------------------

import tempfile
tmp_file = tempfile.NamedTemporaryFile(mode='r+b',suffix='.txt')
fname = tmp_file.name

#fname = 'test_save_txtnda_pedestals.txt'

t0_sec=time()
det.save_txtnda(fname, ndarr=peds, cmts=('comment1', 'comment2'), fmt='%.2f', verbos=True)
print('Time to save %s n-d array  in  file = %9.6f sec' % (src, time()-t0_sec))


f = open(fname)
for i,line in enumerate(f) :
    if i>16 : f.close(); break
    print(line.rstrip('\n'))

t0_sec=time()
peds_loaded = det.load_txtnda(fname)
print('Time to load %s n-d array from file = %9.6f sec' % (src, time()-t0_sec))
print_ndarr(peds_loaded, '%s\npedestals loaded'%(80*'_'))

print('End of test')

##-----------------------------
