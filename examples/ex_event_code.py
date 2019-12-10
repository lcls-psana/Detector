#!/usr/bin/env python

from __future__ import print_function
import sys
import psana
from time import time
from Detector.EvrDetector import EvrDetector

##-----------------------------

def test_event_code() : 
    """get and print list of event codes"""

    ds = psana.DataSource('exp=xpptut15:run=54')
    evrdet = EvrDetector(':Evr')

    for i, evt in enumerate(ds.events()):
        print('Event %3d codes:' % i, evrdet.eventCodes(evt))
        if i>10 : break

##-----------------------------

def test_event_code_raw() : 
    """get and print list of event codes"""

    #dsname = 'exp=mfxc0116:run=56'
    dsname = '/reg/g/psdm/detector/data_test/types/0014-MfxEndstation.0-Rayonix.0.xtc'
    ds = psana.DataSource(dsname)
    src = psana.Source(':Evr') # 'DetInfo(NoDetector.0:Evr.0)'

    for i, evt in enumerate(ds.events()):
        o = evt.get(psana.EvrData.DataV4, src)
        if   o is None : o = evt.get(psana.EvrData.DataV3, src)
        elif o is None : print('EvrData.DataV4,3 is not found in event %d' % i)

        lst_ec  = [eco.eventCode() for eco in o.fifoEvents()]
        print('Event %3d codes:' % i, lst_ec)
        if i>10 : break

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print('Test # %d' % ntest)
if   ntest==1 : test_event_code()
if   ntest==2 : test_event_code_raw()
sys.exit(0)

##-----------------------------
