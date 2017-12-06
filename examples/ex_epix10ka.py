#------------------------------

# event_keys -d exp=mfxx32516:run=5 -n 50
# shape=(352, 384)
# Example of code for ipython

import psana
from Detector.GlobalUtils import print_ndarr

ds = psana.DataSource('exp=mfxx32516:run=5')
det = psana.Detector('MfxEndstation.0:Epix10ka.0') # 'Epix10ka'
evt = None
for i, evt in enumerate(ds.events()) :
    if i>100 : break
    raw = det.raw(evt)
    if raw is None:
        print i, 'None'
    else:
        print_ndarr(raw, 'Event %3d: raw' % i)

#------------------------------

