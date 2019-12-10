from __future__ import print_function
import psana
import numpy as np
import time
import matplotlib.pyplot as plt
from pyimgalgos.GlobalUtils import print_ndarr


experimentName = 'mfxls0816'
runNumber = '56'
detInfo = 'Jungfrau512k'

ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
times = run.times()
env = ds.env()
eventTotal = len(times)
noEvts = len(times)

det.do_reshape_2d_to_3d(flag=True)

for i in times:
    evt = run.event(i)
    calib = det.calib(evt)
    print_ndarr(calib, name='calib', first=0, last=5)
    img = det.image(evt,calib)
    print_ndarr(img, name='img', first=0, last=5)
    mask_roi = np.zeros_like(img)
    nda = det.ndarray_from_image(evt, mask_roi, pix_scale_size_um=None, xy0_off_pix=None)
    print(calib.shape, img.shape, nda.shape)
    exit()

