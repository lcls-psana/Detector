
"""
> s3dflogin
srun --partition milano --account lcls:prjdat21 -n 1 --time=02:00:00 --exclusive --pty /bin/bash

in other window

> s3dflogin
ssh -Y sdfmilan216
cd LCLS/con-py3

source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/psconda.sh
source /sdf/group/lcls/ds/ana/sw/conda1/manage/bin/setup_testrel

mpirun -n 1 python  Detector/examples/test-scaling-mpi.py 2
mpirun -n 80 python Detector/examples/test-scaling-mpi.py 2
python Detector/examples/test-scaling-mpi.py -99
"""
#import logging
#logger = logging.getLogger(__name__)


import os
import sys
import numpy as np
from time import time

import psutil
from CalibManager.GlobalUtils import get_hostname, load_textfile
from CalibManager.PlotImgSpeWidget import proc_stat
from PSCalib.GlobalUtils import save_textfile, string_from_source #, complete_detname
from Detector.GlobalUtils import info_ndarr, divide_protected
from Detector.UtilsCommonMode import common_mode_cols,\
                                     common_mode_rows_hsplit_nbanks, common_mode_2d_hsplit_nbanks
import pyimgalgos.Graphics as gr
from pyimgalgos.GlobalUtils import reshape_to_2d

import Detector.UtilsJungfrau as uj

store = uj.store
cache = uj.cache
BW1, BW2, BW3, MSK = uj.BW1, uj.BW2, uj.BW3, uj.MSK

# CALIBMET options
CALIB_LOCAL    = 0
CALIB_STD      = 1
CALIB_V2       = 2
CALIB_LOCAL_V2 = 3
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


def random_standard(shape=(40,60), mu=200, sigma=25, dtype=np.float64):
    a = mu + sigma*np.random.standard_normal(shape)
    return np.require(a, dtype)


#def random_arrays(sh2d = (512,1024), dtype=np.float32): # v1.000
#def random_arrays(sh2d = (256,1024), dtype=np.float32): # v1o2
#def random_arrays(sh2d = (128,1024), dtype=np.float32): # v1o4
#def random_arrays(sh2d = (64,1024), dtype=np.float32): # v1o8
#def random_arrays(sh2d = (1024,1024), dtype=np.float32): # v2o1
def random_arrays(sh2d = (2048,1024), dtype=np.float32): # v4o1
    """returns simulated det.raw, pedestals, gain, offset, mask, gfac, factor1, offset1, out
     raw shape:(1, 512, 1024) size:524288 dtype:uint16 [2734 2664 2675 2651 2633...]
     peds shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [2723.69  2668.95
     gain shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [36.8558 37.24   36.5578 36.7929 36.1728...]
     offs shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [0. 0. 0. 0. 0....]
     gfac shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [0.02713277 0.02685284 0.02735394 0.02717916 0.02764508...]
     arrf shape:(1, 512, 1024) size:524288 dtype:float32 [ 6.7856445
     factor shape:(1, 512, 1024) size:524288 dtype:float32 [0.02713277 0.02685284
     offset shape:(1, 512, 1024) size:524288 dtype:float32 [0. 0. 0.
     mask shape:(1, 512, 1024) size:524288 dtype:uint8 [1 1 1 1 1...]
     resp shape:(1, 512, 1024) size:524288 dtype:float32 [0.18411334 0.12152617 0.08894039 0.11908797 0.5094565 ...]
    """
    sh3d = (3,) + sh2d
    raw  = random_standard(shape=sh2d, mu=2650, sigma=20, dtype=np.uint16)
    peds = random_standard(shape=sh3d, mu=2650, sigma=20, dtype=dtype)
    gain = random_standard(shape=sh3d, mu=36.5, sigma=0.1, dtype=dtype)
    offs = random_standard(shape=sh3d, mu=0.5, sigma=0.1, dtype=dtype)
    gfac = random_standard(shape=sh3d, mu=0.027, sigma=0.002, dtype=dtype)
    arrf = random_standard(shape=sh2d, mu=6.75, sigma=0.3, dtype=dtype)
    factor = random_standard(shape=sh2d, mu=0.027, sigma=0.002, dtype=dtype)
    offs = random_standard(shape=sh2d, mu=0.5, sigma=0.1, dtype=dtype)
    mask = np.ones_like(raw, dtype=np.uint8)
    resp = random_standard(shape=sh2d, mu=0.2, sigma=0.01, dtype=dtype)
    return arrf, peds, gain, offs, gfac, raw, factor, offs, mask, resp


def time_consuming_algorithm():
    a, b, _, _, _, _, _, _, _, _ = random_arrays()
    t0_sec = time()
    gr1 = a>=7.1
    gr2 = (a>6.5) & (a<7.1)
    gr3 = a<=6.5
    a[gr1] -= b[0, gr1]
    a[gr2] -= b[1, gr2]
    a[gr3] -= b[2, gr3]
    return time() - t0_sec


def test_mpi_for_random(SHOW_FIGS=True, SAVE_FIGS=True, cmt='v1.000'):

    from mpi4py import MPI
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    hostname = get_hostname()
    cpu_num = psutil.Process().cpu_num()
    print('rank:%02d cpu_num:%03d size:%02d' % (rank, cpu_num, size))

    ranks = (0, 10, 20, 30, 40, 50, 60, 70)
    nevents = 100
    arrts = np.zeros((nevents, size), dtype=np.float64)

    for nevt in range(nevents):
        dt_sec = time_consuming_algorithm()
        arrts[nevt,rank] = dt_sec  # dt_sec = time()-t0_sec
        cpu_num = psutil.Process().cpu_num()
        if cpu_num >=16 and cpu_num <=23:
            print('rank:%02d cpu_num:%03d nevt:%03d time:%.6f CPU_NUM IN WEKA RANGE [16,23]' % (rank, cpu_num, nevt, dt_sec))
        if nevt%10>0: continue
        print('rank:%02d cpu_num:%03d nevt:%03d time:%.6f' % (rank, cpu_num, nevt, dt_sec))


    amp_range=(0, 1.0)
    times = arrts[:,rank]
    print(info_ndarr(times, 'rank:%d times:' % rank, last=nevents))
    tit = '%s rank %02d of %02d cpu_num %03d' % (hostname, rank, size, cpu_num)

    fhi, ahi, his = hist(times, amp_range=amp_range, title=tit, xlabel='dt, sec', ylabel='dN/dt', titwin=tit + ' time per event')
    fpl, apl, spl = plot(times, amp_range=amp_range, title=tit, xlabel='event', ylabel='t, sec', titwin=tit + ' time vs event')

    mean, rms, err_mean, err_rms, neff, skew, kurt, err_err, sum_w = hist_stat(his)
    rec = 'hostname:%s rank:%03d cpu:%03d cmt:%s proc time (sec) mean: %.4f +/- %.4f rms: %.4f +/- %.4f\n' % (hostname, rank, cpu_num, cmt, mean, err_mean, rms, err_rms)
    print(rec)
    fnprefix = 'figs/fig-mpi-rand-%s-%s-ncores%02d' % (cmt, hostname, size)
    save_textfile(rec, fnprefix+'-summary.txt', mode='a')

    if rank in ranks:
        if SAVE_FIGS:
            fnprefix = '%s-rank%02d-cpu%03d' % (fnprefix, rank, cpu_num)
            gr.save_fig(fhi, fname=fnprefix+'-time.png')
            gr.save_fig(fpl, fname=fnprefix+'-time-vs-evt.png')

        if SHOW_FIGS:
            gr.show()



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

    t00 = time()

    src = det.source # - src (psana.Source)   - Source object

    nda_raw = kwa.get('nda_raw', None)
    arr = det.raw(evt) if nda_raw is None else nda_raw # shape:(<npanels>, 512, 1024) dtype:uint16
    if arr is None: return None

    t01 = time()

    peds = det.pedestals(evt) # - 4d pedestals shape:(3, 1, 512, 1024) dtype:float32
    if peds is None: return None

    t02 = time()

    gain = det.gain(evt)      # - 4d gains
    offs = det.offset(evt)    # - 4d offset

    t03 = time()

    detname = string_from_source(det.source)
    cmp = det.common_mode(evt) if cmpars is None else cmpars

    t04 = time()

    if gain is None: gain = np.ones_like(peds)  # - 4d gains
    if offs is None: offs = np.zeros_like(peds) # - 4d gains

    #print(info_ndarr(arr,  'raw')) # raw shape:(1, 512, 1024) size:524288 dtype:uint16 [2734 2664 2675 2651 2633...]
    #print(info_ndarr(peds, 'peds')) # peds shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [2723.69  2668.95
    #print(info_ndarr(gain, 'gain')) # gain shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [36.8558 37.24   36.5578 36.7929 36.1728...]
    #print(info_ndarr(offs, 'offs')) # offs shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [0. 0. 0. 0. 0....]

    # cache
    gfac = store.gfac.get(detname, None) # det.name
    if gfac is None:
       gfac = divide_protected(np.ones_like(peds), gain)
       store.gfac[detname] = gfac
       store.arr1 = np.ones_like(arr, dtype=np.int8)

    t05 = time()

    # Define bool arrays of ranges
    # faster than bit operations
    gr0 = arr <  BW1              # 490 us
    gr1 =(arr >= BW1) & (arr<BW2) # 714 us
    gr2 = arr >= BW3              # 400 us

    t06 = time()

    # Subtract pedestals
    arrf = np.array(arr & MSK, dtype=np.float32)

    t07 = time()

    arrf[gr0] -= peds[0,gr0]
    arrf[gr1] -= peds[1,gr1] #- arrf[gr1]
    arrf[gr2] -= peds[2,gr2] #- arrf[gr2]

    t08 = time() # - t07 = 11.15ms

    factor = np.select((gr0, gr1, gr2), (gfac[0,:], gfac[1,:], gfac[2,:]), default=1) # 2msec

    t09 = time()  # - t07 = 11.2ms

    offset = np.select((gr0, gr1, gr2), (offs[0,:], offs[1,:], offs[2,:]), default=0)

    t10 = time() # - t07 = 11.4ms

    arrf -= offset # Apply offset correction

    t11 = time()
    #print('   time to subtract offset(sec): %.06f' % (t11-t10)) # ~< 100us

    if store.mask is None:
       store.mask = det.mask_total(evt, **kwa)
    mask = store.mask

    t12 = time()

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

    t13 = time()

    resp = arrf * factor if mask is None else arrf * factor * mask # gain correction

    #print(info_ndarr(gr0, 'gr0')) # gr0 shape:(1, 512, 1024) size:524288 dtype:bool
    #print(info_ndarr(gr1, 'gr1'))
    #print(info_ndarr(gr2, 'gr2'))
    #print(info_ndarr(gfac,  'gfac')) # gfac shape:(3, 1, 512, 1024) size:1572864 dtype:float32 [0.02713277 0.02685284 0.02735394 0.02717916 0.02764508...]
    #print(info_ndarr(arrf,  'arrf')) # arrf shape:(1, 512, 1024) size:524288 dtype:float32 [ 6.7856445
    #print(info_ndarr(factor, 'factor')) # factor shape:(1, 512, 1024) size:524288 dtype:float32 [0.02713277 0.02685284
    #print(info_ndarr(offset, 'offset')) # offset shape:(1, 512, 1024) size:524288 dtype:float32 [0. 0. 0.
    #print(info_ndarr(mask, 'mask')) # mask shape:(1, 512, 1024) size:524288 dtype:uint8 [1 1 1 1 1...]
    #print(info_ndarr(resp, 'resp')) # resp shape:(1, 512, 1024) size:524288 dtype:float32 [0.18411334 0.12152617 0.08894039 0.11908797 0.5094565 ...]

    t14 = time()
    times = np.array((t00, t01, t02, t03, t04, t05, t06, t07, t08, t09, t10, t11, t12, t13, t14), dtype=np.float64)

    return resp, times








def calib_jungfrau_v2(det, evt, cmpars=(7,3,200,10), **kwa):
    """
    v2 - improving performance, reduce time and memory consumption, use peds-offset constants
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

    t00 = time()

    src = det.source # - src (psana.Source)   - Source object

    nda_raw = kwa.get('nda_raw', None)
    loop_segs = kwa.get('loop_segs', False)
    arr = det.raw(evt) if nda_raw is None else nda_raw # shape:(<npanels>, 512, 1024) dtype:uint16
    if arr is None: return None

    t01 = time()

    detname = string_from_source(det.source)

    t02 = time()

    #print('XXX type(detname):', type(detname))
    odc = cache.detcache_for_detname(detname)

    t03 = time()

    first_entry = odc is None
    if first_entry:
       odc = cache.add_detcache(det, evt)
       odc.cmps = det.common_mode(evt) if cmpars is None else cmpars
       odc.mask = det.mask_total(evt, **kwa)

    poff = odc.poff # 4d pedestals + offset shape:(3, 1, 512, 1024) dtype:float32
    gfac = odc.gfac # 4d gain factors evaluated form gains
    mask = odc.mask
    outa = odc.outa
    cmps = odc.cmps

    t04 = time()

    if first_entry:
        logger.info('\n  ====================== det.name: %s' % det.name\
                   +'\n  detname from source: %s' % string_from_source(det.source)\
                   +info_ndarr(arr,  '\n  calib_jungfrau arr ')\
                   +info_ndarr(poff, '\n  calib_jungfrau peds+off')\
                   +info_ndarr(gfac, '\n  calib_jungfrau gfac')\
                   +info_ndarr(mask, '\n  calib_jungfrau mask')\
                   +info_ndarr(outa, '\n  calib_jungfrau outa')\
                   +info_ndarr(cmps, '\n  calib_jungfrau common mode parameters ')
                   +'\n    loop over segments: %s' % loop_segs)

    if loop_segs:
      nsegs = arr.shape[0]
      shseg = arr.shape[-2:] # (512, 1024)
      for i in range(nsegs):
        arr1  = arr[i,:]
        mask1 = mask[i,:]
        gfac1 = gfac[:,i,:,:]
        poff1 = poff[:,i,:,:]
        arr1.shape  = (1,) + shseg
        mask1.shape = (1,) + shseg
        gfac1.shape = (3,1,) + shseg
        poff1.shape = (3,1,) + shseg
        #print(info_ndarr(arr1,  'XXX  arr1 '))
        #print(info_ndarr(poff1, 'XXX  poff1 '))
        out1, times = calib_jungfrau_single_panel(arr1, gfac1, poff1, mask1, cmps)
        #print(info_ndarr(out1, 'XXX  out1 '))
        outa[i,:] = out1[0,:]
      #print(info_ndarr(outa, 'XXX  outa '))
      #sys.exit('TEST EXIT')

      resp = outa

    else:
      resp, times = calib_jungfrau_single_panel(arr, gfac, poff, mask, cmps)

    t17 = time()
    times = (t00, t01, t02, t03, t04) + times + (t17,)
    return resp, np.array(times, dtype=np.float64)



def calib_jungfrau_single_panel(arr, gfac, poff, mask, cmps):
    """ Arrays should have a single panel shape, example for 8-panel detector:
    arr:  shape:(8, 512, 1024) size:4194304 dtype:uint16 [2906 2945 2813 2861 3093...]
    poff: shape:(3, 8, 512, 1024) size:12582912 dtype:float32 [2922.283 2938.098 2827.207 2855.296 3080.415...]
    gfac: shape:(3, 8, 512, 1024) size:12582912 dtype:float32 [0.02490437 0.02543429 0.02541406 0.02539831 0.02544083...]
    mask: shape:(8, 512, 1024) size:4194304 dtype:uint8 [1 1 1 1 1...]
    cmps: shape:(16,) size:16 dtype:float64 [  7.   1. 100.   0.   0....]
    """

    t05 = time()

    # Define bool arrays of ranges
    gr0 = arr <  BW1              # 490 us
    gr1 =(arr >= BW1) & (arr<BW2) # 714 us
    gr2 = arr >= BW3              # 400 us

    t06 = time()

    factor = np.select((gr0, gr1, gr2), (gfac[0,:], gfac[1,:], gfac[2,:]), default=1) # 2msec

    t07 = time()

    pedoff = np.select((gr0, gr1, gr2), (poff[0,:], poff[1,:], poff[2,:]), default=0)

    t08 = time()

    # Subtract offset-corrected pedestals
    arrf = np.array(arr & MSK, dtype=np.float32)

    t09 = time()

    arrf -= pedoff

    t10 = time()

    if cmps is not None:
      mode, cormax = int(cmps[1]), cmps[2]
      npixmin = cmps[3] if len(cmps)>3 else 10
      if mode>0:
        #arr1 = store.arr1
        #grhg = np.select((gr0,  gr1), (arr1, arr1), default=0)
        logger.debug(info_ndarr(gr0, 'gain group0'))
        logger.debug(info_ndarr(mask, 'mask'))
        t0_sec_cm = time()

        t11 = time()
        gmask = np.bitwise_and(gr0, mask) if mask is not None else gr0

        t12 = time()

        #sh = (nsegs, 512, 1024)
        hrows = 256 #512/2

        for s in range(arrf.shape[0]):

          t13 = time()

          if mode & 4: # in banks: (512/2,1024/16) = (256,64) pixels # 100 ms
            common_mode_2d_hsplit_nbanks(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], nbanks=16, cormax=cormax, npix_min=npixmin)
            common_mode_2d_hsplit_nbanks(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], nbanks=16, cormax=cormax, npix_min=npixmin)

          t14 = time()

          if mode & 1: # in rows per bank: 1024/16 = 64 pixels # 275 ms
            common_mode_rows_hsplit_nbanks(arrf[s,], mask=gmask[s,], nbanks=16, cormax=cormax, npix_min=npixmin)

          t15 = time()

          if mode & 2: # in cols per bank: 512/2 = 256 pixels  # 290 ms
            common_mode_cols(arrf[s,:hrows,:], mask=gmask[s,:hrows,:], cormax=cormax, npix_min=npixmin)
            common_mode_cols(arrf[s,hrows:,:], mask=gmask[s,hrows:,:], cormax=cormax, npix_min=npixmin)

        logger.debug('TIME: common-mode correction time = %.6f sec' % (time()-t0_sec_cm))

    t16 = time()

    arrf = arrf * factor if mask is None else arrf * factor * mask # gain correction

    return arrf, (t05, t06, t07, t08, t09, t10, t11, t12, t13, t14, t15, t16)









def calib_local(det, evt, cmpars=None, mbits=None, **kwargs):
    """local version of det.calib for jungfrau > calib_jungfrau"""
    kwargs['mbits']=mbits
    return calib_jungfrau(det, evt, cmpars=cmpars, **kwargs)


def calib_std(det, evt, cmpars=None, mbits=None, **kwargs):
    """det.calib for jungfrau"""
    kwargs['mbits']=mbits
    return uj.calib_jungfrau(det, evt, cmpars=cmpars, **kwargs)


def calib_v2(det, evt, cmpars=None, mbits=None, LOOP_SEGS=False, **kwargs):
    """NEW DWVELOPMEENT of det.calib for jungfrau"""
    kwargs['mbits']=mbits
    kwargs['loop_segs']=LOOP_SEGS
    return uj.calib_jungfrau_v2(det, evt, cmpars=cmpars, **kwargs)


def calib_local_v2(det, evt, cmpars=None, mbits=None, LOOP_SEGS=False, **kwargs):
    """local version of calib_jungfrau_v2"""
    kwargs['mbits']=mbits
    kwargs['loop_segs']=LOOP_SEGS
    return calib_jungfrau_v2(det, evt, cmpars, **kwargs)


def test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='1panel-v00', CALIBMET=CALIB_LOCAL, LOOP_SEGS=False):

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
    ntpoints = 15 if CALIBMET == CALIB_LOCAL else 18 # for CALIB_LOCAL_V2
    arrts = np.zeros((nevents,ntpoints), dtype=np.float64) if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2) else\
            np.zeros(nevents, dtype=np.float64)

    #ds = MPIDataSource('exp=cxix1000021:run=5') # 8-panel
    #det = Detector('jungfrau4M')

    #ds = MPIDataSource('exp=xcsx1003522:run=33') # single panel 72257 events
    #det = Detector('XcsEndstation.0:Jungfrau.1')

    ds = MPIDataSource('exp=cxilx7422:run=232') # 8-panel 31652 events
    det = Detector('CxiDs1.0:Jungfrau.0')
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

        if CALIBMET == CALIB_LOCAL:
            calib, times = calib_local(det, evt, cmpars=None)
            dt_sec = times[14] - times[0]
            arrts[nevt,:] = times
        elif CALIBMET == CALIB_STD:
            t0_sec = time()
            calib = calib_std(det, evt, cmpars=None)
            dt_sec = time()-t0_sec
            arrts[nevt] = dt_sec
        elif CALIBMET == CALIB_V2:
            t0_sec = time()
            calib = calib_v2(det, evt, cmpars=None, LOOP_SEGS=LOOP_SEGS)
            dt_sec = time()-t0_sec
            arrts[nevt] = dt_sec
        elif CALIBMET == CALIB_LOCAL_V2:
            calib, times = calib_local_v2(det, evt, cmpars=(7,7,200,10), LOOP_SEGS=LOOP_SEGS)
            dt_sec = times[14] - times[0]
            arrts[nevt,:] = times
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

    if True: # rank in ranks:
        amp_range=(0, 2.0)
        #dt = arrts[1:,14] - arrts[1:,0] if CALIBMET == CALIB_LOCAL else\
        dt = arrts[1:,14] - arrts[1:,0] if CALIBMET in (CALIB_LOCAL, CALIB_LOCAL_V2) else\
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

        if CALIBMET == CALIB_LOCAL_V2:
            plot_figs_v2(fnprefix, tit, arrts)

        if rank in ranks:
          if SAVE_FIGS:
            fnprefix1 = '%s-rank%02d-cpu%03d' % (fnprefix, rank, cpu_num)
            gr.save_fig(fhi, fname=fnprefix1+'-time.png')
            gr.save_fig(fpl, fname=fnprefix1+'-time-vs-evt.png')
            if rank == 0:
                fim, imsh, cbar = image(reshape_to_2d(calib), amin=None, amax=None)
                gr.save_fig(fim, fname=fnprefix1+'-image.png')

          if SHOW_FIGS:
            gr.show()


def plot_figs_v2(fnprefix, tit, arrts):
    print('plot_figs_v2\nfnprefix: %s title: %s' % (fnprefix, tit))
    arrts = arrts[1:,:] # exclude 1st event
    #for c in range(1,arrts.shape[1]):
    #  arrts[:,c] -= arrts[:,0] # subtract t0 for all columns but 0
    arrts[:,1:] -= arrts[:,0:-1] # evaluate dt for each step
    arrts[:,1:] *= 1000 # convert sec > msec
    print(info_ndarr(arrts, 'arrts[msec]:', last=100))
    fmt = 17*' %7.3f'
    for n,r in enumerate(range(arrts.shape[0])):
        times = arrts[r,:]
        print('%03d '%n, ('%14.3f' + fmt) % tuple(times))

    s = '     '.join(['t%02d'%i for i in range(1,arrts.shape[1])])
    print('evt  t00(sec)    ms: ', s)

    tmed = np.median(arrts[:,1:], axis=0)
    print('median:' + 12*' ' + (fmt % tuple(tmed)))

    for t in (1,6,7,8,9,10,12,13,14,15,16,17):
        dt = arrts[:,t]
        amp_range = (0,1000) if t==13 else (0,100) if t in (14,15,16) else (0,10)
        dtitle = 'dt%02d' % t
        _, _, _ = hist(dt, amp_range=amp_range, title=dtitle + ' ' + tit,\
                             xlabel='%s, msec' % dtitle, ylabel='dN/dt', titwin=dtitle + ' ' + tit + ' time per event')

def sort_records_in_file(fname):
    """ Parse and order records like
        hostname:sdfmilan216 rank:010 cpu:047 cmt:1p-v00 proc time (sec) mean: 0.0693 +/- 0.0041 rms: 0.0093 +/- 0.0029
    """
    print('\n\n\nsort_records_in_file: %s' % fname)
    s = load_textfile(fname)
    recs = sorted(s.split('\n'))
    print('records:')
    means = []
    for s in recs:
        fields = s.split()
        if len(fields)<8:  continue
        means.append(float(fields[8]))
    means = np.array(means)
    print(info_ndarr(means, 'means:', last=100))
    msg = 'mean time (sec): %0.4f' % means.mean()
    print(msg)

    s = '\n'.join(recs) + '\n%s' % msg
    print(s)
    save_textfile(s, fname.rstrip('.txt')+'-ordered.txt', mode='w')


def sort_records_in_files():
    for fname in (
            'fig-mpi-data-8p-v3-sdfmilan204-ncores01-summary.txt',
            'fig-mpi-data-8p-v3-sdfmilan204-ncores80-summary.txt',
            'fig-mpi-data-8p-v4-sdfmilan204-ncores01-summary.txt',
            'fig-mpi-data-8p-v4-sdfmilan204-ncores80-summary.txt',
            'fig-mpi-data-8p-v5-sdfmilan204-ncores01-summary.txt',
            'fig-mpi-data-8p-v5-sdfmilan204-ncores80-summary.txt',
        ):
        sort_records_in_file('figs/%s' % fname)


def selector(mode):
    if os.path.exists(FNAME_START_TIME):
        cmd = 'rm %s' % FNAME_START_TIME
        os.system(cmd)
        print('execute command:', sys.argv)
    #print('sys.argv:', sys.argv)
    #print('selector for mode: %s' % str(mode))
    #if mode >-1 and mode<128: do_algo(cpu=mode, cmt='v0' if len(sys.argv)<3 else sys.argv[2], SHOW_FIGS=False, SAVE_FIGS=False)
    if   mode == 0: test_mpi_for_random(SHOW_FIGS=False, SAVE_FIGS=True, cmt='v1.000')
    elif mode == 1: test_mpi_for_random(SHOW_FIGS=True, SAVE_FIGS=True, cmt='v4o1')
    elif mode == 2: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v2', CALIBMET=CALIB_LOCAL)
    elif mode == 3: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v3', CALIBMET=CALIB_STD)
    elif mode == 4: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v4', CALIBMET=CALIB_V2, LOOP_SEGS=False)
    elif mode == 5: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v5', CALIBMET=CALIB_V2, LOOP_SEGS=True)
    elif mode == 6: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v6', CALIBMET=CALIB_LOCAL_V2, LOOP_SEGS=False)
    elif mode == 7: test_mpi_for_data(SHOW_FIGS=True, SAVE_FIGS=True, cmt='8p-v7', CALIBMET=CALIB_LOCAL_V2, LOOP_SEGS=True)
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
