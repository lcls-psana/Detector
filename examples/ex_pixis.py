#------------------------------
#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc
#EventKey(type=psana.Pixis.FrameV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#event_keys -d /reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc -m2
#EventKey(type=None, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#EventKey(type=psana.Pixis.ConfigV1, src='DetInfo(MecTargetChamber.0:Pixis.1)', alias='pixis1')
#------------------------------

import psana
import sys
from Detector.GlobalUtils import print_ndarr

npars=len(sys.argv)
print '%s npars:%d' % (sys.argv[0], npars) 
dsname = '/reg/g/psdm/detector/data_test/xtc/mecdaq115-e993-r0174-s00-c00.xtc' if npars==1 else sys.argv[1]
srcname = 'MecTargetChamber.0:Pixis.1'      if npars<3  else sys.argv[2]
print 'Test of dsname: %s  srcname: %s' % (dsname, srcname)

ds = psana.DataSource(dsname)
det = psana.Detector(srcname)
evt = None
for i, evt in enumerate(ds.events()) :
    if i>10 : break
    raw = det.raw(evt)
    if raw is None:
        print i, 'None'
    else:
        print_ndarr(raw, 'Event %3d: raw' % i)

#------------------------------

rnum = evt.run()
print '\nGet calib arrays for run %d' % rnum
print 'det.shape: ', det.shape()
peds = det.pedestals(rnum)
print_ndarr(peds, 'det.pedestals')

#cmode = det.common_mode(rnum)
#print_ndarr(cmode, 'det.common_mode')

#------------------------------

