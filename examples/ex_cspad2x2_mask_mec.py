#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana
import numpy as np

from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

detnum = int(sys.argv[1]) if len(sys.argv)>1 else 1
if detnum<1 : detnum = 0
if detnum>4 : detnum = 4
print('CSPAD2x2 Detnum # %d' % detnum)

##----------------------------- init

#dsname, src = 'exp=mecj5515:run=99', 'MecTargetChamber.0:Cspad.0'

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad2x2/calib-cspad2x2-01-2013-02-13/calib')
dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc', 'MecTargetChamber.0:Cspad2x2.%1d' % detnum

ds  = psana.DataSource(dsname)
env = ds.env()
evt = ds.events().next()
rnum = evt.run()

calibdir = env.calibDir()
#print evt.keys()

det = psana.Detector(src, env)

print('dsname     : %s' % dsname)
print('calibdir   : %s' % calibdir)
print('src        : %s' % src)
print('Run number : %d' % rnum)

##----------------------------- evt

t0_sec = time()
nda = det.calib(evt, mbits=0377)

print('Consumed time = %7.3f sec' % (time()-t0_sec))
print_ndarr(nda, 'raw')

if nda is None :
    sys.exit('Exit: DO NOT plot anything for nda=None...')

##----------------------------- img

img = det.image(evt, nda)
print_ndarr(img, 'img')

##----------------------------- plot img

import pyimgalgos.GlobalGraphics as gg
ave, rms = nda.mean(), nda.std()
gg.plotImageLarge(img, amp_range=(ave-rms, ave+5*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
