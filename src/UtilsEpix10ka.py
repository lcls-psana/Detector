
"""
:py:class:`UtilsEpix10ka` contains utilities for epix10ka and its composite detectors
=====================================================================================

Usage::
    from Detector.UtilsEpix10ka import ...


This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-11-14 by Mikhail Dubrovin
"""

import os
import numpy as np
from time import time

import logging
logger = logging.getLogger(__name__)

from Detector.PyDataAccess import get_epix_data_object, get_epix10ka_config_object,\
                                  get_epix10kaquad_config_object, get_epix10ka2m_config_object,\
                                  get_epix10ka_any_config_object
from Detector.GlobalUtils import print_ndarr, info_ndarr, divide_protected
from PSCalib.GlobalUtils import merge_masks

from Detector.UtilsCommonMode import common_mode_cols,\
                                     common_mode_rows_hsplit_nbanks, common_mode_2d_hsplit_nbanks

get_epix10ka_data_object = get_epix_data_object

# CALIB_REPO_EPIX10KA = '/reg/g/psdm/detector/gains/epix10k/panels'

#--------------------

GAIN_MODES    = ['FH','FM','FL','AHL-H','AML-M','AHL-L','AML-L']
GAIN_MODES_IN = ['FH','FM','FL','AHL-H','AML-M']

B14 = 0o40000 # 16384 or 1<<14 (15-th bit starting from 1)
B04 =    0o20 #    16 or 1<<4   (5-th bit starting from 1)
B05 =    0o40 #    32 or 1<<5   (6-th bit starting from 1)
M14 =  0x3fff # 16383 or (1<<14)-1 - 14-bit mask

#--------------------

class Storage:
    def __init__(self):
        self.arr1 = None
        self.gfac = None
        self.mask = None
        self.counter = -1

#--------------------
dic_store = {} # {det.name:Storage()} in stead of singleton
#--------------------

def config_objects(env, src, idx=0):
    """ Returns configuration objects for detector, quad, element; 
        dco,qco,eco (or None depending on detector) of types
        psana.Epix.Config10ka2MV1 or psana.Epix.Config10ka2MV1
        psana.Epix.Config10kaQuadV1 or psana.Epix.Config10kaQuadV2
        psana.Epix.Config10ka, psana.Epix.Config10kaV1, or psana.Epix.Config10kaV2
    """
    dco = get_epix10ka2m_config_object(env, src)
    if dco is not None: return dco, dco.quad(idx/4), dco.elemCfg(idx)

    qco = get_epix10kaquad_config_object(env, src)
    if qco is not None: return None, qco, qco.elemCfg(idx)

    eco = get_epix10ka_config_object(env, src)
    if eco is not None: return None, None, eco

    logger.warning('None of epics10ka/quad/2m configuration objects found for env:%s src:%s idx:%s'%\
                    (str(env), str(src), str(idx)))
    return None, None, None

#--------------------

def cbits_config_epix10ka(cob):
    """Returns array of control bits shape=(352, 384) from psana.Epix.Config10ka object
       get epix10ka per panel 4-bit pixel config array with bit assignment]
          0001 = 1<<0 = 1 - T test bit
          0010 = 1<<1 = 2 - M mask bit
          0100 = 1<<2 = 4 - g  gain bit
          1000 = 1<<3 = 8 - ga gain bit
          # add trbit
          010000 = 1<<4 = 16 - trbit
    """
    trbits = [cob.asics(i).trbit() for i in range(cob.numberOfAsics())] # 4 ASIC trbits, ex: [1,1,1,1]
    #logger.debug('In cbits_config_epix10ka cob: %s trbits: %s' %  (str(cob), str(trbits)))

    # begin to create array of control bits 
    pca = cob.asicPixelConfigArray()
    cbits = np.bitwise_and(pca,12) # 014 (bin:1100)

    # add trbit
    if all(trbits): cbits = np.bitwise_or(cbits, B04) # for all pixels (352, 384)
    elif not any(trbits): return cbits
    else: # set trbit per ASIC
        if trbits[2]: cbits[:176,:192] = np.bitwise_or(cbits[:176,:192], B04)
        if trbits[3]: cbits[176:,:192] = np.bitwise_or(cbits[176:,:192], B04)
        if trbits[0]: cbits[176:,192:] = np.bitwise_or(cbits[176:,192:], B04)
        if trbits[1]: cbits[:176,192:] = np.bitwise_or(cbits[:176,192:], B04)
    return cbits

#------------------------------

def cbits_config_epix10kaquad(qcob):
    """Returns array of control bits shape=(4, 352, 384) from psana.Epix.Config10kaQuadV1
    """
    lst_cbits = [cbits_config_epix10ka(qcob.elemCfg(i)) for i in range(qcob.numberOfElements())]
    cbits = np.stack(tuple(lst_cbits))
    #logger.debug('In cbits_config_epix10kaquad cob: %s numberOfElements: %d\n  %s'%\
    #              (str(qcob), qcob.numberOfElements(), info_ndarr(cbits, 'cbits for epix10kaquad')))
    return cbits

#--------------------

def cbits_config_epix10ka2m(dcob):
    """Returns array of control bits shape=(16, 352, 384) from psana.Epix.Config10ka2MV1 object
    """
    lst_cbits = [cbits_config_epix10ka(dcob.elemCfg(i)) for i in range(dcob.numberOfElements())]
    cbits = np.stack(tuple(lst_cbits))
    #logger.debug('In cbits_config_epix10ka2m cob: %s numberOfElements: %d\n %s'%\
    #              (str(dcob), dcob.numberOfElements(), info_ndarr(cbits, 'cbits for epix10ka2m')))
    return cbits
       
#--------------------

def cbits_config_epix10ka_any(env, src):
    """Returns array of control bits shape=(16, 352, 384) from any config object
    """
    cob = get_epix10ka2m_config_object(env, src)
    if cob is not None: return cbits_config_epix10ka2m(cob)

    cob = get_epix10kaquad_config_object(env, src)
    if cob is not None: return cbits_config_epix10kaquad(cob)

    cob = get_epix10ka_config_object(env, src)
    if cob is not None: return cbits_config_epix10ka(cob)

    return None

#--------------------

def cbits_total_epix10ka_any(det, data=None):
    """Returns array of control bits shape=(16, 352, 384) 
       from any config object and data array.
    """
    cbits = cbits_config_epix10ka_any(det.env, det.source)
    #logger.debug(info_ndarr(cbits, 'cbits', first, last))
    
    if cbits is None: return None

    #--------------------------------
    # get 5-bit pixel config array with bit assignments
    #   0001 = 1<<0 = 1 - T test bit
    #   0010 = 1<<1 = 2 - M mask bit
    #   0100 = 1<<2 = 4 - g  gain bit
    #   1000 = 1<<3 = 8 - ga gain bit
    # 010000 = 1<<4 = 16 - trbit 1/0 for H/M
    # add data bit
    # 100000 = 1<<5 = 32 - data bit 14
    #--------------------------------
    if data is not None:
        #logger.debug(info_ndarr(data, 'data', first, last))
        # get array of data bit 14 and add it as a bit 5 to cbits
        databit14 = np.bitwise_and(data, B14)
        databit05 = np.right_shift(databit14,9) # 040000 -> 040
        cbits = np.bitwise_or(cbits, databit05) # 109us
        #cbits[databit14>0] += 040              # 138us

    return cbits

#--------------------

def gain_maps_epix10ka_any(det, data=None):
    """Returns maps of gain groups shape=(16, 352, 384) 
    """
    cbits = cbits_total_epix10ka_any(det, data)
    if cbits is None: return None

    #--------------------------------
    # cbits - pixel control bit array
    #--------------------------------
    #   data bit 14 is moved here 1/0 for H,M/L
    #  / trbit  1/0 for H/M
    # V / bit3  1/0 for F/A
    #  V / bit2 1/0 for H,M/L
    #   V / M   mask
    #    V / T  test       gain range index
    #     V /             /  in calib files
    #      V             V 
    # x111xx =28 -  FH_H 0 
    # x011xx =12 -  FM_M 1 
    # xx10xx = 8 -  FL_L 2
    # 0100xx =16 - AHL_H 3
    # 0000xx = 0 - AML_M 4
    # 1100xx =48 - AHL_L 5
    # 1000xx =32 - AML_L 6
    #--------------------------------
    # 111100 =60 - cbitsM60 - mask 
    # 011100 =28 - cbitsM28 - mask 
    # 001100 =12 - cbitsM12 - mask 
    #--------------------------------

    cbitsM60 = cbits & 60 # control bits masked by configuration 3-bit-mask
    cbitsM28 = cbits & 28 # control bits masked by configuration 3-bit-mask
    cbitsM12 = cbits & 12 # control bits masked by configuration 2-bit-mask
    #logger.debug(info_ndarr(cbitsMCB, 'cbitsMCB', first, last))

    gr0 = (cbitsM28 == 28)
    gr1 = (cbitsM28 == 12)
    gr2 = (cbitsM12 ==  8)
    gr3 = (cbitsM60 == 16)
    gr4 = (cbitsM60 ==  0)
    gr5 = (cbitsM60 == 48)
    gr6 = (cbitsM60 == 32)

    #first = 10000; logger.debug(info_gain_mode_arrays(gr0, gr1, gr2, gr3, gr4, gr5, gr6, first, first+5))
        
    return gr0, gr1, gr2, gr3, gr4, gr5, gr6

#--------------------

def info_gain_mode_arrays1(gmaps, first=0, last=5):
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps
    return 'gain range arrays:\n  %s\n  %s\n  %s\n  %s\n  %s\n  %s\n  %s'%(\
        info_ndarr(gr0, 'gr0', first, last),\
        info_ndarr(gr1, 'gr1', first, last),\
        info_ndarr(gr2, 'gr2', first, last),\
        info_ndarr(gr3, 'gr3', first, last),\
        info_ndarr(gr4, 'gr4', first, last),\
        info_ndarr(gr5, 'gr5', first, last),\
        info_ndarr(gr6, 'gr6', first, last))

def info_gain_mode_arrays(gr0, gr1, gr2, gr3, gr4, gr5, gr6, first=0, last=5):
    """DEPRECATED"""
    return info_gain_mode_arrays1((gr0, gr1, gr2, gr3, gr4, gr5, gr6), first, last)

#--------------------

def pixel_gain_mode_statistics1(gmaps):
    """returns statistics of pixels in defferent gain modes in gain maps
    """
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps
    arr1 = np.ones_like(gr0, dtype=np.int32)
    return\
      np.sum(np.select((gr0,), (arr1,), default=0)),\
      np.sum(np.select((gr1,), (arr1,), default=0)),\
      np.sum(np.select((gr2,), (arr1,), default=0)),\
      np.sum(np.select((gr3,), (arr1,), default=0)),\
      np.sum(np.select((gr4,), (arr1,), default=0)),\
      np.sum(np.select((gr5,), (arr1,), default=0)),\
      np.sum(np.select((gr6,), (arr1,), default=0))

def pixel_gain_mode_statistics(gr0, gr1, gr2, gr3, gr4, gr5, gr6):
    """DEPRECATED"""
    return pixel_gain_mode_statistics1((gr0, gr1, gr2, gr3, gr4, gr5, gr6))

#--------------------

#def pixel_gain_mode_fractions(gr0, gr1, gr2, gr3, gr4, gr5, gr6):
def pixel_gain_mode_fractions(det, data):
    """returns fraction of pixels in defferent gain modes in gain maps
    """
    gmaps = gain_maps_epix10ka_any(det, data)
    if gmaps is None: return None
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps
    pix_stat = pixel_gain_mode_statistics1(gmaps)
    f = 1.0/gr0.size
    return [npix*f for npix in pix_stat]

#--------------------

def info_pixel_gain_mode_fractions(det, raw, msg='pixel gain mode fractions : '):
    """returns (str) with fraction of pixels in defferent gain modes in gain maps
    """
    grp_prob = pixel_gain_mode_fractions(det, raw)
    return '%s%s' % (msg, ', '.join(['%.5f'%p for p in grp_prob]))

#--------------------

def info_pixel_gain_mode_statistics1(gmaps):
    """returns (str) with statistics of pixels in defferent gain modes in gain maps
    """
    grp_stat = pixel_gain_mode_statistics1(gmaps)
    return ', '.join(['%7d' % npix for npix in grp_stat])

def info_pixel_gain_mode_statistics(gr0, gr1, gr2, gr3, gr4, gr5, gr6):
    """DEPRECATED"""
    return info_pixel_gain_mode_statistics1((gr0, gr1, gr2, gr3, gr4, gr5, gr6))

#--------------------

def info_pixel_gain_mode_statistics_for_raw(det, raw, msg='pixel gain mode statistics: '):
    """returns (str) with statistics of pixels in defferent gain modes in raw data
    """
    gmaps = gain_maps_epix10ka_any(det, raw)
    if gmaps is None: return None
    #gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps
    return '%s%s' % (msg, info_pixel_gain_mode_statistics1(gmaps))

#--------------------

def map_pixel_gain_mode1(gmaps):
    """returns map of pixel gain modes shaped as (16/4, 352, 384)
       enumerated from 0 to 6 for 'FH','FM','FL','AHL-H','AML-M','AHL-L','AML-L'
    """
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps
    arr1 = np.ones_like(gr0, dtype=np.int16)
    return np.select(gmaps,\
                     (arr1*0, arr1, arr1*2, arr1*3, arr1*4, arr1*5, arr1*6), default=-1)

def map_pixel_gain_mode(gr0, gr1, gr2, gr3, gr4, gr5, gr6):
    return map_pixel_gain_mode1((gr0, gr1, gr2, gr3, gr4, gr5, gr6))

#--------------------

def map_pixel_gain_mode_for_raw(det, raw):
    gmaps = gain_maps_epix10ka_any(det, raw)
    if gmaps is None: return None
    return map_pixel_gain_mode1(gmaps)

#--------------------

def calib_epix10ka_any(det, evt, cmpars=None, **kwa): # cmpars=(7,2,10,10), mbits=1, mask=None, nda_raw=None and 
    """
    Returns calibrated epix10ka data

    - gets constants
    - gets raw data
    - evaluates (code - pedestal - offset)
    - applys common mode correction if turned on
    - apply gain factor

    Parameters

    - det (psana.Detector) - Detector object
    - evt (psana.Event)    - Event object
    - cmpars (tuple) - common mode parameters
          = None - use pars from calib directory
          = cmpars=(<alg>, <mode>, <maxcorr>)
            alg is not used
            mode =0-correction is not applied, =1-in rows, =2-in cols-WORKS THE BEST
            i.e: cmpars=(7,0,100) or (7,2,100)
    - **kwa - used here and passed to det.mask_comb
      - nda_raw - substitute for det.raw(evt)
      - mbits - parameter of the det.mask_comb(...)
      - mask - user defined mask passed as optional parameter
    """

    logger.debug('In calib_epix10ka_any')

    t0_sec_tot = time()

    nda_raw = kwa.get('nda_raw', None)
    raw = det.raw(evt) if nda_raw is None else nda_raw # shape:(352, 384) or suppose to be later (<nsegs>, 352, 384) dtype:uint16
    if raw is None: return None

    cmp  = det.common_mode(evt) if cmpars is None else cmpars
    gain = det.gain(evt)      # - 4d gains  (7, <nsegs>, 352, 384)
    peds = det.pedestals(evt) # - 4d pedestals
    if gain is None: return None # gain = np.ones_like(peds)  # - 4d gains
    if peds is None: return None # peds = np.zeros_like(peds) # - 4d gains

    store = dic_store.get(det.name, None)

    if store is None:
        logger.debug('create store for detector %s' % det.name)
        store = dic_store[det.name] = Storage()

        # do ONCE this initialization 
        logger.debug(info_ndarr(raw,  '\n  raw ')\
                    +info_ndarr(gain, '\n  gain')\
                    +info_ndarr(peds, '\n  peds'))

        store.gfac = divide_protected(np.ones_like(gain), gain)
        store.arr1 = np.ones_like(raw, dtype=np.int8)

        logger.debug(info_ndarr(store.gfac,  '\n  gfac '))

        # 'FH','FM','FL','AHL-H','AML-M','AHL-L','AML-L'
        #store.gf4 = np.ones_like(raw, dtype=np.int32) * 0.25 # 0.3333 # M - perefierial
        #store.gf6 = np.ones_like(raw, dtype=np.int32) * 1    # L - center

    gfac = store.gfac

    gmaps = gain_maps_epix10ka_any(det, raw)
    if gmaps is None: return None
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps

    factor = np.select(gmaps,\
                       (gfac[0,:], gfac[1,:], gfac[2,:], gfac[3,:],\
                        gfac[4,:], gfac[5,:], gfac[6,:]), default=1) # 2msec

    #==================== TEST RETURN MAP OF PIXEL GAIN MODES
    #return map_pixel_gain_mode1(gmaps)
    #====================

    pedest = np.select(gmaps,\
                       (peds[0,:], peds[1,:], peds[2,:], peds[3,:],\
                        peds[4,:], peds[5,:], peds[6,:]), default=0)

    store.counter += 1
    if not store.counter%100:
        logger.debug(info_gain_mode_arrays1(gmaps)\
               +'\n'+info_pixel_gain_mode_statistics1(gmaps))

    logger.debug('TOTAL consumed time (sec) = %.6f' % (time()-t0_sec_tot)\
                +info_ndarr(factor, '\n  calib_epix10ka factor')\
                +info_ndarr(pedest, '\n  calib_epix10ka pedest'))

    arrf = np.array(raw & M14, dtype=np.float32) - pedest

    if store.mask is None: 
        mbits = kwa.pop('mbits',1) # 1-mask from status, etc.
        mask = det.mask_comb(evt, mbits, **kwa) if mbits > 0 else None
        mask_opt = kwa.get('mask',None) # mask optional parameter in det.calib(...,mask=...)
        if mask_opt is not None:
           store.mask = mask_opt if mask is None else merge_masks(mask,mask_opt)
    mask = store.mask        

    logger.debug('common-mode correction pars cmp: %s' % str(cmp))

    if cmp is not None:
      mode, cormax = int(cmp[1]), cmp[2]
      npixmin = cmp[3] if len(cmp)>3 else 10
      if mode>0:
        t0_sec_cm = time()
        #t2_sec_cm = time()
        arr1 = store.arr1 # np.ones_like(mask, dtype=np.uint8)
        grhm = np.select((gr0,  gr1,  gr3,  gr4), (arr1, arr1, arr1, arr1), default=0)
        gmask = np.bitwise_and(grhm, mask) if mask is not None else grhm
        if gmask.ndim == 2: gmask.shape = (1,gmask.shape[-2],gmask.shape[-1])

        #logger.debug(info_ndarr(arr1, '\n  arr1'))
        #logger.debug(info_ndarr(grhm, 'XXXX grhm'))
        logger.debug(info_ndarr(gmask, 'gmask')\
                     + '\n  per panel statistics of cm-corrected pixels: %s'%
                     str(np.sum(gmask, axis=(1,2), dtype=np.uint32) if gmask is not None else None))
        #logger.debug('common-mode mask massaging (sec) = %.6f' % (time()-t2_sec_cm)) # 5msec

        #sh = (nsegs, 352, 384)
        hrows = 176 # int(352/2)
        for s in range(arrf.shape[0]):

          if mode & 4: # in banks: (352/2,384/8)=(176,48) pixels
            common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=8, cormax=cormax, npix_min=npixmin)
            common_mode_2d_hsplit_nbanks(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], nbanks=8, cormax=cormax, npix_min=npixmin)

          if mode & 1: # in rows per bank: 384/8 = 48 pixels # 190ms
            common_mode_rows_hsplit_nbanks(arrf[s,], mask=gmask[s,], nbanks=8, cormax=cormax, npix_min=npixmin)

          if mode & 2: # in cols per bank: 352/2 = 176 pixels # 150ms
            common_mode_cols(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], cormax=cormax, npix_min=npixmin)
            common_mode_cols(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], cormax=cormax, npix_min=npixmin)

        logger.debug('TIME common-mode correction = %.6f sec for cmp=%s' % (time()-t0_sec_cm, str(cmp)))

    return arrf * factor if mask is None else arrf * factor * mask # gain correction

#--------------------

calib_epix10ka = calib_epix10ka_any

#--------------------

def find_gain_mode(det, data=None):
    """Returns str gain mode from the list GAIN_MODES or None.
       if data=None: distinguish 5-modes w/o data
    """
    #gmaps = gain_maps_epix10ka_any(det, data)
    #if gmaps is None: return None
    #gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps

    #arr1 = np.ones_like(gr0)
    #npix = arr1.size
    #pix_stat = (np.select((gr0,), (arr1,), 0).sum(),\
    #            np.select((gr1,), (arr1,), 0).sum(),\
    #            np.select((gr2,), (arr1,), 0).sum(),\
    #            np.select((gr3,), (arr1,), 0).sum(),\
    #            np.select((gr4,), (arr1,), 0).sum(),\
    #            np.select((gr5,), (arr1,), 0).sum(),\
    #            np.select((gr6,), (arr1,), 0).sum())

    ##logger.debug('Statistics in gain groups: %s' % str(pix_stat))

    #f = 1.0/arr1.size
    #grp_prob = [npix*f for npix in pix_stat]
    #logger.debug('grp_prob: %s' % ', '.join(['%.4f'%p for p in grp_prob]))

    #grp_prob = pixel_gain_mode_fractions(gr0, gr1, gr2, gr3, gr4, gr5, gr6)
    grp_prob = pixel_gain_mode_fractions(det, data)

    ind = next((i for i,p in enumerate(grp_prob) if p>0.5), None)
    if ind is None: return None
    gain_mode = GAIN_MODES[ind] if ind<len(grp_prob) else None 
    #logger.debug('Gain mode %s is selected from %s' % (gain_mode, ', '.join(GAIN_MODES)))

    return gain_mode

#--------------------
#--------------------
#--------------------

if __name__ == "__main__":

  import sys
  import psana
  #from pyimgalgos.GlobalUtils import print_ndarr

  EVENTS  = 5

#--------------------

  # See Detector.examples.ex_source_dsname
  def ex_source_dsname(tname): 
    src, dsn = 'MfxEndstation.0:Epix10ka.0', 'exp=mfxx32516:run=346' # 'Epix10ka_0', run=377
    if   tname == '1': pass
    elif tname == '2': src, dsn = 'NoDetector.0:Epix10ka.3',\
                                  'exp=mfxx32516:run=1021:dir=/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/combined'
    elif tname == '10': src, dsn = 'MfxEndstation.0:Epix10ka.1', 'exp=mfxx32516:run=377' 
    else: sys.exit('Non-implemented sample for test number # %s' % tname)
    return src, dsn

#--------------------

  def test_config_data(tname):
    
    ssrc, dsname = ex_source_dsname(tname)
    print('Test: %s\n  dataset: %s\n  source: %s' % (tname, dsname, ssrc))

    ds = psana.DataSource(dsname)
    det = psana.Detector(ssrc)
    env = ds.env()
    evt = ds.events().next()
    src = psana.Source(ssrc)

    #confo = env.configStore().get(psana.Epix.Config10kaV1, src)
    #datao = evt.get(psana.Epix.ElementV3, src)
    confo = get_epix10ka_config_object(env, src)
    datao = get_epix10ka_data_object(evt, src)

    epix_name = 'epix-%s' % id_epix(confo)
    print('epix_name: %s' % epix_name)

#--------------------

  def test_calib(tname):
    
    ssrc, dsname = ex_source_dsname(tname)
    print('Test: %s\n  dataset: %s\n  source: %s' % (tname, dsname, ssrc))

    ds  = psana.DataSource(dsname)
    d   = psana.Detector(ssrc)
    env = ds.env()
    src = psana.Source(ssrc)

    for nev,evt in enumerate(ds.events()):
    
        if nev > EVENTS: break
        print('%s\nEvent %4d' % (50*'_', nev))
        if evt is None: continue

        raw = d.raw(evt)
        t0_sec = time()
        gain = d.gain(evt)
        peds = d.pedestals(evt)
        dt = time()-t0_sec
        print('\nXXX: det.gain & peds constants consumed time = %.6f sec' % dt)

        print_ndarr(raw,  name='raw ')
        print_ndarr(gain, name='gain')
        print_ndarr(peds, name='peds')

        nda = calib_epix10ka_any(d, evt, cmpars=None)
        print_ndarr(nda, name='calib')

        #print_ndarr(d.common_mode(evt), name='common_mode')
        #d.image(evt)

        #nda = d.calib(evt, cmppars=(8,5,500))

#--------------------

if __name__ == "__main__":
    print(80*'_')
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if tname == '1': test_config_data(tname)
    if tname == '2': test_calib(tname)
    else: sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#--------------------
