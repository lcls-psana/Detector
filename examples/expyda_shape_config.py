#!/usr/bin/env python

from __future__ import print_function
import sys
import psana
from time import time
from ex_source_dsname import ex_source_dsname
from Detector.PyDetectorAccess import PyDetectorAccess
 
##-----------------------------

def test_shape_config(ntest) : 
    """test shape retreived fron config object"""

    src, dsn = ex_source_dsname(ntest)
    print('src=%s, dsname=%s' % (src, dsn))

    src = psana.Source(src)
    ds  = psana.DataSource(dsn)
    env = ds.env()
    evt = next(ds.events())

    pda = PyDetectorAccess(src, env, pbits=0)
    print('shape_config =', pda.shape_config(env))

    #print 'raw data imp =', pda.raw_data_imp(evt, env).shape
    #print 'shape_data_camera =', pda.shape_data_camera(evt)

    #for i, evt in enumerate(ds.events()):
    #    if i>10 : break

##-----------------------------

if __name__ == "__main__" :

    ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
    print('%s\nExample # %d' % (80*'_', ntest))

    test_shape_config(ntest)

    sys.exit(0)

##-----------------------------
