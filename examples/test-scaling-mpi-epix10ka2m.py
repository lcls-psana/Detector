"""
> s3dflogin
> psana
srun --partition milano --account lcls:prjdat21 -n 1 --time=05:00:00 --exclusive --pty /bin/bash --exclude sdfmilan022

in other window

> s3dflogin
ssh -Y sdfmilan216
cd LCLS/con-py3

source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/setup_testrel

mpirun -n 1 python  Detector/examples/test-scaling-mpi-epix10ka2m.py 1
mpirun -n 80 python Detector/examples/test-scaling-mpi-epix10ka2m.py 1

python Detector/examples/test-scaling-mpi-epix10ka2m.py <Test-number>
"""

import os
import sys
import numpy as np
from time import time
#from Detector.UtilsJungfrau import Cache


import psutil
from CalibManager.GlobalUtils import get_hostname, load_textfile
from CalibManager.PlotImgSpeWidget import proc_stat
from PSCalib.GlobalUtils import save_textfile, string_from_source #, complete_detname
from Detector.GlobalUtils import info_ndarr, divide_protected
#from Detector.UtilsCommonMode import common_mode_cols,\
#                                     common_mode_rows_hsplit_nbanks, common_mode_2d_hsplit_nbanks
import pyimgalgos.Graphics as gr
from pyimgalgos.GlobalUtils import reshape_to_2d

#import Detector.UtilsJungfrau as uj
import Detector.UtilsEpix10ka as ue

# CALIBMET options
CALIB_STD      = 0
CALIB_LOCAL    = 1
CALIB_LOCAL_V2 = 2
CALIB_V2       = 3
FNAME_START_TIME = 'figs/mpi-job-2nd-evt-time.txt' # save job start time in multi-runk mpi

def hist_stat(hi):
    """returns mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w"""
    wei, bins, patches = hi
    return proc_stat(wei, bins)


def hist(arr, amp_range=None, bins=200, figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80),\
         title='title', xlabel='xlabel', ylabel='ylabel',titwin=None):
    fig = gr.figure(figsize=figsize, dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None, title=titwin)
    ax = gr.add_axes(fig, axwin=axwin)
    his = gr.hist(ax, arr, bins=bins, amp_range=amp_range, weights=None, color=None, log=False)
    gr.add_title_labels_to_axes(ax, title=title, xlabel=xlabel, ylabel=ylabel, fslab=14, fstit=20, color='k')
    return fig, ax, his


def plot(y, amp_range=None, figsize=(6,5), axwin=(0.15, 0.12, 0.78, 0.80), pfmt='bo', lw=1,\
         title='set_title', xlabel='xlabel', ylabel='ylabel', titwin=None):
    fig = gr.figure(figsize=figsize, dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None, title=titwin)
    x = list(range(len(y)))
    ax = gr.add_axes(fig, axwin=axwin)
    p = ax.plot(x, y, pfmt, linewidth=lw)
    if amp_range is not None: ax.set_ylim(amp_range)
    gr.add_title_labels_to_axes(ax, title=title, xlabel=xlabel, ylabel=ylabel, fslab=14, fstit=20, color='k')
    return fig, ax, p


def image(img, amin=None, amax=None):
    fig, axim, axcb = gr.fig_img_cbar_axes(fig=None)
    imsh, cbar = gr.imshow_cbar(fig, axim, axcb, img, amin=amin, amax=amax)
    return fig, imsh, cbar





def calib_epix10ka_any(det, evt, cmpars=None, **kwa): # cmpars=(7,2,10,10), mbits=None, mask=None, nda_raw=None
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
      - mbits - deprecated parameter of the det.mask_comb(...), det.mask_v2 is used by default
      - mask - user defined mask passed as optional parameter
    """

    t00 = time()

    logger.debug('In calib_epix10ka_any')

    nda_raw = kwa.get('nda_raw', None)
    raw = det.raw(evt) if nda_raw is None else nda_raw # shape:(352, 384) or suppose to be later (<nsegs>, 352, 384) dtype:uint16
    if raw is None: return None

    t01 = time()

    cmp  = det.common_mode(evt) if cmpars is None else cmpars
    gain = det.gain(evt)      # - 4d gains  (7, <nsegs>, 352, 384)
    peds = det.pedestals(evt) # - 4d pedestals
    if gain is None: return None # gain = np.ones_like(peds)  # - 4d gains
    if peds is None: return None # peds = np.zeros_like(peds) # - 4d gains

    t02 = time()

    store = ue.dic_store.get(det.name, None)

    if store is None:
        logger.debug('create store for detector %s' % det.name)
        store = ue.dic_store[det.name] = ue.Storage()

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

    t03 = time()

    gfac = store.gfac

    gmaps = ue.gain_maps_epix10ka_any(det, raw)
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

    t04 = time()

    store.counter += 1
    if not store.counter%100:
        logger.debug(ue.info_gain_mode_arrays1(gmaps)\
               +'\n'+ue.info_pixel_gain_mode_statistics1(gmaps))

    arrf = np.array(raw & ue.M14, dtype=np.float32) - pedest

    t05 = time()

    if store.mask is None:
       store.mask = det.mask_total(evt, **kwa)
    mask = store.mask

    t06 = time()

    logger.debug('common-mode correction pars cmp: %s' % str(cmp))

    if cmp is not None:
      mode, cormax = int(cmp[1]), cmp[2]
      npixmin = cmp[3] if len(cmp)>3 else 10
      if mode>0:

        t07 = t0_sec_cm = time()

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

        t08 = time()

        #sh = (nsegs, 352, 384)
        hrows = 176 # int(352/2)
        for s in range(arrf.shape[0]):

          t09 = time()

          if mode & 4: # in banks: (352/2,384/8)=(176,48) pixels
            ue.common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=8, cormax=cormax, npix_min=npixmin)
            ue.common_mode_2d_hsplit_nbanks(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], nbanks=8, cormax=cormax, npix_min=npixmin)

          t10 = time()

          if mode & 1: # in rows per bank: 384/8 = 48 pixels # 190ms
            ue.common_mode_rows_hsplit_nbanks(arrf[s,], mask=gmask[s,], nbanks=8, cormax=cormax, npix_min=npixmin)

          t11 = time()

          if mode & 2: # in cols per bank: 352/2 = 176 pixels # 150ms
            ue.common_mode_cols(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], cormax=cormax, npix_min=npixmin)
            ue.common_mode_cols(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], cormax=cormax, npix_min=npixmin)

        logger.debug('TIME common-mode correction = %.6f sec for cmp=%s' % (time()-t0_sec_cm, str(cmp)))

        t12 = time()
        res = arrf * factor if mask is None else arrf * factor * mask # gain correction

    t13 = time()

    logger.debug('TOTAL consumed time (sec) = %.6f' % (t13-t00)\
                +info_ndarr(factor, '\n  calib_epix10ka factor')\
                +info_ndarr(pedest, '\n  calib_epix10ka pedest'))

    return res, (t00, t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13)




class DetCache():
    """ Cash of calibration constants for epix10ka2m.
    """
    def __init__(self, det, evt, **kwa):
        print('DetCache for epix10ka2m')
        #self.poff = None
        #self.arr1 = None
        self.kwa = kwa
        self.peds = None
        self.gfac = None
        self.mask = None
        self.outa = None
        self.cmps = None
        self.aone = None
        self.isset = False
        self.evnum = 0
        self.add_calibcons(det, evt)

    def kwargs_are_the_same(self, **kwa):
        return self.kwa == kwa

    def add_calibcons(self, det, evt):

        self.detname = string_from_source(det.source)

        #arr  = np.array(det.raw(evt), dtype=np.float32)
        self.peds = det.pedestals(evt) # - 4d pedestals shape:(3, 1, 512, 1024) dtype:float32
        if self.peds is None: return

        gain = det.gain(evt)      # - 4d gains
        if gain is None: gain = np.ones_like(self.peds)  # - 4d gains

        self.gfac = divide_protected(np.ones_like(self.peds), gain)
        #self.arr1 = np.ones(self.peds.shape[1:], dtype=np.int8)
        self.outa = np.zeros(self.peds.shape[1:], dtype=np.float32)

        #self.cmps  = det.common_mode(evt) if cmpars is None else cmpars
        #self.mask = det.mask_total(evt, **kwa)

        self.isset = True



class Cache():
    """ Wrapper around dict {detname:DetCache} for cache of calibration constants.
    """
    def __init__(self):
        self.calibcons = {}

    def add_detcache(self, det, evt, **kwa):
        detname = string_from_source(det.source)
        if isinstance(detname, str):
            o = self.calibcons[detname] = DetCache(det, evt, **kwa)
            return o
        return None

    def detcache_for_detname(self, detname):
        return self.calibcons.get(detname, None)

    def detcache_for_detobject(self, det):
        detname = string_from_source(det.source)
        return self.detcache_for_detname(detname)

cache = Cache() # singleton





def calib_epix10ka_v2(det, evt, cmpars=None, **kwa): # cmpars=(7,2,10,10), mbits=None, mask=None, nda_raw=None
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
      - mbits - deprecated parameter of the det.mask_comb(...), det.mask_v2 is used by default
      - mask - user defined mask passed as optional parameter
    """

    t00 = time()

    logger.debug('calib_epix10ka_v2')

    nda_raw = kwa.get('nda_raw', None)
    raw = det.raw(evt) if nda_raw is None else nda_raw # shape:(352, 384) or suppose to be later (<nsegs>, 352, 384) dtype:uint16
    if raw is None: return None

    t01 = time()

    detname = string_from_source(det.source) # str, i.e. XcsEndstation.0:Epix10ka2M.0
    odc = cache.detcache_for_detname(detname)
    first_entry = odc is None
    if first_entry:
       t_first = time()
       odc = cache.add_detcache(det, evt, **kwa)
       odc.cmps = det.common_mode(evt) if cmpars is None else cmpars
       odc.mask = det.mask_total(evt, **kwa)
       odc.aone = np.ones_like(raw, dtype=np.int8)
       odc.loop_segs = kwa.get('loop_segs', True)

       logger.info('\n  ====================== det.name: %s' % det.name\
                   +'\n  detname from source: %s' % detname\
                   +info_ndarr(raw,  '\n  calib_epix10ka_v2 first entry:\n    raw ')\
                   +info_ndarr(odc.peds, '\n    peds')\
                   +info_ndarr(odc.gfac, '\n    gfac')\
                   +info_ndarr(odc.mask, '\n    mask')\
                   +info_ndarr(odc.outa, '\n    outa')\
                   +'\n    ' + info_ndarr(odc.cmps, 'common mode parameters ')
                   +'\n    loop over segments: %s' % odc.loop_segs
                   +'\n    1-st entry consumed time (sec): %.3f' % (time() - t_first))

    odc.evnum += 1
    cmps = odc.cmps
    gfac = odc.gfac
    peds = odc.peds
    mask = odc.mask
    aone = odc.aone
    outa = odc.outa

    arr = raw

    gmap = ue.gain_maps_epix10ka_any(det, raw)  #shape:(7, 16, 352, 384)
    if gmap is None: return None
    gmap = np.array(gmap)

    t02 = time()

    if not odc.evnum%100:
        logger.info(ue.info_gain_mode_arrays1(gmap)\
               +'\n'+ue.info_pixel_gain_mode_statistics1(gmap))

    if first_entry: print(info_ndarr(gmap, 'first_entry gmap'))

    if odc.loop_segs:
      nsegs = arr.shape[0]   # 16 for epix10ka2m
      shseg = arr.shape[-2:] # (352, 384)
      if first_entry: logger.info('first_entry: number of segments: %d   segment shape: %s' % (nsegs, str(shseg)))

      for i in range(nsegs):
        # define per-segment arrays
        #print('ev:%d seg:%02d' % (odc.evnum, i))
        arr1s = arr[i,:]
        aone1 = aone[i,:]
        mask1 = None if mask is None else mask[i,:]
        gfac1 = None if gfac is None else gfac[:,i,:,:]
        peds1 = None if peds is None else peds[:,i,:,:]
        gmap1 = None if gmap is None else gmap[:,i,:,:]
        arr1s.shape  = (1,) + shseg
        if mask1 is not None: mask1.shape = (1,) + shseg
        if gfac1 is not None: gfac1.shape = (7,1,) + shseg
        if peds1 is not None: peds1.shape = (7,1,) + shseg
        if gmap1 is not None: gmap1.shape = (7,1,) + shseg
        #print(info_ndarr(arr1s,  'XXX  arr1s '))
        #print(info_ndarr(peds1, 'XXX  peds11 '))
        out1, t03_12 = calib_epix10ka_nda(arr1s, gfac1, peds1, mask1, cmps, gmap1, aone1)
        #print(info_ndarr(out1, 'XXX  out1 '))
        outa[i,:] = out1[0,:]
      #print(info_ndarr(outa, 'XXX  outa '))
      #sys.exit('TEST EXIT')
      #return outa
    else:
      outa, t03_12 = calib_epix10ka_nda(arr, gfac, peds, mask, cmps, gmap, aone)

    t13 = time()

    #t02 = t03 = t04 = t05 = t06 = t07 = t08 = t09 = t10 = t11 = t12 = t13

    times = (t00, t01, t02) + t03_12 + (t13,)
    return outa, times # (t00, t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13)



def calib_epix10ka_nda(arr, gfac, peds, mask, cmps, gmap, aone):

    t03 = time()

    raw = arr

    # FH, FM, FL, AHL-H, AML-M, AHL-L, AML-L
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmap

    factor = np.select(gmap,\
                       (gfac[0,:], gfac[1,:], gfac[2,:], gfac[3,:],\
                        gfac[4,:], gfac[5,:], gfac[6,:]), default=1) # 2msec

    t04 = time()
    pedest = np.select(gmap,\
                       (peds[0,:], peds[1,:], peds[2,:], peds[3,:],\
                        peds[4,:], peds[5,:], peds[6,:]), default=0)

    t05 = time()

    arrf = np.array(raw & ue.M14, dtype=np.float32) - pedest
    res = arrf

    t06 = time()

    if True: # False: #cmps is not None:
      mode, cormax = int(cmps[1]), cmps[2]
      npixmin = cmps[3] if len(cmps)>3 else 10
      if mode>0:

        t07 = t0_sec_cm = time()

        arr1 = aone # np.ones_like(mask, dtype=np.uint8)
        grhm = np.select((gr0,  gr1,  gr3,  gr4), (arr1, arr1, arr1, arr1), default=0)
        gmask = np.bitwise_and(grhm, mask) if mask is not None else grhm
        if gmask.ndim == 2: gmask.shape = (1,gmask.shape[-2],gmask.shape[-1])

        logger.debug(info_ndarr(gmask, 'gmask')\
                     + '\n  per panel statistics of cm-corrected pixels: %s'%
                     str(np.sum(gmask, axis=(1,2), dtype=np.uint32) if gmask is not None else None))

        t08 = time()

        #sh = (nsegs, 352, 384)
        hrows = 176 # int(352/2)
        for s in range(arrf.shape[0]):

          t09 = time()

          if mode & 4: # in banks: (352/2,384/8)=(176,48) pixels
            ue.common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=8, cormax=cormax, npix_min=npixmin)
            ue.common_mode_2d_hsplit_nbanks(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], nbanks=8, cormax=cormax, npix_min=npixmin)

          t10 = time()

          if mode & 1: # in rows per bank: 384/8 = 48 pixels # 190ms
            ue.common_mode_rows_hsplit_nbanks(arrf[s,], mask=gmask[s,], nbanks=8, cormax=cormax, npix_min=npixmin)

          t11 = time()

          if mode & 2: # in cols per bank: 352/2 = 176 pixels # 150ms
            ue.common_mode_cols(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], cormax=cormax, npix_min=npixmin)
            ue.common_mode_cols(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], cormax=cormax, npix_min=npixmin)

        logger.debug('TIME common-mode correction = %.6f sec for cmps=%s' % (time()-t0_sec_cm, str(cmps)))

        t12 = time()
        res = arrf * factor if mask is None else arrf * factor * mask # gain correction

    return res, (t03, t04, t05, t06, t07, t08, t09, t10, t11, t12)








def calib_std(det, evt, cmpars=None, mbits=None, **kwargs):
    """det.calib for epix10ka"""
    kwargs['mbits']=mbits
    return ue.calib_epix10ka_any(det, evt, cmpars=cmpars, **kwargs) # cmpars=(7,2,10,10), mbits=None, mask=None, nda_raw=None
    #return uj.calib_jungfrau(det, evt, cmpars=cmpars, **kwargs)


def calib_epix10ka_local(det, evt, cmpars=None, mbits=None, **kwargs):
    """local version of det.calib for epix10ka"""
    kwargs['mbits']=mbits
    return calib_epix10ka_any(det, evt, cmpars=cmpars, **kwargs)


def calib_epix10ka_local_v2(det, evt, cmpars=None, mbits=None, **kwargs):
    """v2 - improved local version of det.calib for epix10ka"""
    kwargs['mbits']=mbits
    return calib_epix10ka_v2(det, evt, cmpars=cmpars, **kwargs)



def test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='v00', CALIBMET=CALIB_LOCAL, loop_segs=False):

    from psana import MPIDataSource, Detector

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    hostname = get_hostname()
    cpu_num = psutil.Process().cpu_num()
    print('rank:%03d cpu_num:%03d size:%02d' % (rank, cpu_num, size))

    #ranks = (0, 10)
    ranks = (0, 10, 20, 30, 40, 50, 60, 70)
    nevents = 101
    #nevents = 380 # at 80-core
    #nevents = 254 # at 120-core
    #nevents = 380*80 # at single core
    ntpoints = 14 if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2) else 18 # for CALIB_LOCAL_V2
    arrts = np.zeros((nevents,ntpoints), dtype=np.float64) if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2) else\
            np.zeros(nevents, dtype=np.float64)

    #ds = MPIDataSource('exp=cxilx7422:run=232') # 8-panel 31652 events
    #det = Detector('CxiDs1.0:Jungfrau.0')
    # datinfo -e xcsl1030422 -r 237 -d XcsEndstation.0:Epix10ka2M.0
    ds = MPIDataSource('exp=xcsl1030422:run=237')
    det = Detector('XcsEndstation.0:Epix10ka2M.0')
    ds.break_after(nevents*size)

    nevt = -1
    #for irun,orun in enumerate(ds.runs()):
    # if rank ==0: print('==== %d ==== runnum:' % (irun, orun.run()))
    #  for istep,step in enumerate(ds.steps()):
    calib = None
    for ievt,evt in enumerate(ds.events()):
        raw = det.raw(evt) # prefetch the data from disk
        if raw is None:
            print('WARNING: det.raw is None for ievt:%02d rank:%03d' % (ievt, rank))
            continue
        nevt += 1
        #if nevt >= nevents:
        #    print('WARNING: nevt:%03d - break   ievt:%02d rank:%03d' % (nevt, ievt, rank))
        #    break

        if nevt==1 and not os.path.exists(FNAME_START_TIME):
            ttot_sec = time() # init ttot_sec, skip nevt==0
            save_textfile(str(ttot_sec), FNAME_START_TIME, mode='w')
            logger.info('rank:%03d job 2-nd evt time:%.6f saveed in file: %s' % (rank, ttot_sec, FNAME_START_TIME))

        if CALIBMET == CALIB_STD:
            t0_sec = time()
            calib = calib_std(det, evt, cmpars=None)
            dt_sec = time()-t0_sec
            arrts[nevt] = dt_sec
        elif CALIBMET == CALIB_LOCAL:
            calib, times = calib_epix10ka_local(det, evt, cmpars=(7,7,200,10))
            dt_sec = times[13] - times[0]
            arrts[nevt,:] = times
        elif CALIBMET == CALIB_LOCAL_V2:
            calib, times = calib_epix10ka_local_v2(det, evt, cmpars=(7,7,200,10), loop_segs=loop_segs)
            dt_sec = times[13] - times[0]
            arrts[nevt,:] = times
        elif CALIBMET == CALIB_V2:
            t0_sec = time()
            calib = calib_v2(det, evt, cmpars=None, loop_segs=loop_segs)
            dt_sec = time()-t0_sec
            arrts[nevt] = dt_sec
        else:
            sys.exit('WARNING: CALIBMET %s IS NOT DEFINED!' % str(CALIBMET))

        cpu_num = psutil.Process().cpu_num()
        #if cpu_num >=16 and cpu_num <=23:
        #    print('rank:%03d cpu_num:%03d nevt:%03d time:%.6f CPU_NUM IN WEKA RANGE [16,23]' % (rank, cpu_num, nevt, dt_sec))
        if nevt%10>0: continue
        print('rank:%03d cpu_num:%03d nevt:%04d time:%.6f' % (rank, cpu_num, nevt, dt_sec))

    s = load_textfile(FNAME_START_TIME)
    recs = s.split('\n')
    ttot_sec = eval(recs[0])

    logger.info('Summary for rank:%03d job 2-nd evt time:%.6f time total (sec):%.6f' % (rank, ttot_sec, time()-ttot_sec))

    #if False:
    #if rank in ranks:
    if rank == 0:
        amp_range=(0, 0.5)
        #dt = arrts[1:,14] - arrts[1:,0] if CALIBMET == CALIB_LOCAL else\
        dt = arrts[1:,13] - arrts[1:,0] if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2) else\
             arrts[1:]
        print(info_ndarr(dt, 'rank:%03d times:' % rank, last=nevents))
        tit = '%s rank %03d of %03d cpu_num %03d' % (hostname, rank, size, cpu_num)

        fhi, ahi, his = hist(dt, amp_range=amp_range, title=tit, xlabel='dt, sec', ylabel='dN/dt', titwin=tit + ' time per event')
        fpl, apl, spl = plot(dt, amp_range=amp_range, title=tit, xlabel='event', ylabel='t, sec', titwin=tit + ' time vs event')

        mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w = hist_stat(his)
        rec = 'hostname:%s rank:%03d cpu:%03d cmt:%s proc time (sec) mean: %.4f +/- %.4f rms: %.4f +/- %.4f\n'%\
              (hostname, rank, cpu_num, cmt, mean, err_mean, rms, err_rms)
        print(rec)
        fnprefix = 'figs/fig-mpi-data-%s-%s-ncores%02d' % (cmt, hostname, size)
        save_textfile(rec, fnprefix+'-summary.txt', mode='a')

        arrts = arrts[1:,:] # exclude 1st event
        arrts[:,1:] -= arrts[:,0:-1] # evaluate dt for each step
        arrts[:,0]   = dt   # elt 0: total time per event
        arrts[:,:]  *= 1000 # convert sec > msec

        if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2):
            print_summary(arrts)
            if SAVE_FIGS:
                print('plot_figs_local\nfnprefix: %s title: %s' % (fnprefix, tit))
                plot_figs(arrts, tit)

        if SAVE_FIGS:
            fnprefix1 = '%s-rank%02d-cpu%03d' % (fnprefix, rank, cpu_num)
            gr.save_fig(fhi, fname=fnprefix1+'-time.png')
            gr.save_fig(fpl, fname=fnprefix1+'-time-vs-evt.png')
            if rank == 0:
                fim, imsh, cbar = image(reshape_to_2d(calib), amin=None, amax=None)
                gr.save_fig(fim, fname=fnprefix1+'-image.png')

        if SHOW_FIGS:
            gr.show()


def print_summary(arrts):
    print(info_ndarr(arrts, 'arrts[msec]:', last=100))
    fmt = 14*' %9.4f'
    for n,r in enumerate(range(arrts.shape[0])):
        times = arrts[r,:]
        print('%03d '%n, fmt % tuple(times))

    #s = '     '.join(['  t%02d'%i for i in range(1,arrts.shape[1])])
    s = '     '.join(['  t%02d'%i for i in range(0,arrts.shape[1])])
    print('dt, ms:  %s' % s)

    #tmed = np.median(arrts[:,1:], axis=0)
    tmed = np.median(arrts[:,:], axis=0)
    print('median:' + (fmt % tuple(tmed)))


def plot_figs(arrts, tit):
      print('hist title: %s' % tit)
      for t in (1,2,3,4,5,6,7,8,9,10,11,12,13):
        dt = arrts[:,t]
        amp_range = (0,10) if t==13 else\
                    (0,100) if t in (14,15,16) else\
                    (0,5) if t in (6,) else\
                    (0,0.01) if t in (9,7) else\
                    (0,400) if t in (3,) else\
                    (0,20) if t in (11,12) else\
                    (0,10)
        dtitle = 'dt%02d' % t
        _, _, _ = hist(dt, amp_range=amp_range, title=dtitle + ' ' + tit,\
                             xlabel='%s, msec' % dtitle, ylabel='dN/dt', titwin=dtitle + ' ' + tit + ' time per event')



def selector(mode):
    if os.path.exists(FNAME_START_TIME):
        cmd = 'rm %s' % FNAME_START_TIME
        os.system(cmd)
        print('execute command:', sys.argv)
    #print('sys.argv:', sys.argv)
    #print('selector for mode: %s' % str(mode))
    #if mode >-1 and mode<128: do_algo(cpu=mode, cmt='v0' if len(sys.argv)<3 else sys.argv[2], SHOW_FIGS=False, SAVE_FIGS=False)
    if   mode == 1: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='16p-v1', CALIBMET=CALIB_STD)
    elif mode == 2: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='16p-v2', CALIBMET=CALIB_LOCAL)
    elif mode == 3: test_mpi_for_data(SHOW_FIGS=False,SAVE_FIGS=False,cmt='16p-v3', CALIBMET=CALIB_LOCAL_V2, loop_segs=False)
    elif mode == 4: test_mpi_for_data(SHOW_FIGS=False,SAVE_FIGS=False,cmt='16p-v4', CALIBMET=CALIB_LOCAL_V2, loop_segs=True)
    elif mode == 5: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='16p-v5', CALIBMET=CALIB_V2, loop_segs=False)
    elif mode == 6: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='16p-v6', CALIBMET=CALIB_V2, loop_segs=True)
    elif mode ==-99: sort_records_in_files()
    else: print ('ERROR: NON-IMPLEMENTED mode: %s' % str(mode))


if __name__ == "__main__":

    if len(sys.argv) < 2:
        import inspect
        USAGE = '\nUsage: %s <tname>\n' % sys.argv[0].split('/')[-1]\
              + '\n'.join([s for s in inspect.getsource(selector).split('\n') if "mode ==" in s])
        print('\n%s\n' % USAGE)
    else:
        from Detector.UtilsLogging import sys, logging, STR_LEVEL_NAMES, basic_config
        logger = logging.getLogger(__name__)
        basic_config(format='[%(levelname).1s] L%(lineno)04d: %(filename)s %(message)s', int_loglevel=None, str_loglevel='INFO')
        mode = int(sys.argv[1])
        selector(mode)

# EOF
