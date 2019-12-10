from __future__ import print_function
import psana
import numpy as np
import time
import matplotlib.pyplot as plt
import h5py
import os
from scipy import signal as sg
from skimage.measure import label, regionprops
from skimage import morphology

#experimentName = 'mfxlp4815'
#runNumber = '147'

experimentName = 'mfxlt3017' 
runNumber = '3'

detInfo = 'Rayonix'
evtNum = 0

ds = psana.DataSource('exp='+experimentName+':run='+runNumber+':idx')
run = ds.runs().next()
det = psana.Detector(detInfo)
#det.set_print_bits(0177777)
times = run.times()
env = ds.env()
eventTotal = len(times)
evt = run.event(times[evtNum])

print(det.dettype)



raw = det.raw(evt)
print(raw.shape)
print(('shape_config:', det.shape_config(env)))

calib = det.calib(evt)
print(calib.shape)

det.do_reshape_2d_to_3d(flag=True)

calib = det.calib(evt)
print(calib.shape)

#from Detector.PyDataAccess import get_rayonix_config_object
#c = get_rayonix_config_object(env, det.source)

c = env.configStore().get(psana.Rayonix.ConfigV2, det.source)
print('c.deviceID:', c.deviceID(), "See PyDetectorAccess.py shape=(7680,7680) if 'MX340' in c.deviceID() else (3840,3840)")  
