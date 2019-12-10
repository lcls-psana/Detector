from __future__ import print_function
#------------------------------

#event_keys -d exp=detdaq17:run=111
#EventKey(type=psana.Uxi.FrameV1, src='DetInfo(DetLab.0:Uxi.0)', alias='uxi')

#event_keys -d exp=detdaq17:run=111 -m2
#EventKey(type=None, src='DetInfo(DetLab.0:Uxi.0)', alias='uxi')
#EventKey(type=psana.Uxi.ConfigV1, src='DetInfo(DetLab.0:Uxi.0)', alias='uxi')

#------------------------------

from time import time
import psana
import sys
from Detector.GlobalUtils import print_ndarr

npars=len(sys.argv)
print('%s npars:%d' % (sys.argv[0], npars)) 
#dsname = 'exp=detdaq17:run=111' if npars==1 else sys.argv[1]
dsname = '/reg/g/psdm/detector/data_test/types/0027-DetLab.0-Uxi.0.xtc' if npars==1 else sys.argv[1]
srcname = 'DetLab.0:Uxi.0'      if npars<3  else sys.argv[2]
print('Test of dsname: %s  srcname: %s' % (dsname, srcname))

psana.setOption('psana.calib-dir', '/reg/g/psdm/detector/data_test/calib/') # '/reg/d/psdm/det/detdaq17/calib')

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
print_ndarr(det.common_mode(rnum), 'det.common_mode')
print_ndarr(det.pedestals(rnum),   'det.pedestals  ')
print_ndarr(det.rms(rnum),         'det.rms        ')
print_ndarr(det.status(rnum),      'det.status     ')
print_ndarr(det.common_mode(rnum), 'det.common_mode')

t0_sec = time()
calib = det.calib(evt)
dt_sec = time() - t0_sec
print_ndarr(det.calib(evt), 'det.calib      ')
print('calib time = %.3f sec' % (dt_sec))

#------------------------------

