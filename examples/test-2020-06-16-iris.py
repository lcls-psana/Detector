
import psana
import numpy as np
import matplotlib.pyplot as plt
from Detector.UtilsEpix10ka import find_gain_mode

ds = psana.DataSource('exp=xcsx35617:run=421:idx')
run = ds.runs().next()
det = psana.Detector('epix10ka2m')
peds = None
for enum, i in enumerate(run.times()):
    if enum > 5: break
    evt = run.event(i)
    raw = det.raw(evt)
    if raw is None: continue
    print raw.shape
    if peds is None:
        peds = det.pedestals(evt).astype('uint16')
        print peds.shape
    gm = find_gain_mode(det, raw) # returns string name of the gain mode
    print gm
    calib = det.calib(evt, cmpars=(0,0,100), nda_raw=peds[2])
    img = det.image(evt, calib)
    med = np.median(calib)
    spr = np.median(np.abs(calib-med))
    print 'median, spread:', med, spr
    plt.imshow(img, vmin=med-3*spr, vmax=med+3*spr)
    plt.colorbar()
    plt.show()
    print calib.shape
    print img.shape
    break
