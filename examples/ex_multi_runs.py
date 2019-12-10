#!/usr/bin/env python

#------------------------------

from __future__ import print_function
import os
import sys
import psana
import numpy as np
from time import time, localtime, strftime

#------------------------------

def test_multiruns() :

    SKIP   = 0
    EVENTS = 100

    dsname = 'exp=cxi11216:run=9,11,12:smd'
    src = 'CxiEndstation.0:Jungfrau.0'

    ds  = psana.DataSource(dsname)
    env = ds.env()

    t0_sec = time()

    # Loop over runs

    nruns = 0

    for irun, run in enumerate(ds.runs()):
        print('%s\nRun %d' % (50*'=', run.run()))
        nruns += 1
        
        # Loop over calibcycles
        nclc = 0
        for istep, step in enumerate(run.steps()):
            env = step.env()
            print('  Calibcycle %d'%(istep))
            nclc += 1

            # Loop over events
            for i, evt in enumerate(step.events()):
            
                if i<SKIP : continue
                if not i<EVENTS : break
                #if not ecm.select(evt) : continue 
                if not (i%10) : print('  Event %4d,  time=%7.3f sec' % (i, time()-t0_sec))

            print('# processed events %d in calibcycle %d' % (i, nclc))
            
        print('# calibcycles %d in run %d' % (nclc, run.run()))

    print('# runs processed %d' % nruns)

#------------------------------

if __name__ == "__main__" :
    #if len(sys.argv)==1 : print '\n%s' % usage(2)
    test_multiruns()
    sys.exit(0)

#------------------------------
