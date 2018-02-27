#------------------------------

# event_keys -d exp=mfxx32516:run=5 -n 50
# shape=(352, 384)
# Example of code for ipython
# /reg/d/psdm/MFX/mfxx32516/calib/
# /reg/d/psdm/MFX/mfxx32516/xtc/

#------------------------------

import psana
import sys
from Detector.GlobalUtils import print_ndarr

dsname = 'exp=mfxx32516:run=377' if len(sys.argv)==1 else sys.argv[1]
srcname = 'MfxEndstation.0:Epix10ka.0' # 'Epix10ka'
print 'Test of dsname: %s  srcname: %s' % (dsname, srcname)

ds = psana.DataSource(dsname)
det = psana.Detector(srcname)
evt = None
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print i, 'None'
    else:
        print_ndarr(raw, 'Event %3d: raw' % i)

#------------------------------

rnum = evt.run()
print '\nGet calib arrays for run %d' % rnum
peds = det.pedestals(rnum)
print_ndarr(peds, 'det.pedestals')

cmode = det.common_mode(rnum)
print_ndarr(cmode, 'det.common_mode')

#------------------------------

