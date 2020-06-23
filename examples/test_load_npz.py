#!/usr/bin/env python
#------------------------------
"""
    python ~/LCLS/con-detector/Detector/examples/test_load_npz.py
"""


#import os
#import sys
import numpy as np
#from time import time
from Detector.GlobalUtils import print_ndarr #, info_ndarr, divide_protected

if True:

        fname = '/reg/g/psdm/detector/data2_test/npy/epix10ka_0030_20200515204229_detdaq18_r0014_sp07_df.npz'
        npz=np.load(fname)

        print 'Constants loaded from file: %s' % fname

        #print 'npz:', npz
        print 'dir(npz):', dir(npz)
        print 'npz.items():', npz.items()

        darks  = getattr(npz.items(), 'darks', None)
        #darks  =npz['darks']
        fits_ml=npz['fits_ml']
        fits_hl=npz['fits_hl']

        print_ndarr(darks  , 'darks  ')
        print_ndarr(fits_ml, 'fits_ml')
        print_ndarr(fits_hl, 'fits_hl')
