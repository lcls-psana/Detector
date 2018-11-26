#------------------------------
"""
:py:class:`UtilsEpix10ka` contains utilities for epix10ka and its composite detectors
=====================================================================================

Usage::
    from Detector.UtilsEpix10ka import ...


This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-11-14 by Mikhail Dubrovin
"""

#--------------------
import os
import numpy as np
from time import time

import logging
logger = logging.getLogger(__name__)

from Detector.PyDataAccess import get_epix_data_object, get_epix10ka_config_object,\
                                  get_epix10kaquad_config_object, get_epix10ka2m_config_object,\
                                  get_epix10ka_any_config_object
from Detector.GlobalUtils import print_ndarr, info_ndarr, divide_protected
#from PSCalib.GlobalUtils import load_textfile, save_textfile

# o = get_epix_data_object(evt, src)
# co = get_epix_config_object(env, src)
get_epix10ka_data_object = get_epix_data_object

# CALIB_REPO_EPIX10KA = '/reg/g/psdm/detector/gains/epix10k/panels'

#--------------------

B14 = 040000 # 16384 or 1<<14 (15-th bit starting from 1)
B04 =    020 #    16 or 1<<4   (5-th bit starting from 1)
B05 =    040 #    32 or 1<<5   (6-th bit starting from 1)
M14 = 0x3fff # 16383 or (1<<14)-1 - 14-bit mask

#--------------------

class Storage :
    def __init__(self) :
        self.arr1 = None
        self.gfac = None

#--------------------
store = Storage() # singleton
#--------------------

def config_objects(env, src, idx=0) :
    """ Returns configuration objects for detector, quad, element; 
        dco,qco,eco (or None depending on detector) of types
        psana.Epix.Config10ka2MV1
        psana.Epix.Config10kaQuad
        psana.Epix.Config10ka or psana.Epix.Config10kaV1
    """
    dco = get_epix10ka2m_config_object(env, src)
    if dco is not None : return dco, dco.quad(idx/4), dco.elemCfg(idx)

    qco = get_epix10kaquad_config_object(env, src)
    if qco is not None : return None, qco, qco.elemCfg(idx)

    eco = get_epix10ka_config_object(env, src)
    if eco is not None : return None, None, eco

    logger.warning('None of epics10ka/quad/2m configuration objects found for env:%s src:%s idx:%s'%\
                    (str(env), str(src), str(idx)))
    return None, None, None

#--------------------

def cbits_config_epix10ka(cob) :
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
    if all(trbits) : cbits = np.bitwise_or(cbits, B04) # for all pixels (352, 384)
    elif not any(trbits) : return cbits
    else : # set trbit per ASIC
        if trbits[2] : cbits[:176,:192] = np.bitwise_or(cbits[:176,:192], B04)
        if trbits[3] : cbits[176:,:192] = np.bitwise_or(cbits[176:,:192], B04)
        if trbits[0] : cbits[176:,192:] = np.bitwise_or(cbits[176:,192:], B04)
        if trbits[1] : cbits[:176,192:] = np.bitwise_or(cbits[:176,192:], B04)
    return cbits

#------------------------------

def cbits_config_epix10kaquad(qcob) :
    """Returns array of control bits shape=(4, 352, 384) from psana.Epix.Config10kaQuadV1
    """
    lst_cbits = [cbits_config_epix10ka(qcob.elemCfg(i)) for i in range(qcob.numberOfElements())]
    cbits = np.stack(tuple(lst_cbits))
    #logger.debug('In cbits_config_epix10kaquad cob: %s numberOfElements: %d\n  %s'%\
    #              (str(qcob), qcob.numberOfElements(), info_ndarr(cbits, 'cbits for epix10kaquad')))
    return cbits

#--------------------

def cbits_config_epix10ka2m(dcob) :
    """Returns array of control bits shape=(16, 352, 384) from psana.Epix.Config10ka2MV1 object
    """
    lst_cbits = [cbits_config_epix10ka(dcob.elemCfg(i)) for i in range(dcob.numberOfElements())]
    cbits = np.stack(tuple(lst_cbits))
    #logger.debug('In cbits_config_epix10ka2m cob: %s numberOfElements: %d\n %s'%\
    #              (str(dcob), dcob.numberOfElements(), info_ndarr(cbits, 'cbits for epix10ka2m')))
    return cbits
       
#--------------------

def cbits_config_epix10ka_any(env, src) :
    """Returns array of control bits shape=(16, 352, 384) from any config object
    """
    cob = get_epix10ka2m_config_object(env, src)
    if cob is not None : return cbits_config_epix10ka2m(cob)

    cob = get_epix10kaquad_config_object(env, src)
    if cob is not None : return cbits_config_epix10kaquad(cob)

    cob = get_epix10ka_config_object(env, src)
    if cob is not None : return cbits_config_epix10ka(cob)

    return None

#--------------------

def cbits_total_epix10ka_any(det, data=None) :
    """Returns array of control bits shape=(16, 352, 384) 
       from any config object and data array.
    """
    cbits = cbits_config_epix10ka_any(det.env, det.source)
    #logger.debug(info_ndarr(cbits, 'cbits', first, last))
    
    if cbits is None : return None

    #--------------------------------
    # get 5-bit pixel config array with bit assignments
    #   0001 = 1<<0 = 1 - T test bit
    #   0010 = 1<<1 = 2 - M mask bit
    #   0100 = 1<<2 = 4 - g  gain bit
    #   1000 = 1<<3 = 8 - ga gain bit
    # 010000 = 1<<4 = 16 - trbit
    # add data bit
    # 100000 = 1<<5 = 32 - data bit 14
    #--------------------------------
    if data is not None :
        #logger.debug(info_ndarr(data, 'data', first, last))
        # get array of data bit 14 and add it as a bit 5 to cbits
        databit14 = np.bitwise_and(data, B14)
        databit05 = np.right_shift(databit14,9) # 040000 -> 040
        cbits = np.bitwise_or(cbits, databit05) # 109us
        #cbits[databit14>0] += 040              # 138us

    return cbits

#--------------------

def gain_maps_epix10ka_any(det, data=None) :
    """Returns maps of gain groups shape=(16, 352, 384) 
    """
    cbits = cbits_total_epix10ka_any(det, data)
    if cbits is None : return None

    #--------------------------------
    # cbits - pixel control bit array
    #--------------------------------
    #   data bit 14
    #  / trbit
    # V / bit3
    #  V / bit2
    #   V / M
    #    V / T             gain range index
    #     V /             /  in calib files
    #      V             V 
    # x111xx =28 -  FH_H 0 
    # x011xx =12 -  FM_M 1 
    # xx10xx = 8 -  FL_L 2  
    # 1100xx =48 - AHL_H 3 
    # 1000xx =32 - AML_M 4 
    # 0100xx =16 - AHL_L 5 
    # 0000xx = 0 - AML_L 6 
    #--------------------------------
    # 111100 =60 - cbitsM60 - mask 
    # 011100 =28 - cbitsM28 - mask 
    # 001100 =12 - cbitsM12 - mask 
    #--------------------------------

    cbitsM28 = cbits & 28 # control bits masked by configuration 3-bit-mask
    cbitsM12 = cbits & 12 # control bits masked by configuration 2-bit-mask
    #logger.debug(info_ndarr(cbitsMCB, 'cbitsMCB', first, last))

    gr0 = (cbitsM28 == 28)
    gr1 = (cbitsM28 == 12)
    gr2 = (cbitsM12 ==  8)
    gr3 = (cbitsM28 == 16)
    gr4 = (cbitsM28 ==  0)
    gr5 = (cbits    == 16)
    gr6 = (cbits    ==  0)

    #first = 10000
    #last  = first+5
    #logger.debug(info_ndarr(gr0, 'gr0', first, last))
    #logger.debug(info_ndarr(gr1, 'gr1', first, last))
    #logger.debug(info_ndarr(gr2, 'gr2', first, last))
    #logger.debug(info_ndarr(gr3, 'gr3', first, last))
    #logger.debug(info_ndarr(gr4, 'gr4', first, last))
    #logger.debug(info_ndarr(gr5, 'gr5', first, last))
    #logger.debug(info_ndarr(gr6, 'gr6', first, last))

    return gr0, gr1, gr2, gr3, gr4, gr5, gr6

#--------------------

def calib_epix10ka_any(det, evt, cmpars=None) : # cmpars=(7,3,100)) :
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
    """

    logger.debug('In calib_epix10ka_any')

    t0_sec_tot = time()

    arr = det.raw(evt) # shape:(352, 384) or suppose to be later (<nsegs>, 352, 384) dtype:uint16
    if arr is None : return None

    gain = det.gain(evt)      # - 4d gains  (7, <nsegs>, 352, 384)
    peds = det.pedestals(evt) # - 4d pedestals
    if gain is None : return None # gain = np.ones_like(peds)  # - 4d gains
    if peds is None : return None # peds = np.zeros_like(peds) # - 4d gains

    #gfac = gain 
    gfac = store.gfac
    arr1 = store.arr1 
    if store.gfac is None :
        logger.debug(info_ndarr(arr,  '\n  raw ')\
                    +info_ndarr(gain, '\n  gain')\
                    +info_ndarr(peds, '\n  peds'))

        store.gfac = gfac = divide_protected(np.ones_like(gfac), gain)
        store.arr1 = arr1 = np.ones_like(arr)

    gmaps = gain_maps_epix10ka_any(det, arr)
    if gmaps is None : return None
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps

    #t0_sec = time()
    #logger.debug('gain range statistics:\n  gr0 %d\n  gr1 %d\n  gr2 %d\n  gr3 %d\n  gr4 %d\n  gr5 %d\n  gr6 %d'%\
    # (np.sum(np.select((gr0,), (arr1,), default=0)),\
    #  np.sum(np.select((gr1,), (arr1,), default=0)),\
    #  np.sum(np.select((gr2,), (arr1,), default=0)),\
    #  np.sum(np.select((gr3,), (arr1,), default=0)),\
    #  np.sum(np.select((gr4,), (arr1,), default=0)),\
    #  np.sum(np.select((gr5,), (arr1,), default=0)),\
    #  np.sum(np.select((gr6,), (arr1,), default=0)))) # 3ms !!!
    #dt = time()-t0_sec; print('debug statistics consumed time (sec) = %.6f' % dt)

    factor = np.select((gr0, gr1, gr2, gr3, gr4, gr5, gr6),\
                       (gfac[0,:], gfac[1,:], gfac[2,:], gfac[3,:],\
                        gfac[4,:], gfac[5,:], gfac[6,:]), default=1) # 2msec

    pedest = np.select((gr0, gr1, gr2, gr3, gr4, gr5, gr6),\
                       (peds[0,:], peds[1,:], peds[2,:], peds[3,:],\
                        peds[4,:], peds[5,:], peds[6,:]), default=0)

    logger.debug('TOTAL consumed time (sec) = %.6f' % (time()-t0_sec_tot))
    logger.debug(info_ndarr(factor, 'calib_epix10ka factor'))
    logger.debug(info_ndarr(pedest, 'calib_epix10ka pedest'))

    arrf = np.array(arr & M14, dtype=np.float32) - pedest
    return arrf * factor

    #====================
    #sys.exit('TEST EXIT')
    #====================

#--------------------

calib_epix10ka = calib_epix10ka_any

#--------------------
#--------------------
#--------------------

if __name__ == "__main__" :

  import sys
  import psana
  #from pyimgalgos.GlobalUtils import print_ndarr

  EVENTS  = 5

#--------------------

  # See Detector.examples.ex_source_dsname
  def ex_source_dsname(tname) : 
    src, dsn = 'MfxEndstation.0:Epix10ka.0', 'exp=mfxx32516:run=346' # 'Epix10ka_0', run=377
    if   tname == '1': pass
    elif tname == '2': src, dsn = 'NoDetector.0:Epix10ka.3',\
                                  'exp=mfxx32516:run=1021:dir=/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/combined'
    elif tname == '10': src, dsn = 'MfxEndstation.0:Epix10ka.1', 'exp=mfxx32516:run=377' 
    else : sys.exit('Non-implemented sample for test number # %s' % tname)
    return src, dsn

#--------------------

  def test_config_data(tname) :
    
    ssrc, dsname = ex_source_dsname(tname)
    print 'Test: %s\n  dataset: %s\n  source : %s' % (tname, dsname, ssrc)

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

  def test_calib(tname) :
    
    ssrc, dsname = ex_source_dsname(tname)
    print 'Test: %s\n  dataset: %s\n  source : %s' % (tname, dsname, ssrc)

    ds  = psana.DataSource(dsname)
    d   = psana.Detector(ssrc)
    env = ds.env()
    src = psana.Source(ssrc)

    for nev,evt in enumerate(ds.events()):
    
        if nev > EVENTS : break
        print '%s\nEvent %4d' % (50*'_', nev)
        if evt is None : continue

        raw = d.raw(evt)
        t0_sec = time()
        gain = d.gain(evt)
        peds = d.pedestals(evt)
        dt = time()-t0_sec
        print '\nXXX: det.gain & peds constants consumed time (sec) =', dt

        print_ndarr(raw,  name='raw ')
        print_ndarr(gain, name='gain')
        print_ndarr(peds, name='peds')

        nda = calib_epix10ka_any(d, evt, cmpars=None)
        print_ndarr(nda, name='calib')

        #print_ndarr(d.common_mode(evt), name='common_mode')
        #d.image(evt)

        #nda = d.calib(evt, cmppars=(8,5,500))

#--------------------

if __name__ == "__main__" :
    print 80*'_'
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if tname == '1' : test_config_data(tname)
    if tname == '2' : test_calib(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#--------------------
