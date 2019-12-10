from __future__ import print_function
import psana
import numpy as np
import time
import matplotlib.pyplot as plt

experimentName = 'amok5415'
runNumber = '87'
detInfo = 'pnccdFront'

# 'exp=amok5415:run=87:idx'

ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = next(ds.runs())
det = psana.Detector(detInfo)
#det.set_print_bits(0377)

times = run.times()
env = ds.env()
eventTotal = len(times)
noEvts = len(times)

#det.do_reshape_2d_to_3d(flag=True)

for i in times:
    evt = run.event(i)
    calib = det.calib(evt)
    plt.subplot(221)
    plt.imshow(calib[0],interpolation='none',vmin=0,vmax=100)
    plt.subplot(222)
    plt.imshow(calib[1],interpolation='none',vmin=0,vmax=100)
    plt.subplot(223)
    plt.imshow(calib[2],interpolation='none',vmin=0,vmax=100)
    plt.subplot(224)
    plt.imshow(calib[3],interpolation='none',vmin=0,vmax=100)
    plt.show()       
    _img = det.image(evt)
    print("$$$$$: ", _img.shape)
    exit()

