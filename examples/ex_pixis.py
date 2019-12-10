from __future__ import print_function
#------------------------------
#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc
#EventKey(type=psana.Pixis.FrameV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc -m2
#EventKey(type=None, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#EventKey(type=psana.Pixis.ConfigV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')

#event_keys -d exp=mecdaq115:run=174
#EventKey(type=psana.Pixis.FrameV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#event_keys -d exp=mecdaq115:run=174 -m2
#EventKey(type=None, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#EventKey(type=psana.Pixis.ConfigV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#------------------------------

from time import time
import psana
import sys
from Detector.GlobalUtils import print_ndarr

npars=len(sys.argv)
print('%s npars:%d' % (sys.argv[0], npars)) 
#dsname = '/reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc' if npars==1 else sys.argv[1]
#dsname = 'exp=mecdaq115:run=174' if npars==1 else sys.argv[1]
dsname = '/reg/g/psdm/detector/data_test/types/0026-MecTargetChamber.0-Pixis.1.xtc' if npars==1 else sys.argv[1]
srcname = 'MecTargetChamber.0:Pixis.1'      if npars<3  else sys.argv[2]
print('Test of dsname: %s  srcname: %s' % (dsname, srcname))

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/') # '/reg/d/psdm/det/mecdaq115/calib'

ds = psana.DataSource(dsname)
det = psana.Detector(srcname)
evt = None
for i, evt in enumerate(ds.events()) :
    if i>10 : break
    raw = det.raw(evt)
    if raw is None:
        print(i, 'None')
    else:
        print_ndarr(raw, 'Event %3d: raw' % i)

#------------------------------

rnum = evt.run()
print('\nGet calib arrays for run %d' % rnum)
print('det.shape: ', det.shape())
print_ndarr(det.pedestals(rnum),   'det.pedestals  ')
print_ndarr(det.rms(rnum),         'det.rms        ')
print_ndarr(det.status(rnum),      'det.status     ')
print_ndarr(det.common_mode(rnum), 'det.common_mode')

t0_sec = time()
calib = det.calib(evt) #, cmpars=0)
dt_sec = time() - t0_sec
print_ndarr(calib, 'det.calib      ')
print('calib time = %.3f sec' % (dt_sec))

#------------------------------
