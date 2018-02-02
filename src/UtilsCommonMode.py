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

import numpy as np
from math import fabs
#from time import time
#from Detector.GlobalUtils import print_ndarr, divide_protected

def common_mode_rows(arr, mask=None, cormax=None, npix_min=10) :
    """Defines and applys common mode correction to 2-d arr and mask in loop for rows.
    """
    rows, cols = arr.shape

    if mask is None :
        for r in range(rows) :
            cmode = np.median(arr[r,:])
            if cormax is None or fabs(cmode) < cormax :
                arr[r,:] -= cmode
    else :
        arr1 = np.ones_like(arr, dtype=np.int16)
        for r in range(rows) :
            bmask = mask[r,:]>0
            npix = arr1[r,:][bmask].sum()
            if npix < npix_min : continue
            cmode = np.median(arr[r,:][bmask])
            #if npix != 512 : print '  XXX:row:%3d npix:%3d cmode:%.1f' % (r,npix,cmode)
            if cormax is None or fabs(cmode) < cormax :
                #arr[r,:][bmask] -= cmode
                arr[r,:] -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_cols(arr, mask=None, cormax=None, npix_min=10) :
    """Defines and applys common mode correction to 2-d arr using the same shape mask in loop for cols.
    """
    rows, cols = arr.shape
    #print_ndarr(arr, 'XXX.common_mode_cols.arr')

    if mask is None :
        for c in range(cols) :
            cmode = np.median(arr[:,c])
            if cormax is None or fabs(cmode) < cormax :
                arr[:,c] -= cmode
    else :
        arr1 = np.ones_like(arr, dtype=np.int16)
        for c in range(cols) :
            bmask = mask[:,c]>0
            npix = arr1[:,c][bmask].sum()
            if npix < npix_min : continue
            cmode = np.median(arr[:,c][bmask])
            if cormax is None or fabs(cmode) < cormax :
                #arr[:,c][bmask] -= cmode
                arr[:,c] -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_2d(arr, mask=None, cormax=None, npix_min=10) :
    """Defines and applys common mode correction to entire 2-d arr using the same shape mask. 
    """
    if mask is None :
        cmode = np.median(arr)
        if cormax is None or fabs(cmode) < cormax :
            arr -= cmode
    else :
        arr1 = np.ones_like(arr, dtype=np.int16)
        bmask = mask>0
        npix = arr1[bmask].sum()
        if npix < npix_min : return
        cmode = np.median(arr[bmask])
        if cormax is None or fabs(cmode) < cormax :
            #arr[bmask] -= cmode
            arr -= cmode # apply correction to all pixels in the group

#------------------------------

def common_mode_rows_hsplit_nbanks(data, mask, nbanks=4, cormax=None) :
    """Works with 2-d data and mask numpy arrays,
       hsplits them for banks (df. nbanks=4),
       for each bank applies median common mode correction for pixels in rows,
       hstack banks in array of original data shape and copy results in i/o data 
    """
    bdata = np.hsplit(data, nbanks)

    if mask is None :
        for b in bdata :
            common_mode_rows(b, None, cormax)
    else :
        bdata = np.hsplit(data, nbanks)
        bmask = np.hsplit(mask, nbanks)
        for b,m in zip(bdata,bmask) :
            common_mode_rows(b, m, cormax)
    data[:] = np.hstack(bdata)[:]    

#------------------------------

def common_mode_2d_hsplit_nbanks(data, mask, nbanks=4, cormax=None) :
    """Works with 2-d data and mask numpy arrays,
       hsplits them for banks (df. nbanks=4),
       for each bank applies median common mode correction for all pixels,
       hstack banks in array of original data shape and copy results in i/o data 
    """
    bdata = np.hsplit(data, nbanks)
    if mask is None :
        for b in bdata :
            common_mode_rows(b, None, cormax)
    else :
        bmask = np.hsplit(mask, nbanks) if mask is not None else None
        for b,m in zip(bdata,bmask) :
            common_mode_2d(b, m, cormax)
    data[:] = np.hstack(bdata)[:]    

#------------------------------
