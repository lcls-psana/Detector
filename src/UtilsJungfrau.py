#------------------------------
""":py:class:`UtilsJungfrau` contains utilities for Jungfrau detector correction.

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
from math import fabs
from Detector.GlobalUtils import print_ndarr

BW1 =  040000 # 16384 or 1<<14 (15-th bit starting from 1)
BW2 = 0100000 # 32768 or 2<<14 or 1<<15
BW3 = 0140000 # 49152 or 3<<14
MSK =  0x3fff # 16383 or (1<<14)-1 - 14-bit mask
#MSK =  037777 # 16383 or (1<<14)-1

#------------------------------

def calib_jungfrau(det, evt, src, cmpars=(7,3,100)) :
    """
    Parameters

    - det (psana.Detector) - Detector object
    - evt (psana.Event)    - Event object
    - src (psana.Source)   - Source object
    - cmpars (tuple) - common mode parameters 
        - cmpars[0] - algorithm # 7-for jungfrau
        - cmpars[1] - control bit-word 1-in rows, 2-in columns
        - cmpars[2] - maximal applied correction 
    """
    arr  = det.raw(evt) # shape:(1, 1024, 512) dtype:uint16
    #arr  = np.array(det.raw(evt), dtype=np.float32)
    peds = det.pedestals(evt) # - 4d pedestals shape:(3, 1, 1024, 512) dtype:float32

    #mask = det.status_as_mask(evt, mode=0) # - 4d mask

    gain = det.gain(evt)      # - 4d gains
    offs = det.offset(evt)    # - 4d offset
    cmp  = det.common_mode(evt) if cmpars is None else cmpars
    if gain is None : gain = np.ones_like(peds)  # - 4d gains
    if offs is None : offs = np.zeros_like(peds) # - 4d gains

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
    arrf[gr0]-= peds[0,gr0]
    arrf[gr1] = peds[1,gr1] - arrf[gr1]
    arrf[gr2] = peds[2,gr2] - arrf[gr2]

    #t0_sec = time()
    if cmp is not None :
      mode, cormax = int(cmp[1]),cmp[2] 
      #common_mode_2d(arrf, mask=gr0, cormax=cormax)
      for s in range(arrf.shape[0]) :
          if mode & 1 :
            #common_mode_rows(arrf[s,], mask=gr0[s,], cormax=cormax)
            common_mode_rows(arrf[s,:,:256], mask=gr0[s,:,:256], cormax=cormax)
            common_mode_rows(arrf[s,:,256:], mask=gr0[s,:,256:], cormax=cormax)
            #common_mode_cols(arrf[s,:512,:], mask=gr0[s,:512,:], cormax=cormax)
          if mode & 2 :
            common_mode_cols(arrf[s,], mask=gr0[s,], cormax=cormax)
    #print '\nXXX: CM consumed time (sec) =', time()-t0_sec # 90-100msec total

    # Apply gain and offset
    #gri = gr0*0 + gr1*1 + gr2*2
    ####a = gain[0,gr0] + gain[1,gr1] + gain[2,gr2]
    ####b = offs[0,gr0] + offs[1,gr1] + offs[2,gr2]
    #a = gain[gri]
    #b = offs[gri]

    #t0_sec = time()
    #print '\nXXX: Consumed time (sec) =', time()-t0_sec # 7msec

    #a = gain[0,:]*gr0 + gain[1,:]*gr1 + gain[2,:]*gr2 # 3.5 msec
    #b = offs[0,:]*gr0 + offs[1,:]*gr1 + offs[2,:]*gr2

    a = np.select((gr0, gr1, gr2), (gain[0,:], gain[1,:], gain[2,:]), default=1) # 2msec
    b = np.select((gr0, gr1, gr2), (offs[0,:], offs[1,:], offs[2,:]), default=0)

    #print_ndarr(a, 'XXX: calib_jungfrau a')
    #print_ndarr(b, 'XXX: calib_jungfrau b')

    return a*arrf + b # 1msec

#------------------------------

def common_mode_rows(arr, mask=None, cormax=None) :
    """Defines and applys common mode correction to 2-d arr using the same shape mask in loop for rows.
    """
    rows, cols = arr.shape
    #print 'XXX.common_mode_rows.arr.shape', arr.shape

    for r in range(rows) :
        cmode = 0
        cmode = np.median(arr[r,:][mask[r,:]]) if mask is not None else\
                np.median(arr[r,:])

        #print 'XXX.common_mode_2 cmode=%.3f, len(selected arr)=%d' % (cmode, len(arr[r,:][mask[r,:]]))

        if cormax is None or fabs(cmode) < cormax :
            if mask is not None : arr[r,:][mask[r,:]] -= cmode
            else : arr[r,:] -= cmode
        else :
            return 

#------------------------------

def common_mode_cols(arr, mask=None, cormax=None) :
    """Defines and applys common mode correction to 2-d arr using the same shape mask in loop for cols.
    """
    rows, cols = arr.shape
    #print 'XXX.common_mode_cols.arr.shape', arr.shape

    for c in range(cols) :
        cmode = 0
        cmode = np.median(arr[:,c][mask[:,c]]) if mask is not None else\
                np.median(arr[:,c])

        #print 'XXX.common_mode_2 cmode=%.3f, len(selected arr)=%d' % (cmode, len(arr[:,c][mask[:,c]]))

        if cormax is None or fabs(cmode) < cormax :
            if mask is not None : arr[:,c][mask[:,c]] -= cmode
            else : arr[:,c] -= cmode
        else :
            return 

#------------------------------

def common_mode_2d(arr, mask=None, cormax=None) :
    """Defines and applys common mode correction to entire 2-d arr using the same shape mask. 
    """
    cmode = 0
    cmode = np.median(arr[mask>0]) if mask is not None else\
            np.median(arr)

    #print 'XXX.common_mode_2 cmode=%.3f, len(selected arr)=%d' % (cmode, len(arr[mask>0]))

    if cormax is None or fabs(cmode) < cormax :
        if mask is not None : arr[mask>0] -= cmode
        else : arr -= cmode
    else :
        return 

#------------------------------

def common_mode_jungfrau(frame) :
    """
    Parameters

    - frame (np.array) - shape=(1024, 512)
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
                cmode = np.median(frame[r, col0:col0+bsize][frame[r, col0:col0+bsize]<intmax])
                if not np.isnan(cmode):
                    ## e.g. found no pixels below intmax
                    ##                    print r, cmode, col0, b, bsize
                    if cmode<intmax-1 :
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
