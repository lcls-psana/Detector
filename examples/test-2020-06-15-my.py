import psana
import numpy as np
import time
import matplotlib.pyplot as plt

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname).1s] %(message)s', level=logging.DEBUG)

from Detector.UtilsEpix10ka import find_gain_mode
from Detector.GlobalUtils import print_ndarr

#'/reg/d/psdm/xcs/xcslt4017/calib/Epix10ka2M::CalibV1/XcsEndstation.0:Epix10ka2M.0/pedestals/231-end.data'

#ds = psana.DataSource('exp=xcslt4017:run=357')
ds = psana.DataSource('exp=xcsx35617:run=421')
run = ds.runs().next()
det = psana.Detector('epix10ka2m')
#times = run.times()
env = ds.env()

peds = None
mask = None
gain = None

for evt in run.events():
    #evt = run.event(i)
    raw = det.raw(evt)
    if raw is None: continue
    print_ndarr(raw, 'raw')

    if peds is None:
       peds = det.pedestals(evt)[2].astype(np.uint16)
       print_ndarr(peds, 'peds')
    if mask is None:
       mask = det.status_as_mask(evt)
       print_ndarr(mask, 'mask')
    if gain is None:
       gain = det.gain(evt)[2]
       print_ndarr(gain, 'gain')

    print 'gain mode:', find_gain_mode(det, raw)

    calib = det.calib(evt, cmpars=(0, 0, 100), nda_raw=peds)
    img1 = det.image(evt, calib)
    ave, rms = img1.mean(), img1.std()
    imsh = plt.imshow(img1) #, norm=LogNorm())
    #imsh.set_clim(ave-1*rms, ave+5*rms)
    #imsh.set_clim(3000, 4000)
    imsh.set_clim(-10, 10)
    #plt.colorbar()
    plt.show()
    exit()
