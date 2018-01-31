#------------------------------
"""
:py:class:`UtilsPNCCD` contains utilities for PNCCD detector correction
=============================================================================

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-01-30 by Mikhail Dubrovin
"""
#------------------------------

from time import time
#import numpy as np
#from math import fabs
#from Detector.GlobalUtils import print_ndarr, divide_protected
from Detector.UtilsJungfrau import common_mode_rows, common_mode_cols #, common_mode_2d

#------------------------------

def common_mode_rows_128(data, mask, cormax) :
    """Works with pnccd ASIC data.shape=(512,512),
       splits it for 4 (512,128) banks,
       and for each bank applies median common mode correction in rows of 128 pixels.
    """
    #rows = 512
    cols = 512
    banks = 4
    bsize = cols/banks
    for bank in range(banks) :
        cbeg = bank * bsize
        cend = cbeg + bsize
        bmask = None if mask is None else mask[:,cbeg:cend]
        common_mode_rows(data[:,cbeg:cend], bmask, cormax)

#------------------------------

def common_mode_pnccd(data, mask, cmp=(8,1,500)) :

    t0_sec = time()
    if cmp is not None :
      mode, cormax = int(cmp[1]), cmp[2]
      if mode>0 :
        #common_mode_2d(data, mask=gr0, cormax=cormax)
        for s in range(data.shape[0]) :
          smask = None if mask is None else mask[s,]
          #print_ndarr(smask, '    segment: %d mask' % s)
          if mode & 1 :
            common_mode_rows_128(data[s,], mask=smask, cormax=cormax)
          if mode & 2 :
            common_mode_rows(data[s,], mask=smask, cormax=cormax)
          if mode & 4 :
            common_mode_cols(data[s,], mask=smask, cormax=cormax)

    print 'Detector.common_mode_pnccd: CM consumed time (sec) =', time()-t0_sec

#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------
