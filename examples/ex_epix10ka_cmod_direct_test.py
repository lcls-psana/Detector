#!/usr/bin/env python

import logging
logger = logging.getLogger(__name__)
logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d : %(message)s', level=logging.INFO) # INFO) #DEBUG

import sys
import numpy as np
from time import time
import Detector.UtilsCommonMode as ucm

from pyimgalgos.NDArrGenerators import random_standard
from pyimgalgos.GlobalUtils import print_ndarr

##-----------------------------

ntest = int(sys.argv[1]) if len(sys.argv)>1 else 1
print 'Test # %d' % ntest
print 80*'_'
        
fname = '/reg/g/psdm/detector/data2_test/misc/img-detdaq18-r23-epix10ka-raw-peds-for-cmtest.txt'
print('load array from file: %s' % fname)
raw = np.loadtxt(fname)
print_ndarr(raw, 'raw')
img = np.array(raw)

CORMAX=100

t0_sec = time()

def print_comment(ntest=None) :
    s = ''#test %s' % str(ntest)
    if ntest in (0,None): s+='\n  0-random mask'
    if ntest in (1,None): s+='\n  1-raw data'
    if ntest in (2,None): s+='\n  2-common_mode_cols for mask=None   (3 msec)'
    if ntest in (3,None): s+='\n  3-common_mode_cols for random mask (12 msec)'
    if ntest in (4,None): s+='\n  4-transposed raw data'
    if ntest in (5,None): s+='\n  5-transposed -common_mode_rows for mask=None   (3 msec)'
    if ntest in (6,None): s+='\n  6-transposed -common_mode_rows for random mask (12 msec)'
    print s

print_comment(ntest)

if ntest==0 : # random mask
    ones = np.ones_like(img, dtype=np.int16)
    ranarr = random_standard(shape=img.shape, mu=0, sigma=1, dtype=np.float)
    mask = np.select((ranarr>-1,), (ones,), default=0)
    img = mask

# TESTS FOR COLUMNS
elif ntest==1 : # raw data from file
    pass

elif ntest==2 : # common mode correction in columns common_mode_cols
    hrows = img.shape[0]/2
    ucm.common_mode_cols(img[hrows:,:], mask=None, cormax=CORMAX)

elif ntest==3 : # common mode correction in columns common_mode_cols
    hrows = img.shape[0]/2
    ones = np.ones_like(img, dtype=np.int16)
    ranarr = random_standard(shape=img.shape, mu=0, sigma=1, dtype=np.float)
    mask = np.select((ranarr>-1,), (ones,), default=0)
    ucm.common_mode_cols(img[:hrows,:], mask=mask[:hrows,:], cormax=CORMAX)

# TESTS FOR RAWS ON TRANSPOSED raw
elif ntest==4 : # transposed raw data from file
    img = img.T

elif ntest==5 : # common mode correction in rows common_mode_rows
    img = img.T
    hcols = img.shape[1]/2
    ucm.common_mode_rows(img[:,:hcols], mask=None, cormax=CORMAX)

elif ntest==6 : # common mode correction in rows common_mode_rows
    img = img.T
    hcols = img.shape[1]/2
    ones = np.ones_like(img, dtype=np.int16)
    ranarr = random_standard(shape=img.shape, mu=0, sigma=1, dtype=np.float)
    mask = np.select((ranarr>-1,), (ones,), default=0)
    ucm.common_mode_rows(img[:,hcols:], mask=mask[:,hcols:], cormax=CORMAX)

dt_sec = time()-t0_sec
print('test %d: common-mode correction consumed time (sec) = %.6f' % (ntest, dt_sec))
print_comment(None)

##-----------------------------

print_ndarr(img, 'img')

import pyimgalgos.GlobalGraphics as gg

ave, rms = img.mean(), img.std()
print 'ave=%.3f rms=%.3f' % (ave, rms)
amp_range=(ave-1*rms, ave+2*rms)
#amp_range=(-10, 25)
gg.plotImageLarge(img, amp_range=amp_range, cmap='jet')

#gg.save(fname='img.png', do_save=True, pbits=0377)

gg.show()

##-----------------------------

sys.exit(0)

##-----------------------------
