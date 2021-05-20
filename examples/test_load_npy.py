#!/usr/bin/env python
#------------------------------
"""
    python ~/LCLS/con-detector/Detector/examples/test_load_npz.py
"""

import numpy as np
from Detector.GlobalUtils import print_ndarr #, info_ndarr, divide_protected

if True:

        fname = 'mfxlx4219_0048_epix10k2M_mean.npy'
        npy=np.load(fname)
        print('Constants loaded from file: %s' % fname)
        print_ndarr(npy, 'npy')

        np.save('test.npy', npy)




