#------------------------------
"""
:py:class:`UtilsCommonMode` contains detector independent utilities for common mode correction
==============================================================================================

Usage::

    from Detector.UtilsCommonMode import *
    #OR
    import Detector.UtilsCommonMode as ucm

    ucm.common_mode_rows(arr, mask=None, cormax=None, npix_min=10)
    ucm.common_mode_cols(arr, mask=None, cormax=None, npix_min=10)
    ucm.common_mode_2d(arr, mask=None, cormax=None, npix_min=10)
    ucm.common_mode_rows_hsplit_nbanks(data, mask, nbanks=4, cormax=None)
    ucm.common_mode_2d_hsplit_nbanks(data, mask, nbanks=4, cormax=None)

This software was developed for the LCLS project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-01-31 by Mikhail Dubrovin
"""
#------------------------------

import logging
logger = logging.getLogger(__name__)

import numpy as np
from math import fabs
from Detector.GlobalUtils import info_ndarr, print_ndarr #, divide_protected

#------------------------------

def common_mode_rows(arr, mask=None, cormax=None, npix_min=10):
    """Defines and applys common mode correction to 2-d arr for rows.
       I/O parameters:
       - arr (float) - i/o 2-d array of intensities
       - mask (int or None) - the same shape 2-d array of bad/good = 0/1 pixels
       - cormax (float or None) - maximal allowed correction in ADU
       - npix_min (int) - minimal number of good pixels in row to evaluate and apply correction
    """
    rows, cols = arr.shape
    if mask is None:
        cmode = np.median(arr,axis=1) # column of median values
    else:
        marr = np.ma.array(arr, mask=mask<0) # use boolean inverted mask (True for masked pixels)
        cmode = np.ma.median(marr,axis=1) # column of median values for masked array
        npix = mask.sum(axis=1) # count good pixels in each row
        #print('npix', npix[:100])
        cmode = np.select((npix>npix_min,), (cmode,), default=0)
    
    if cormax is not None:
        cmode = np.select((np.fabs(cmode) < cormax,), (cmode,), default=0)
    
    logger.debug(info_ndarr(cmode, 'cmode'))
    _,m2 = np.meshgrid(np.zeros(cols, dtype=np.int16), cmode) # stack cmode 1-d column to 2-d matrix
    arr -= m2

#------------------------------

def common_mode_rows_v0(arr, mask=None, cormax=None, npix_min=10):
    rows, cols = arr.shape
    if mask is None:
       for r in range(rows):
           cmode = np.median(arr[r,:])
           if cormax is None or fabs(cmode) < cormax:
               arr[r,:] -= cmode
    else:
      arr1 = np.ones_like(arr, dtype=np.int16)
      for r in range(rows):
          bmask = mask[r,:]>0
          npix = arr1[r,:][bmask].sum()
          if npix < npix_min: continue
          cmode = np.median(arr[r,:][bmask])
          #if npix != 512: print '  XXX:row:%3d npix:%3d cmode:%.1f' % (r,npix,cmode)
          if cormax is None or fabs(cmode) < cormax:
              #arr[r,:][bmask] -= cmode
              arr[r,:] -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_cols(arr, mask=None, cormax=None, npix_min=10):
    """Defines and applys common mode correction to 2-d arr for cols.
       I/O parameters:
       - arr (float) - i/o 2-d array of intensities
       - mask (int or None) - the same shape 2-d array of bad/good = 0/1 pixels
       - cormax (float or None) - maximal allowed correction in ADU
       - npix_min (int) - minimal number of good pixels in column to evaluate and apply correction
    """
    rows, cols = arr.shape
    if mask is None:
        cmode = np.median(arr,axis=0) # row of median values
    else:
        marr = np.ma.array(arr, mask=mask<0) # use boolean inverted mask (True for masked pixels)
        cmode = np.ma.median(marr,axis=0) # row of median values for masked array
        npix = mask.sum(axis=0) # count good pixels in each column
        cmode = np.select((npix>npix_min,), (cmode,), default=0)

    if cormax is not None:
        cmode = np.select((np.fabs(cmode) < cormax,), (cmode,), default=0)

    logger.debug(info_ndarr(cmode, 'cmode'))
    m1,_ = np.meshgrid(cmode, np.zeros(rows, dtype=np.int16)) # stack cmode 1-d row to 2-d matrix
    arr -= m1

#------------------------------

def common_mode_cols_v0(arr, mask=None, cormax=None, npix_min=10):
    """Defines and applys common mode correction to 2-d arr using the same shape mask in loop for cols.
    """
    rows, cols = arr.shape

    if mask is None:
        for c in range(cols):
            cmode = np.median(arr[:,c])
            if cormax is None or fabs(cmode) < cormax:
                arr[:,c] -= cmode
    else:
        arr1 = np.ones_like(arr, dtype=np.int16)
        for c in range(cols):
            bmask = mask[:,c]>0
            npix = arr1[:,c][bmask].sum()
            if npix < npix_min: continue
            cmode = np.median(arr[:,c][bmask])
            if cormax is None or fabs(cmode) < cormax:
                #arr[:,c][bmask] -= cmode
                arr[:,c] -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_2d(arr, mask=None, cormax=None, npix_min=10):
    """Defines and applys common mode correction to entire 2-d arr using the same shape mask. 
    """
    if mask is None:
        cmode = np.median(arr)
        if cormax is None or fabs(cmode) < cormax:
            arr -= cmode
    else:
        arr1 = np.ones_like(arr, dtype=np.int16)
        bmask = mask>0
        npix = arr1[bmask].sum()
        if npix < npix_min: return
        cmode = np.median(arr[bmask])
        if cormax is None or fabs(cmode) < cormax:
            #arr[bmask] -= cmode
            arr -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_rows_hsplit_nbanks(data, mask, nbanks=4, cormax=None):
    """Works with 2-d data and mask numpy arrays,
       hsplits them for banks (df. nbanks=4),
       for each bank applies median common mode correction for pixels in rows,
       hstack banks in array of original data shape and copy results in i/o data 
    """
    bdata = np.hsplit(data, nbanks)

    if mask is None:
        for b in bdata:
            common_mode_rows(b, None, cormax)
    else:
        bdata = np.hsplit(data, nbanks)
        bmask = np.hsplit(mask, nbanks)
        for b,m in zip(bdata,bmask):
            common_mode_rows(b, m, cormax)
    data[:] = np.hstack(bdata)[:]    

#------------------------------

def common_mode_2d_hsplit_nbanks(data, mask, nbanks=4, cormax=None):
    """Works with 2-d data and mask numpy arrays,
       hsplits them for banks (df. nbanks=4),
       for each bank applies median common mode correction for all pixels,
       hstack banks in array of original data shape and copy results in i/o data 
    """
    bdata = np.hsplit(data, nbanks)
    if mask is None:
        for b in bdata:
            common_mode_rows(b, None, cormax)
    else:
        bmask = np.hsplit(mask, nbanks) if mask is not None else None
        for b,m in zip(bdata,bmask):
            common_mode_2d(b, m, cormax)
    data[:] = np.hstack(bdata)[:]    

#------------------------------
