#------------------------------
"""
:py:class:`UtilsJungfrau` contains utilities for Jungfrau detector correction
=============================================================================

    Jungfrau gain range coding
    bit: 15,14,...,0   Gain range, ind
          0, 0         Normal,       0
          0, 1         ForcedGain1,  1
          1, 1         FixedGain2,   2

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2017-10-03 by Mikhail Dubrovin
"""
#------------------------------

import numpy as np
from time import time
#from math import fabs
from Detector.GlobalUtils import print_ndarr, divide_protected
from Detector.UtilsCommonMode import common_mode_rows, common_mode_cols, common_mode_2d

BW1 =  040000 # 16384 or 1<<14 (15-th bit starting from 1)
BW2 = 0100000 # 32768 or 2<<14 or 1<<15
BW3 = 0140000 # 49152 or 3<<14
MSK =  0x3fff # 16383 or (1<<14)-1 - 14-bit mask
#MSK =  037777 # 16383 or (1<<14)-1

#------------------------------

class Storage :
    def __init__(self) :
        self.offs = None
        self.gfac = None

#------------------------------
store = Storage() # singleton
#------------------------------

def calib_jungfrau(det, evt, src, cmpars=(7,3,100)) :
    """
    Returns calibrated jungfrau data

    - gets constants
    - gets raw data
    - evaluates (code - pedestal - offset)
    - applys common mode correction if turned on
    - apply gain factor

    Parameters

    - det (psana.Detector) - Detector object
    - evt (psana.Event)    - Event object
    - src (psana.Source)   - Source object
    - cmpars (tuple) - common mode parameters 
        - cmpars[0] - algorithm # 7-for jungfrau
        - cmpars[1] - control bit-word 1-in rows, 2-in columns
        - cmpars[2] - maximal applied correction 
    """

    arr  = det.raw(evt) # shape:(1, 512, 1024) dtype:uint16
    if arr is None : return None

    #arr  = np.array(det.raw(evt), dtype=np.float32)
    peds = det.pedestals(evt) # - 4d pedestals shape:(3, 1, 512, 1024) dtype:float32
    if peds is None : return None

    #mask = det.status_as_mask(evt, mode=0) # - 4d mask

    gain = det.gain(evt)      # - 4d gains
    offs = det.offset(evt)    # - 4d offset
    cmp  = det.common_mode(evt) if cmpars is None else cmpars
    if gain is None : gain = np.ones_like(peds)  # - 4d gains
    if offs is None : offs = np.zeros_like(peds) # - 4d gains

    gfac = store.gfac
    if store.gfac is None :
       store.gfac = gfac = divide_protected(np.ones_like(peds), gain)

    #print_ndarr(cmp,  'XXX: common mode parameters ')
    #print_ndarr(arr,  'XXX: calib_jungfrau arr ')
    #print_ndarr(peds, 'XXX: calib_jungfrau peds')
    #print_ndarr(gain, 'XXX: calib_jungfrau gain')
    #print_ndarr(offs, 'XXX: calib_jungfrau offs')

    # make bool arrays of gain ranges shaped as data
    #abit15 = arr & BW1 # ~0.5ms
    #abit16 = arr & BW2
    #gr0 = np.logical_not(arr & BW3) #1.6ms
    #gr1 = np.logical_and(abit15, np.logical_not(abit16))
    #gr2 = np.logical_and(abit15, abit16)

    #pro_den = np.select((den!=0,), (den,), default=1)

    # Define bool arrays of ranges
    # faster than bit operations
    gr0 = arr <  BW1              # 490 us
    gr1 =(arr >= BW1) & (arr<BW2) # 714 us
    gr2 = arr >= BW3              # 400 us

    #print_ndarr(gr0, 'XXX: calib_jungfrau gr0')
    #print_ndarr(gr1, 'XXX: calib_jungfrau gr1')
    #print_ndarr(gr2, 'XXX: calib_jungfrau gr2')

    # Subtract pedestals
    arrf = np.array(arr & MSK, dtype=np.float32)
    arrf[gr0] -= peds[0,gr0]
    arrf[gr1] -= peds[1,gr1] #- arrf[gr1]
    arrf[gr2] -= peds[2,gr2] #- arrf[gr2]

    #a = np.select((gr0, gr1, gr2), (gain[0,:], gain[1,:], gain[2,:]), default=1) # 2msec
    factor = np.select((gr0, gr1, gr2), (gfac[0,:], gfac[1,:], gfac[2,:]), default=1) # 2msec
    offset = np.select((gr0, gr1, gr2), (offs[0,:], offs[1,:], offs[2,:]), default=0)

    #print_ndarr(factor, 'XXX: calib_jungfrau factor')
    #print_ndarr(offset, 'XXX: calib_jungfrau offset')

    #print 'XXX calib_jungfrau cmp:', cmp

    # Apply offset
    arrf -= offset

    t0_sec = time()
    #if False :
    if cmp is not None :
      mode, cormax = int(cmp[1]), cmp[2]
      if mode>0 :
        #common_mode_2d(arrf, mask=gr0, cormax=cormax)
        for s in range(arrf.shape[0]) :
          if mode & 1 :
            common_mode_rows(arrf[s,], mask=gr0[s,], cormax=cormax)
          if mode & 2 :
            common_mode_cols(arrf[s,], mask=gr0[s,], cormax=cormax)

    #print '\nXXX: CM consumed time (sec) =', time()-t0_sec # 90-100msec total

    # Apply gain
    return arrf * factor

#------------------------------

def common_mode_jungfrau(frame, cormax) :
    """
    Parameters

    - frame (np.array) - shape=(512, 1024)
    """

    intmax = 100

    rows = 512
    cols = 1024
    banks = 4
    bsize = cols/banks

    for r in range(rows):
        col0 = 0
        for b in range(banks):
            try:
                cmode = np.median(frame[r, col0:col0+bsize][frame[r, col0:col0+bsize]<cormax])
                if not np.isnan(cmode):
                    ## e.g. found no pixels below intmax
                    ##                    print r, cmode, col0, b, bsize
                    if cmode<cormax-1 :
                        frame[r, col0:col0+bsize] -= cmode
            except:
                cmode = -666
                print "cmode problem"
                print frame[r, col0:col0 + bsize]
            col0 += bsize

#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------
