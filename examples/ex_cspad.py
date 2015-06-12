#!/usr/bin/env python

import sys
import psana
import numpy as np
from Detector.PyDetector import PyDetector
import Detector.PyDataAccess as pda

dsname, src = 'exp=cxif5315:run=169', psana.Source('DetInfo(CxiDs2.0:Cspad.0)')
print 'Example for\n  dataset: %s\n  source : %s' % (dsname, src)

# Use non-standard calib directory
#opts = {'psana.calib-dir':'./calib',}
#psana.setOptions(opts)
#psana.setOption('psana.calib-dir', './calib')
#psana.setOption('psana.calib-dir', './empty/calib')

ds  = psana.DataSource(dsname)
evt = ds.events().next()
env = ds.env()

#for key in evt.keys() : print key

##-----------------------------

def print_ndarr(nda, name='', first=0, last=5) :
    if nda is None : print '%s\n%s: %s' % (80*'_', name, nda)
    else           : print '%s\n%s: \n%s...\n shape:%s  size:%d  dtype:%s' % \
         (80*'_', name, nda.flatten()[first:last], str(nda.shape), nda.size, nda.dtype)

##-----------------------------

def raw_data_cspad(evt, env, src) :
    # data object
    d = pda.get_cspad_data_object(evt, src)
    if d is None : return None
    print 'd.TypeId: ', d.TypeId

    # configuration from data
    c = pda.get_cspad_config_object(env, src)
    if d is None : return None

    nquads_d = d.quads_shape()[0]
    nquads_c = c.numQuads()
    print 'nquads in data: %d and config: %d' % (nquads_d, nquads_c)

    nquads = nquads_d

    arr = []
    for iq in range(nquads) :
        q = d.quads(iq)
        qnum = q.quad()
        qdata = q.data()
        #n2x1stored = qdata.shape[0]
        roim = c.roiMask(qnum)
        print 'qnum: %d  qdata.shape: %s, mask: %d' % (qnum, str(qdata.shape), roim)
        #     '  n2x1stored: %d' % (n2x1stored)

        #roim = 0355 # for test only

        if roim == 0377 : arr.append(qdata)
        else :
            qdata_full = np.zeros((8,185,388), dtype=qdata.dtype)
            i = 0
            for s in range(8) :
                if roim & (1<<s) :
                    qdata_full[s,:] = qdata[i,:]
                    i += 1
            arr.append(qdata_full)

    nda = np.array(arr)
    print 'nda.shape: ', nda.shape
    nda.shape = (32,185,388)
    return nda

##-----------------------------

raw_data_cspad(evt, env, src)

sys.exit(0)

##-----------------------------
