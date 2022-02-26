
"""
:py:class:`UtilsJungfrau` contains utilities for Jungfrau detector correction
=============================================================================

Usage ::
    # Test: python Detector/src/UtilsJungfrau.py

    # Import:
    from Detector.UtilsJungfrau import id_jungfrau
    from Detector.UtilsJungfrau import id_jungfrau, number_of_modules_in_jungfrau, psana_source,\
                                       number_of_modules_in_jungfrau, string_from_source

    idjf = id_jungfrau_from_config(co)   # 1508613-000022630721062933-3997872-1508613-22630721062933-3997943
    ids0 = id_jungfrau_from_config(co,0) # 1508613-000022630721062933-3997872
    ids0 = id_jungfrau_from_config(co,1) # 1508613-000022630721062933-3997943

Jungfrau gain range coding
bit: 15,14,...,0   Gain range, ind
      0, 0         Normal,       0
      0, 1         ForcedGain1,  1
      1, 1         FixedGain2,   2

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2017-10-03 by Mikhail Dubrovin
"""
from __future__ import print_function
#from __future__ import division


import logging
logger = logging.getLogger(__name__)

import os

import numpy as np
from time import time
from Detector.GlobalUtils import print_ndarr, info_ndarr, divide_protected
from Detector.UtilsCommonMode import common_mode_cols,\
                                     common_mode_rows_hsplit_nbanks, common_mode_2d_hsplit_nbanks
from Detector.PyDataAccess import get_jungfrau_data_object, get_jungfrau_config_object

from PSCalib.GlobalUtils import string_from_source, complete_detname

DIRNAME = '/reg/g/psdm/detector/gains/jungfrau'

BW1 =  0o40000 # 16384 or 1<<14 (15-th bit starting from 1)
BW2 = 0o100000 # 32768 or 2<<14 or 1<<15
BW3 = 0o140000 # 49152 or 3<<14
MSK =  0x3fff # 16383 or (1<<14)-1 - 14-bit mask


class Storage(object):
    def __init__(self):
        #self.offs = None
        self.arr1 = None
        self.mask = None
        self.gfac = {} # {detname:nda}


store = Storage() # singleton


def map_gain_range_index(det, evt, **kwa):
    """Returns per event array of jungfrau pixel gain range indices [0:2] shaped as raw (<nsegs>, 512, 1024) dtype:uint16
    """
    nda_raw = kwa.get('nda_raw', None)
    raw = det.raw(evt) if nda_raw is None else nda_raw
    if raw is None: return None
    gbits = raw>>14 # 00/01/11 - gain bits for mode 0,1,2
    #fg0, fg1, fg2 = gbits==0, gbits==1, gbits==3
    return np.select((gbits<2, gbits>2), (gbits, 2*np.ones(raw.shape, dtype=np.uint16)), 0)


def gain_range_maps_jungfrau(det, evt, nda_raw=None):
    """Returns 3 of four possible arrays (<nsegs>, 512, 1024) dtype bool
       for gain bits 00/01/11/10 of modes 0,1,2,x
    """
    raw = det.raw(evt) if nda_raw is None else nda_raw
    if raw is None: return None
    gbits = raw>>14 # 00/01/11/10 - gain bits for mode 0,1,2,x
    return gbits==0, gbits==1, gbits==3 #, gbits==2


def event_constants(cons, grmaps, default=0):
    """Returns calibration constants shaped as det.raw
       Parameters
       ----------
       cons shape=(3, <nsegs>, 512, 1024)
       grmaps - list of boolean gain maps (gr0, gr1, gr2) = gain_range_maps_jungfrau(det, evt, **kwa)
    """
    return np.select(grmaps, (cons[0,:], cons[1,:], cons[2,:]), default=default)


def calib_jungfrau(det, evt, cmpars=(7,3,200,10), **kwa):
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
    - cmpars (tuple) - common mode parameters
        - cmpars[0] - algorithm # 7-for jungfrau
        - cmpars[1] - control bit-word 1-in rows, 2-in columns
        - cmpars[2] - maximal applied correction
    - **kwa - used here and passed to det.mask_v2 or det.mask_comb
      - nda_raw - if not None, substitutes evt.raw()
      - mbits - DEPRECATED parameter of the det.mask_comb(...)
      - mask - user defined mask passed as optional parameter
    """

    #print('XXX: ====================== det.name', det.name)

    src = det.source # - src (psana.Source)   - Source object

    nda_raw = kwa.get('nda_raw', None)
    arr = det.raw(evt) if nda_raw is None else nda_raw # shape:(<npanels>, 512, 1024) dtype:uint16
    if arr is None: return None

    #arr  = np.array(det.raw(evt), dtype=np.float32)
    peds = det.pedestals(evt) # - 4d pedestals shape:(3, 1, 512, 1024) dtype:float32
    if peds is None: return None

    gain = det.gain(evt)      # - 4d gains
    offs = det.offset(evt)    # - 4d offset
    detname = string_from_source(det.source)

    cmp  = det.common_mode(evt) if cmpars is None else cmpars
    if gain is None: gain = np.ones_like(peds)  # - 4d gains
    if offs is None: offs = np.zeros_like(peds) # - 4d gains

    # cache
    gfac = store.gfac.get(detname, None) # det.name
    if gfac is None:
       gfac = divide_protected(np.ones_like(peds), gain)
       store.gfac[detname] = gfac
       store.arr1 = np.ones_like(arr, dtype=np.int8)

    #print_ndarr(cmp,  'XXX: common mode parameters ')
    #print_ndarr(arr,  'XXX: calib_jungfrau arr ')
    #print_ndarr(peds, 'XXX: calib_jungfrau peds')
    #print_ndarr(gain, 'XXX: calib_jungfrau gain')
    #print_ndarr(offs, 'XXX: calib_jungfrau offs')
    #print_ndarr(gfac, 'XXX: calib_jungfrau gfac')

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

    #gbits = raw>>14 # 00/01/11 - gain bits for mode 0,1,2
    #gr0, gr1, gr2 = gbits==0, gbits==1, gbits==3

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

    arrf -= offset # Apply offset correction

    if store.mask is None:
       store.mask = det.mask_total(evt, **kwa)
    mask = store.mask

    if cmp is not None:
      mode, cormax = int(cmp[1]), cmp[2]
      npixmin = cmp[3] if len(cmp)>3 else 10
      if mode>0:
        #arr1 = store.arr1
        #grhg = np.select((gr0,  gr1), (arr1, arr1), default=0)
        logger.debug(info_ndarr(gr0, 'gain group0'))
        logger.debug(info_ndarr(mask, 'mask'))
        t0_sec_cm = time()
        gmask = np.bitwise_and(gr0, mask) if mask is not None else gr0
        #sh = (nsegs, 512, 1024)
        hrows = 256 #512/2
        for s in range(arrf.shape[0]):
          if mode & 4: # in banks: (512/2,1024/16) = (256,64) pixels # 100 ms
            common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=16, cormax=cormax, npix_min=npixmin)
            common_mode_2d_hsplit_nbanks(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], nbanks=16, cormax=cormax, npix_min=npixmin)

          if mode & 1: # in rows per bank: 1024/16 = 64 pixels # 275 ms
            common_mode_rows_hsplit_nbanks(arrf[s,], mask=gmask[s,], nbanks=16, cormax=cormax, npix_min=npixmin)

          if mode & 2: # in cols per bank: 512/2 = 256 pixels  # 290 ms
            common_mode_cols(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], cormax=cormax, npix_min=npixmin)
            common_mode_cols(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], cormax=cormax, npix_min=npixmin)

        logger.debug('TIME: common-mode correction time = %.6f sec' % (time()-t0_sec_cm))

    return arrf * factor if mask is None else arrf * factor * mask # gain correction


def id_jungfrau_module(mco, fmt='%s-%s-%s'): # '%020d-%020d-%020d'
    """Return (str) Id for jungfrau ModuleConfigV# object mco, e.g.:
       1508613-3997943-22630721062933
    """
    if mco is None: return None
    return fmt % (hex(mco.moduleVersion()).lstrip('0x'),\
                  hex(mco.firmwareVersion()).lstrip('0x'),\
                  hex(mco.serialNumber()).lstrip('0x'))\
           if mco is not None else None


def id_jungfrau_module_v0(mco, fmt='%d-%d-%d'): # '%020d-%020d-%020d'
    """Return (str) Id for jungfrau ModuleConfigV# object mco, e.g.:
       1508613-3997943-22630721062933
    """
    if mco is None: return None
    return fmt % (mco.moduleVersion(), mco.firmwareVersion(), mco.serialNumber())\
           if mco is not None else None


def jungfrau_config_object(env, src):
    """Returns Jungfrau config object"""
    source = psana_source(env, src)
    return get_jungfrau_config_object(env, source)


def number_of_modules_from_config(co):
    """Returns (int) number of modules from Jungfrau configuration object"""
    if co is None: return None
    return co.numberOfModules()


def number_of_modules_in_jungfrau(env, src):
    """Returns (int) number of modules for Jungfrau"""
    source = psana_source(env, src)
    co = get_jungfrau_config_object(env, source)
    return number_of_modules_from_config(co)


def id_jungfrau_from_config(co, iseg=None):
    """Returns (str) Id for Jungfrau configuration object"""
    if co is None  : return None
    if co.Version<3: return None

    nmods = co.numberOfModules()
    if(nmods<1): return None

    if iseg is not None and iseg<nmods:
        return id_jungfrau_module(co.moduleConfig(iseg))

    modconfig_ids = [id_jungfrau_module(co.moduleConfig(i)) for i in range(nmods)]
    return '_'.join(modconfig_ids)


def shape_from_config_jungfrau(co):
    """Returns element/panel/sensor shape (N, 512, 1024) from  psana.Jungfrau.ConfigV3 object
    """
    return (co.numberOfModules(), co.numberOfRowsPerModule(), co.numberOfColumnsPerModule())


def psana_source(env, src):
    """Returns psana.Source from string detector name or alias or psana.Source or psana.DetInfo."""

    import psana

    source = None
    if   isinstance(src, psana.Source) : source = src
    elif isinstance(src, psana.DetInfo): source = psana.Source(src) # complete_detname_from_detinfo(src)
    elif isinstance(src, str):
        detname = complete_detname(env, src)
        if detname is None: return None
        source = psana.Source(detname)
    else: raise TypeError('src parameter type should be psana.Source or str')
    if source is None: raise TypeError('src parameter type should be psana.Source or str')
    return source


def id_jungfrau(env, src, iseg=None):
    """Returns (str) Id for jungfrau detector using env and psana.Source (or str) objects"""
    #print('XXX: id_jungfrau src:', type(src))
    source = psana_source(env, src)
    co = get_jungfrau_config_object(env, source)
    if co is None: return None
    jfid = id_jungfrau_from_config(co, iseg)
    if jfid is not None: return jfid # '170505-149520170815-3d00b0'
    return string_from_source(source).replace(':','-') # e.g. 'XcsEndstation.0-Jungfrau.0'


class JFPanelCalibDir(object):
    """Works with names like '170505-149520170815-3d00b0-20171025000000'
       It does validiti check for availability of 3 or 4 fields and
       separate panel name and time stamp.
    """
    def __init__(self, dname):
        self.set_dir_name(dname)

    def set_dir_name(self, dname):
        self.dname = dname
        fields = dname.split('-')
        nfields = len(fields)
        if nfields<3 or nfields>4:
            #logger.warning('Incorrect directory name: %s' % dname)
            self.is_valid = False
            return
        elif nfields==3:
            self.pname = self.dname
            self.str_ts = None
            self.int_ts = None
        elif nfields==4:
            self.pname = dname.rsplit('-',1)[0] # '_'.join(fields[:3])
            self.str_ts = fields[3]
            self.int_ts = int(fields[3])
        self.is_valid = True

    def is_same_panel(self, other):
        if not(self.is_valid and other.is_valid): return False
        return self.pname == other.pname

    def __cmp__(self, other):
        if not self.is_same_panel(other): return None # Not-comparable names (different panel names)
        elif self.int_ts == other.int_ts: return 0
        elif self.int_ts is None and other.int_ts is not None: return -1
        elif self.int_ts is not None and other.int_ts is None: return  1
        elif self.int_ts < other.int_ts: return -1
        elif self.int_ts > other.int_ts: return  1

    def __eq__(self, other):
        return self.__cmp__(other) == 0

    def __ne__(self, other):
        return self.__cmp__(other) != 0

    def __lt__(self, other):
        return self.__cmp__(other) < 0

    def __le__(self, other):
        return self.__cmp__(other) <= 0

    def __gt__(self, other):
        return self.__cmp__(other) > 0

    def __ge__(self, other):
        return self.__cmp__(other) >= 0


def _find_panel_calib_dir(panel, dnos=DIRNAME, tstamp=None):
    """Returns panel calibration directory from dnos (dirname objects) usint timestamp.
    """
    msg = 'Find calibdir for panel: %s and timestamp: %s' % (panel, str(tstamp))
    sorted_lst = sorted([o for o in dnos if panel==o.pname])
    size = len(sorted_lst)

    msg += '\n  Selected and sorted list of %d calibdirs:' % size
    for o in sorted_lst: msg += '\n    %s' % o.dname
    logger.debug(msg)

    if   size == 0     : return None
    elif size == 1     : return sorted_lst[0].dname  # return 1st
    elif tstamp is None: return sorted_lst[-1].dname # return latest
    else: # select for time stamp
        for i,o in enumerate(sorted_lst[1:]):
            if o.int_ts > tstamp: return sorted_lst[i].dname # previous item in the list started from [1:]
    return sorted_lst[-1].dname # return latest


def find_panel_calib_dirs(jfid, dname=DIRNAME, tstamp=None):
    msg = 'Find panel directories for jungfrau %s\n      in repository %s' % (jfid, dname)
    logger.info(msg)
    msg = ''
    dnos = []
    for d in os.listdir(DIRNAME):
        dno = JFPanelCalibDir(d)
        if not dno.is_valid: continue
        dnos.append(dno)
        msg += '\n  %s'%dno.dname
    logger.debug(msg)

    return [_find_panel_calib_dir(panel, dnos, tstamp) for panel in jfid.split('_')]


def merge_panel_constants(dirs, ifname='%s/g%d_gain.npy', ofname='jf_pixel_gain', ofmt='%.4f'):
    import sys
    from PSCalib.NDArrIO import save_txt

    lst_gains = []
    for gi in range(3):
        lst_segs = []
        for dir in dirs:
            fname = ifname % (dir, gi)
            if not os.path.lexists(fname):
                msg = 'FILE IS NOT AVAILABLE: %s' % fname
                logger.warning(msg)
                sys.exit()
            nda = np.load(fname)
            logger.debug(info_ndarr(nda, 'file %s nda\n     ' % fname))
            lst_segs.append(nda)
        nda_one_gain = np.stack(tuple(lst_segs))
        logger.debug(info_ndarr(nda_one_gain, 'nda'))

        lst_gains.append(tuple(nda_one_gain))

    nda = np.stack(lst_gains)
    logger.debug(info_ndarr(nda, 'merger nda'))

    #sh = (3,<nsegs>,512,1024)

    np.save('%s.npy'%ofname, nda)
    logger.info('Save file "%s"' % ('%s.npy'%ofname))

    save_txt('%s.txt'%ofname, nda, fmt=ofmt)
    logger.info('Save file "%s"' % ('%s.txt'%ofname))


def info_jungfrau(ds, detname):
    source = psana_source(ds.env(), detname)
    strsrc = string_from_source(source).replace(':','-')
    npanels = number_of_modules_in_jungfrau(ds.env(), source)
    logger.info('Found source: %s, number of panels: %s' %(strsrc, str(npanels)))
    id_jf = id_jungfrau(ds.env(), source)
    if id_jf == strsrc: logger.warning('WARNING: numeric id is not available')
    logger.info('Jungfrau id: %s' % (id_jf))


def jungfrau_uniqueid(ds, detname):
    source = psana_source(ds.env(), detname)
    return id_jungfrau(ds.env(), source)


if __name__ == "__main__":
  import sys
  import psana


  def print_dict(d, cmt=''):
    print(cmt)
    for k,v in d.items(): print('%s: %s' % (str(k).ljust(26), v))


  def test_keys(env):
    for k in env.configStore().keys():
        print(k)
        print('  type:', k.type(), '  src:', k.src(), '  alias:', k.alias())
        src = k.src()
        if not isinstance(src, psana.DetInfo): continue
        print('  detname_from_src:', complete_detname_from_detinfo(src))


  # See Detector.examples.ex_source_dsname

  def ex_source_dsname(ntest):

    if   ntest == 1: # psana.Jungfrau.ConfigV1
        src, dsn = 'CxiEndstation.0:Jungfrau.0', 'exp=cxi11216:run=9'
        #src, dsn = ':Jungfrau.0', 'exp=cxi11216:run=9'

    elif ntest == 2: # psana.Jungfrau.ConfigV2
        src, dsn = 'XcsEndstation.0:Jungfrau.0', 'exp=xcsx22015:run=503'

    elif ntest == 3: # psana.Jungfrau.ConfigV3
        src, dsn = 'XcsEndstation.0:Jungfrau.0', 'exp=xcsls3716:run=631'

    elif ntest == 4: # psana.Jungfrau.ConfigV3
        src, dsn = 'MfxEndstation.0:Jungfrau.1', 'exp=xpptut15:run=410'

    elif ntest == 5: # psana.Jungfrau.ConfigV3
        src, dsn = 'MfxEndstation.0:Jungfrau.0', 'exp=xpptut15:run=430'

    else:
        sys.exit('Non-implemented sample for test number # %d' % ntest)

    return src, dsn


  def test_id_jungfrau(tname):

    from PSCalib.GlobalUtils import dict_detinfo_alias, dict_alias_detinfo, complete_detname

    srcname, dsname = ex_source_dsname(int(tname))
    ds  = psana.DataSource(dsname)
    src = psana.Source(srcname)
    env = ds.env()
    co = get_jungfrau_config_object(ds.env(), src)

    print('id_jungfrau_from_config(co,0): %s' % id_jungfrau_from_config(co,0))
    print('id_jungfrau_from_config(co,1): %s' % id_jungfrau_from_config(co,1))
    print('id_jungfrau_from_config(co) : %s' % id_jungfrau_from_config(co))

    print('id_jungfrau(env, src, 0): %s' % id_jungfrau(env, src, iseg=0))
    print('id_jungfrau(env, src, 1): %s' % id_jungfrau(env, src, iseg=1))
    print('id_jungfrau(env, src)  : %s' % id_jungfrau(env, src))
    print('id_jungfrau(env, "Jung"): %s' % id_jungfrau(env, 'Jung'))
    print('id_jungfrau(env, "jungfrau1M"): %s' % id_jungfrau(env, 'jungfrau1M'))
    print('id_jungfrau(env, "Jungfrau"): %s' % id_jungfrau(env, 'Jungfrau'))

    #test_keys(env)
    print_dict(dict_detinfo_alias(env), cmt='\ndict_detinfo_alias(env):')
    print_dict(dict_alias_detinfo(env), cmt='\ndict_alias_detinfo(env):')

    print('complete_detname for full name Xcs: ', complete_detname(env, 'XcsEndstation.0:Jungfrau.0'))
    print('complete_detname for full name Cxi: ', complete_detname(env, 'CxiEndstation.0:Jungfrau.0'))
    print('complete_detname for "Jungfrau.0" : ', complete_detname(env, 'Jungfrau.0'))
    print('complete_detname for "jungfrau1M" : ', complete_detname(env, 'jungfrau1M'))
    print('complete_detname for "Jungfrau"   : ', complete_detname(env, 'Jungfrau'))


if __name__ == "__main__":
    print(80*'_')
    logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '5'
    if tname in ('1', '2', '3', '4', '5'): test_id_jungfrau(tname)
    else: sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

# EOF
