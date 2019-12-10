from __future__ import print_function
from psana import *
import numpy as np

from time import time, strftime

import pyimgalgos.GlobalUtils as gu

#import matplotlib.pyplot as pl
#import h5py, argparse

runnum = 132

# Open data source and detector
ds = DataSource('exp=sxrlq7615:run='+str(runnum)+':smd')
#acq = Detector('Acq01')
pnccd = Detector('pnccd')
#pnccd.set_print_bits(0177777)

#from Detector.AreaDetector import AreaDetector    
#pnccd = AreaDetector('pnccd', ds.env(), pbits=0177777)

# Loop over events
print('Starting Run '+str(runnum)+' at:'+strftime('%b-%d %H:%M:%S'))

img = np.zeros((4,512,512))

peds = None
gain = None
mask = None

for ne,evt in enumerate(ds.events()):
    if ne % 10 == 0: print('Event %4d'%ne)
    if ne >= 500: break

    if peds is None : 
        peds = pnccd.pedestals(evt)
        if peds is None : 
            print('Event %4d: pnccd pedestals are not defined yet...' % ne)
            continue
        else :
            gu.print_ndarr(peds, 'pedestals')
            ofn = 'test-pedestals.npy'
            np.save(ofn, peds)
            print('Saved file %s' % ofn)


    if gain is None : 
        gain = pnccd.gain(evt)
        if gain is None : 
            print('Event %4d: pnccd pixel_gain is not defined yet...' % ne)
            continue
        else :
            gu.print_ndarr(gain, 'gain')
            ofn = 'test-gain.npy'
            np.save(ofn, gain)
            print('Saved file %s' % ofn)


    if mask is None : 
        #mask = pnccd.mask(evt)
        mask = pnccd.mask(evt, calib=False, status=True)
        if mask is None : 
            print('Event %4d: pnccd mask is not defined yet...' % ne)
            continue
        else :
            gu.print_ndarr(mask, 'mask')
            ofn = 'test-mask.npy'
            np.save(ofn, mask)
            print('Saved file %s' % ofn)


    print('YYY:test-pnccd A', 50*'_')
    t0_sec = time()

    #if acq.waveform(evt) is None: print('No Acqiris')
    test = (pnccd.raw(evt) - peds)*gain

    #test = pnccd.common_mode_correction(evt, test)
    #print 'mean common mode correction %.3f' % test.mean()
    #test = pnccd.calib(evt)

    #test = pnccd.photons(evt, adu_per_photon=1250)

    test = pnccd.photons(evt, nda_calib=test, mask=mask, adu_per_photon=1250, thr_fraction=0.9)

    print('YYY:test-pnccd B : pnccd.photons time(sec) =', time()-t0_sec)


    if test is None: 
        print('No pnccd')
        continue

    img += test

print('Completed Run '+str(runnum)+' at:'+strftime('%b-%d %H:%M:%S'))

ofn = 'test-ave.npy'
np.save(ofn,img)
print('Saved file %s' % ofn)
