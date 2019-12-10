#!/usr/bin/env python
##-----------------------------

from __future__ import print_function
import sys
import psana
import numpy as np

from Detector.GlobalUtils import print_ndarr
from time import time

##-----------------------------

quad = int(sys.argv[1]) if len(sys.argv)>1 else 0
if quad<0 : quad = 0
if quad>3 : quad = 3
print('CSPAD Quad # %d' % quad)

##----------------------------- init

#dsname, src = 'exp=mecj5515:run=99', 'MecTargetChamber.0:Cspad.0'

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/alignment/cspad/calib-mec-2015-06-08/calib')
dsname, src = '/reg/g/psdm/detector/data_test/types/0004-MecTargetChamber.0-Cspad.0-three-quads.xtc', 'MecTargetChamber.0:Cspad.0'

ds  = psana.DataSource(dsname)
env = ds.env()
evt = next(ds.events())
rnum = evt.run()
#calibdir = env.calibDir()
#print evt.keys()

det = psana.Detector(src, env)

# get geometry object
#geo = det.pyda.geoaccess(rnum) # for  ana-0.17.5
geo = det.geometry(rnum)        # for >ana-0.17.5

# get pixel index array for quad, shape=(8, 185, 388)
iX, iY = geo.get_pixel_coord_indexes('QUAD:V1', quad)
print_ndarr(iX, 'iX')
print_ndarr(iY, 'iY')

##----------------------------- evt

t0_sec = time()

nda = det.raw(evt)

print('Consumed time = %7.3f sec' % (time()-t0_sec))
print_ndarr(nda, 'raw')

if nda is None :
    sys.exit('Exit: DO NOT plot anything for nda=None...')

# get intensity array for quad, shape=(8, 185, 388)
nda.shape = (4, 8, 185, 388)
ndaq = nda[quad,:]
print_ndarr(ndaq, 'nda[%d,:]'%quad)

##----------------------------- img

#img = det.image(rnum, nda)

# reconstruct image for quad
from PSCalib.GeometryAccess import img_from_pixel_arrays
img = img_from_pixel_arrays(iX, iY, W=ndaq)

##----------------------------- plot img

import pyimgalgos.GlobalGraphics as gg
ave, rms = ndaq.mean(), ndaq.std()
gg.plotImageLarge(img, amp_range=(ave-rms, ave+5*rms))
gg.show()

##-----------------------------

sys.exit('End of test %s' % sys.argv[0])

##-----------------------------
