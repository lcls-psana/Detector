#------------------------------
"""
:py:class:`UtilsEpix` contains utilities for epix100a and epix10ka detectors
============================================================================

    Epix gain range coding ????

    bit: 15,14,...,0   Gain range, ind
          0, 0         Normal,       0
          0, 1         ForcedGain1,  1
          1, 1         FixedGain2,   2

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2018-02-22 by Mikhail Dubrovin
"""

#------------------------------
import os
import sys
import numpy as np
from time import time

import logging
logger = logging.getLogger(__name__)

from Detector.PyDataAccess import get_epix_data_object, get_epix10ka_config_object
from Detector.GlobalUtils import print_ndarr, info_ndarr, divide_protected
from PSCalib.GlobalUtils import load_textfile, save_textfile

# o = get_epix_data_object(evt, src)
# co = get_epix_config_object(env, src)
get_epix10ka_data_object = get_epix_data_object

CALIB_REPO_EPIX10KA = '/reg/g/psdm/detector/gains/epix10k/panels'

#------------------------------

B14 = 040000 # 16384 or 1<<14 (15-th bit starting from 1)
B04 =    020 #    16 or 1<<4   (5-th bit starting from 1)
B05 =    040 #    32 or 1<<5   (6-th bit starting from 1)
M14 = 0x3fff # 16383 or (1<<14)-1 - 14-bit mask

#------------------------------

class Storage :
    def __init__(self) :
        self.arr1 = None
        self.gfac = None

#------------------------------
store = Storage() # singleton
#------------------------------

def create_directory(dir, mode=0777) :
    """Creates directory and sets its mode"""
    if os.path.exists(dir) :
        logger.debug('Exists: %s' % dir)
    else :
        os.makedirs(dir)
        os.chmod(dir, mode)
        logger.debug('Created:%s, mode(oct)=%s' % (dir, oct(mode)))

#------------------------------

def alias_for_id(panel_id, fname='%s/.aliases.txt'%CALIB_REPO_EPIX10KA) :
    """Returns Epix100a/10ka panel short alias for long panel_id, 
       e.g., for panel_id = 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
       returns 0001
    """
    alias_max = 0
    if os.path.exists(fname) :
      logger.debug('search alias for panel id: %s\n  in file %s' % (panel_id, fname))
      recs = load_textfile(fname).strip('\n').split('\n')
      for r in recs :
        fields = r.strip('\n').split(' ')
        if fields[1] == panel_id : 
            logger.debug('found alias %s' % (fields[0]))
            return fields[0]
        ialias = int(fields[0])
        if ialias>alias_max : alias_max = ialias
        #print(fields)
    # if record for panel_id is not found yet, add it to the file and return its alias
    rec = '%04d %s' % (alias_max+1, panel_id)
    logger.debug('file "%s" is appended with record:\n%s' % (fname, rec))
    save_textfile(rec, fname, mode='a')
    return '%04d' % (alias_max+1)

#------------------------------

def id_for_alias(alias, fname='%s/aliases.txt'%CALIB_REPO_EPIX10KA) :
    """Returns Epix100a/10ka panel panel_id for specified alias, 
       e.g., for alias = 0001
       returns 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719
    """
    logger.debug('search panel id for alias: %s\n  in file %s' % (alias, fname))
    recs = load_textfile(fname).strip('\n').split('\n')
    for r in recs :
        fields = r.strip('\n').split(' ')
        if fields[0] == alias : 
            logger.debug('found panel id %s' % (fields[1]))
            return fields[1]

#------------------------------

def id_epix(config_obj) :
    """Returns Epix100 Id as a string, e.g., 3925999616-0996663297-3791650826-1232098304-0953206283-2655595777-0520093719"""

    o = config_obj
    fmt2 = '%010d-%010d'
    zeros = fmt2 % (0,0)
    version = '%010d' % (o.version()) if getattr(o, "version", None) is not None else '%010d' % 0
    carrier = fmt2 % (o.carrierId0(), o.carrierId1())\
              if getattr(o, "carrierId0", None) is not None else zeros
    digital = fmt2 % (o.digitalCardId0(), o.digitalCardId1())\
              if getattr(o, "digitalCardId0", None) is not None else zeros
    analog  = fmt2 % (o.analogCardId0(), o.analogCardId1())\
              if getattr(o, "analogCardId0", None) is not None else zeros
    return '%s-%s-%s-%s' % (version, carrier, digital, analog)

#------------------------------

def is_trbit_high(co) :
    """from configuration object define if detector works in high gain mode.
    """
    if co.numberOfAsics()>1 : 
        return co.asics(0).trbit()==1

#------------------------------

def time_of_nda(t0_sec, res, cmt='XXX') :
    dt = time()-t0_sec
    print_ndarr(res, '%s : consumed time (sec) = %.6f' % (cmt,dt))
    return res

#------------------------------

def calib_epix10ka(det, evt, cmpars=None) : # cmpars=(7,3,100)) :
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
       store.gfac = gfac = divide_protected(np.ones_like(arr), gain)
       store.arr1 = arr1 = np.ones_like(arr)

    cob = get_epix10ka_config_object(det.env, det.source)

    # get 4-bit pixel config array with bit assignment]
    #   0001 = 1<<0 = 1 - T test bit
    #   0010 = 1<<1 = 2 - M mask bit
    #   0100 = 1<<2 = 4 - g  gain bit
    #   1000 = 1<<3 = 8 - ga gain bit

    pca = cob.asicPixelConfigArray()

    # begin to create array of control bits 
    # array of control bits 2 and 3 M mask bits 0, 1 
    #                                 do not override them just in case if they can be useful later.
    cbits = np.bitwise_and(pca,12) # 014 (bin:1100)

    # add bits
    # 010000 = 1<<4 = 16 - trbit
    # 100000 = 1<<5 = 32 - data bit 14

    trbit = cob.asics(0).trbit()
    logger.debug('trbit: %d' % trbit)
    if trbit : cbits = np.bitwise_or(cbits, B04)

    # get array of data bit 14 and add it as a bit 5 to cbits
    arrbit14 = np.bitwise_and(arr, B14)
    arrbit05 = np.right_shift(arrbit14,9)  # 040000 -> 040  
    cbits = np.bitwise_or(cbits, arrbit05) # 109us
    #cbits[arrbit14>0] += 040              # 138us

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

    cbitsMCB = cbits & 28 # control bits masked by configuration 3-bit-mask
    #logger.debug(info_ndarr(cbitsMCB, 'cbitsMCB', first, last))

    gr0 = (cbitsMCB == 28)
    gr1 = (cbitsMCB == 12)
    gr2 = (cbitsMCB ==  8)
    gr3 = (cbitsMCB == 16)
    gr4 = (cbitsMCB ==  0)
    gr5 = (cbits    == 16)
    gr6 = (cbits    ==  0)

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

    #print_ndarr(cmp,  'XXX: common mode parameters ')
    #print_ndarr(arr,  'XXX: calib_jungfrau arr ')
    #print_ndarr(peds, 'XXX: calib_jungfrau peds')
    #print_ndarr(gain, 'XXX: calib_jungfrau gain')
    #print_ndarr(peds, 'XXX: calib_jungfrau peds')
    #====================
    #sys.exit('TEST EXIT')
    #====================

#------------------------------
#------------------------------
#------------------------------
#------------------------------
#------------------------------

if __name__ == "__main__" :

  import psana
  from pyimgalgos.GlobalUtils import print_ndarr

  EVENTS  = 5

#------------------------------

  # See Detector.examples.ex_source_dsname
  def ex_source_dsname(tname) : 
    src, dsn = 'MfxEndstation.0:Epix10ka.0', 'exp=mfxx32516:run=346' # 'Epix10ka_0', run=377
    if   tname == '1': pass
    elif tname == '2': src, dsn = 'NoDetector.0:Epix10ka.3',\
                                  'exp=mfxx32516:run=1021:dir=/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/combined'
    elif tname == '10': src, dsn = 'MfxEndstation.0:Epix10ka.1', 'exp=mfxx32516:run=377' 
    else : sys.exit('Non-implemented sample for test number # %s' % tname)
    return src, dsn

#------------------------------

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

#------------------------------

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

        nda = calib_epix10ka(d, evt, cmpars=None)
        print_ndarr(nda, name='calib')

        #print_ndarr(d.common_mode(evt), name='common_mode')
        #d.image(evt)

        #nda = d.calib(evt, cmppars=(8,5,500))

#------------------------------

if __name__ == "__main__" :
    print 80*'_'
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if tname == '1' : test_config_data(tname)
    if tname == '2' : test_calib(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#------------------------------
