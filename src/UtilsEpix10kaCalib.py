# -*- coding: utf-8 -*-
"""
Created on Fri May 11 18:25:48 2018 
CALIBRATION - TEST PULSES

@author: blaj
"""
#--------------------
import os
import sys
from time import time
import logging
logger = logging.getLogger(__name__)
DICT_NAME_TO_LEVEL = {k:v for k,v in logging._levelNames.iteritems() if isinstance(k, str)}

from time import sleep
from psana import DataSource, Detector
import numpy as np

from PSCalib.DCUtils import env_time, dataset_time, str_tstamp
from Detector.UtilsEpix import id_epix, CALIB_REPO_EPIX10KA, FNAME_PANEL_ID_ALIASES,\
                               alias_for_id, create_directory, set_file_access_mode
from Detector.UtilsEpix10ka import store, GAIN_MODES, GAIN_MODES_IN, config_objects,\
                            get_epix10ka_any_config_object, find_gain_mode

from Detector.UtilsEpix10ka2M import ids_epix10ka2m, print_object_dir # id_epix10ka, print_object_dir

from PSCalib.GlobalUtils import log_rec_on_start, deploy_file, save_textfile,\
                         EPIX10KA2M, EPIX10KAQUAD, EPIX10KA, dic_det_type_to_calib_group # str_tstamp, replace
from Detector.GlobalUtils import info_ndarr, print_ndarr, divide_protected

import matplotlib.pyplot as plt

# supress matplotlib deprication warnings
#import warnings
#warnings.filterwarnings("ignore",".*GUI is implemented.*")

#--------------------

M14 = 0x3fff # 16383 or (1<<14)-1 - 14-bit mask
#B14 = 0x4000 # 16384 or (1<<14)   - 14-bit (15-th bit starting from 1)
B14 = 040000 # 16384 or 1<<14 (15-th bit starting from 1)
#--------------------

def plot_avsi_figaxis():
    if not hasattr(store, 'plot_avsi_figax'):
        fig=plt.figure(101,facecolor='w')
        fig.clf()
        ax=fig.add_subplot(111)
        store.plot_avsi_figax=fig,ax
    return store.plot_avsi_figax

def plot_avsi(x,y,fname):
    fig, ax = plot_avsi_figaxis()
    gbit = np.bitwise_and(y, B14) /8
    #gbit = 2048*(y & B14)
    #line0.set_ydata(y & M14) # (trace%16384)
    #line1.set_ydata(gbit)
    ax.cla()
    ax.set_ylim(0,16384)
    ax.set_yticks(np.arange(0,16385,2048))
    line0,=ax.plot(x,y & M14,'b-',linewidth=1)
    line1,=ax.plot(x,gbit,'r-',linewidth=1)
    #line1.set_ydata(np.polyval(pf0,xx))
    #line2.set_ydata(np.polyval(pf1,xx))
    ax.set_title(fname.rstrip('.png'), fontsize=10)#, color=color, fontsize=fstit, **kwargs)
    fig.canvas.set_window_title(fname)

    fig.canvas.manager.window.move(650,200)
    plt.plot()
    plt.pause(3)
    plt.savefig(fname)
    print 'saved file %s' % fname
    #plt.ioff()
    plt.show()    
    #plt.ion()

#--------------------

def plot_data_block(block, evnum, prefix):
    ts = str_tstamp(fmt='%Y%m%dT%H%M%S', time_sec=time())
    mf,my,mx=block.shape
    print 'block shape:',mf,my,mx
    trace=block[:,0,0]
    x = np.arange(mf)
    print_ndarr(x,'x')
    print_ndarr(trace,'trace')

    for iy in range(my):
        for ix in range(mx):
            selected = (iy*mx+ix)%256==255

            if selected:  #display a subset of plots

                trace=block[:,iy,ix]
                logger.debug('==== saw_edge for %s-proc-ix%02d-iy%02d:' % (prefix, ix, iy))
                for ixb, ixs, ixe in saw_edges(trace, evnum, do_debug=True):
                    print '  saw edges:', ixb, ixs, ixe, 'period:', ixe-ixb+1

                fname = '%s-dat-ix%02d-iy%02d.png' % (prefix, ix, iy)
                plot_avsi(x,trace,fname)

    #sys.exit('TEST EXIT')

#--------------------

def saw_edges(trace, evnums, gap=50, do_debug=True):
    """ Returns list of triplet indexes [(ibegin, iswitch, iend), ...]
        in the arrays trace and evnums for found full periods of the charge injection pulser.
    """
    traceB14 = trace & B14 # np.bitwise_and(trace, B14)
    indsB14 = np.nonzero(traceB14)[0] # index [0] selects dimension in tuple
    evnumsB14 = evnums[indsB14]
    ixoff = np.compress(np.diff(evnumsB14)>gap, indsB14[:-1], axis=0) + 1 # compress, because np.where keeps zeroes

    if do_debug:
        logger.debug(info_ndarr(trace, 'trace', last=10))
        logger.debug(info_ndarr(traceB14, 'trace & B14', last=10))
        logger.debug(info_ndarr(indsB14, 'indsB14'))
        logger.debug(info_ndarr(evnumsB14, 'evnumsB14'))
        logger.debug(info_ndarr(ixoff, 'ixoff', last=15))

    edges = [(ixb, ixb + np.nonzero(traceB14[ixb:ixe])[0][0], ixe) for ixb,ixe in zip(ixoff[:-1],ixoff[1:]-1) if any(traceB14[ixb:ixe])]

    #try:
    #  edges = [(ixb, ixb + np.nonzero(traceB14[ixb:ixe])[0][0], ixe) for ixb,ixe in zip(ixoff[:-1],ixoff[1:]-1)]
    #except IndexError:
    #  msg='IndexError:\n  %s\n  %s\n  compressed: %s\n  %s\n  %s\n  %s' % (
    #       info_ndarr(trace, 'trace', last=10),
    #       info_ndarr(traceB14, 'trace & B14', last=10),
    #       info_ndarr(np.compress(traceB14>0,traceB14), 'compressed trace', last=10),
    #       info_ndarr(indsB14, 'indsB14'),
    #       info_ndarr(evnumsB14, 'evnumsB14'),
    #       info_ndarr(ixoff, 'ixoff', last=15))
    #  logger.warning(msg)
    #
    #  for ixb,ixe in zip(ixoff[:-1],ixoff[1:]-1):
    #      #print('ixb,ixe: ',ixb,ixe,' np.nonzero(traceB14[ixb:ixe])', np.nonzero(traceB14[ixb:ixe]))
    #      print('ixb,ixe: ',ixb,ixe,' traceB14[ixb:ixe]', traceB14[ixb:ixe])
    #  sys.exit('IndexError')

    return edges

#--------------------

def plot_fit_figaxis():
    if not hasattr(store, 'plot_fit_figax'):
        fig=plt.figure(100,facecolor='w')
        ax=fig.add_subplot(111)
        store.plot_fit_figax = fig, ax
    return store.plot_fit_figax

#--------------------

def plot_fit(x,y,pf0,pf1,fname):
    print 'plot_fit %s' % fname
    fig, ax = plot_fit_figaxis()

    #fig.clf()
    ax.cla()
    ax.set_xlim(0,1100)
    ax.set_ylim(0,16384)
    ax.set_xticks(np.arange(0,1100,200))
    ax.set_yticks(np.arange(0,16385,2048))

    ax.plot(x,y,'ko',markersize=1)
    ax.plot(x,np.polyval(pf0,x),'b-',linewidth=1)
    ax.plot(x,np.polyval(pf1,x),'r-',linewidth=1)

    ax.set_title(fname.rstrip('.png'), fontsize=10)#, color=color, fontsize=fstit, **kwargs)
    fig.canvas.set_window_title(fname)
    fig.canvas.manager.window.move(0,0)
    plt.plot()
    plt.pause(3)
    plt.savefig(fname)
    print 'saved file %s' % fname
    #plt.ioff()
    plt.show()    
    #plt.ion()

#--------------------

def figure(figsize=(9,8), title='Image', dpi=80, facecolor='w', edgecolor='w', frameon=True, move=None, **kwargs):
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor, edgecolor=edgecolor, frameon=frameon, **kwargs)
    fig.canvas.set_window_title(title, **kwargs)
    if move is not None:
        fig.canvas.manager.window.move(move[0], move[1])
    return fig

#--------------------

def fig_img_cbar_axes(fig=None,\
                      win_axim=(0.05,  0.05, 0.87, 0.92),\
                      win_axcb=(0.923, 0.05, 0.02, 0.92), **kwargs):
    _fig = figure(move=(650,0)) if fig is None else fig
    axim = _fig.add_axes(win_axim, **kwargs)
    axcb = _fig.add_axes(win_axcb, **kwargs)
    return _fig, axim, axcb

#--------------------

def imshow_cbar(fig, axim, axcb, img, amin=None, amax=None, extent=None,\
                interpolation='nearest', aspect='auto', origin='upper',\
                orientation='vertical', cmap='inferno', **kwargs):
    axim.cla()
    if img is None: return
    imsh = axim.imshow(img, interpolation=interpolation, aspect=aspect, origin=origin, extent=extent, cmap=cmap, **kwargs)
    axim.autoscale(False)
    ave = np.mean(img) if amin is None and amax is None else None
    rms = np.std(img)  if amin is None and amax is None else None
    cmin = amin if amin is not None else ave-1*rms if ave is not None else None
    cmax = amax if amax is not None else ave+3*rms if ave is not None else None
    if cmin is not None: imsh.set_clim(cmin, cmax)
    cbar = fig.colorbar(imsh, cax=axcb, orientation=orientation, **kwargs)

    plt.draw()
    plt.pause(0.01)
    plt.show()

    return imsh, cbar

#--------------------
#--------------------
#--------------------
# 2020-06 development

def fit(block, evnum, display=True, prefix='fig-fit', ixoff=10, nperiods=False):

    mf,my,mx=block.shape
    fits=np.zeros((my,mx,2,2))
    nsp=np.zeros((my,mx),dtype=np.int16)
    msg = ' fit '

    logger.debug(info_ndarr(evnum, 'in fit evnum:'))
    logger.debug(info_ndarr(block, 'in fit block:'))
    #ts = str_tstamp(fmt='%Y%m%dT%H%M%S', time_sec=time())

    if display:
        plot_data_block(block, evnum, prefix)

    for iy in range(my):
        for ix in range(mx):
            selected = (iy*mx+ix)%256==255

            trace=block[:,iy,ix]

            edges = saw_edges(trace, evnum, do_debug=(logger.level==logging.DEBUG))
            if len(edges)==0:
                 logger.warning('pulser saw edges are not found, skip processing for ix%02d-iy%02d:' % (ix,iy))
                 continue

            ixb, ixs, ixe = edges[0]
            nsp[iy,ix]=ixs
            tracem = trace & M14

            x0 =  evnum[ixb:ixs-ixoff]-evnum[ixb]
            y0 = tracem[ixb:ixs-ixoff]
            x1 =  evnum[ixs+ixoff:ixe]-evnum[ixb]
            y1 = tracem[ixs+ixoff:ixe]           
            
            if nperiods:
               for ixb,ixs,ixe in edges[1:]:
                 x0 = np.hstack((x0,  evnum[ixb:ixs-ixoff]-evnum[ixb]))
                 y0 = np.hstack((y0, tracem[ixb:ixs-ixoff]))
                 x1 = np.hstack((x1,  evnum[ixs+ixoff:ixe]-evnum[ixb]))
                 y1 = np.hstack((y1, tracem[ixs+ixoff:ixe]))
                 
            pf0=np.polyfit(x0,y0,1)
            pf1=np.polyfit(x1,y1,1)

            fits[iy,ix,0]=pf0
            fits[iy,ix,1]=pf1
            
            if selected: # for selected ix, iy
                s = '==== ix%02d-iy%02d:' % (ix, iy)
                for ixb, ixs, ixe in edges:
                    s += '\n  saw edges begin: %4d switch: %4d end: %4d period: %4d' % (ixb, ixs, ixe, ixe-ixb+1)
                    s += info_ndarr(tracem, '\n    tracem', last=10)
                    s += info_ndarr(x0,     '\n    x0', last=10)  
                    s += info_ndarr(y0,     '\n    y0', last=10)
                    s += info_ndarr(x1,     '\n    x1', last=10)
                    s += info_ndarr(y1,     '\n    y1', last=10)
                    s += info_ndarr(pf0,    '\n    pf0', last=10)
                    s += info_ndarr(pf1,    '\n    pf1', last=10)
                logger.debug(s)

                msg+='.'
                if display:
                    fname = '%s-ix%02d-iy%02d.png' % (prefix, ix, iy)
                    x = np.hstack((x0,x1))
                    y = np.hstack((y0,y1))
                    logger.debug(info_ndarr(x,'\n    x')\
                               + info_ndarr(y,'\n    y'))
                    plot_fit(x,y,pf0,pf1,fname)

    return fits,nsp,msg

#--------------------
#--------------------
#--------------------
#--------------------

def fit_old(block, evnum, itrim, display=True, prefix='fig-fit', period=1024):
#def fit(block, evnum, itrim, display=True, prefix='fig-fit', period=1024):

    mf,my,mx=block.shape
    fits=np.zeros((my,mx,2,2))
    nsp=np.zeros((my,mx),dtype=np.int16)
    nsaw = 1
    x=np.arange(nsaw*period)%period
    #x=evnum%period
    xx=np.linspace(period,0,100)
    msg = ' fit '

    logger.info(info_ndarr(evnum, 'in fit evnum:'))
    logger.info(info_ndarr(block, 'in fit block:'))
    #ts = str_tstamp(fmt='%Y%m%dT%H%M%S', time_sec=time())

    if display:
        plot_data_block(block, evnum, prefix)

    for iy in range(my):
        for ix in range(mx):
            selected = (iy*mx+ix)%256==255

            trace=block[:,iy,ix]

            ixoff=np.argmin(np.diff(trace[:period+1],axis=0),axis=0)+1 #find pulser value 0

            trace=trace[ixoff:ixoff+nsaw*period]
            tracem = trace & M14
            #x = x[ixoff:ixoff+nsaw*period] # NEW

            isp = period
            try:
                isp=int(np.median(np.where(np.diff(trace)>1000)[0]%period))  #estimate median position of switching point
                nsp[iy,ix]=isp
            except ValueError:
                testval=np.median(tracem) # %16384
                ixoff=period if testval<0.5 else 0

            idx0=x<isp-50; idx1=x>isp+50                           #select data to the left and right of switching point

            if idx0.sum()>10:
                pf0=np.polyfit(x[idx0],tracem[idx0],1) # %16384    #fit high/medium gain trace
            else:
                pf0=np.array([0,0])                                #or set to 0 if not enough data points
            if idx1.sum()>10:
                #pf1=np.polyfit(x[idx1],trace[idx1]%16384,1)       #this doesn't work!
                gl=pf0[0]/(100.0 if itrim else 33.33)              #Medium to Low
                ol=np.mean(tracem[idx1]-gl*x[idx1]) # %16384       #calculate offset
                pf1=np.array([gl,ol])
            else:
                pf1=np.array([0,0])                                #ore st to zero if not enough data points
            fits[iy,ix,0]=pf0
            fits[iy,ix,1]=pf1
            
            if selected:  #display a subset of plots
                #print '\b.',
                print '==== ix%02d-iy%02d:' % (ix, iy)
                print '  ixoff:', ixoff
                print '  isp  :', isp
                print_ndarr(idx0,  '    idx0') #idx0: [ True  True  True ..., False False False]
                print_ndarr(idx1,  '    idx1') #idx1: [False False False ...,  True  True  True]
                print_ndarr(x,     '    x')
                print_ndarr(tracem,'    tracem')

                msg+='.'
                if display:
                    #if store.handle is None: store.handle=init_plot(x,xx,itrim)
                    #fname = 'fig-fit-%s-ix%02d-iy%02d.png' % (ts, ix, iy)
                    fname = '%s-ix%02d-iy%02d.png' % (prefix, ix, iy)
                    #update_plot(store.handle,trace,xx,pf0,pf1,fname)
                    plot_fit(xx,trace,pf0,pf1,fname)

    #fits[iy,ix,1,1] -= fits[iy,ix,0,1] # offset

    return fits,nsp,msg

#--------------------
#--------------------
#--------------------
#--------------------

def find_file_for_timestamp(dirname, pattern, tstamp):
    # list of file names in directory, dirname, containing pattern
    fnames = [name for name in os.listdir(dirname) if pattern in name]

    # list of int tstamps 
    # !!! here we assume specific name structure generated by file_name_prefix
    itstamps = [int(name.split('_',3)[2]) for name in fnames]

    # reverse-sort int timestamps in the list
    itstamps.sort(key=int,reverse=True)

    # find the nearest to requested timestamp
    for its in itstamps:
        if its <= int(tstamp):
            # find and return the full file name for selected timestamp
            ts = str(its)

            for name in fnames:
                if ts in name: 
                     fname = '%s/%s' % (dirname, name)
                     logger.info('  selected %s for %s and %s' % (os.path.basename(fname),pattern,tstamp))
                     return fname

    logger.warning('directory %s\n         DOES NOT CONTAIN file for pattern %s and timestamp <= %s'%\
                   (dirname,pattern,tstamp))
    return None

#--------------------

#def shape_from_config(det):
#    """DEPRICATED single-panel version
#    """
#    c = get_epix10ka_config_object(det.env, det.source)
#    shape = (c.numberOfRows(), c.numberOfColumns())
#    #logger.debug('shape_from_config: %s' % str(shape))
#    return shape

#--------------------

def shape_from_config_epix10ka(eco):
    """Returns element/panel/sensor shape (352,384) from element configuration object
       psana.Epix.Config10ka or psana.Epix.Config10kaV1
    """
    #print_object_dir(eco)
    return (eco.numberOfRows(), eco.numberOfColumns())

#--------------------

def print_config_info(c):
    """Prints config infor for single panel objectpsana.Epix.Config10kaV1
    """
    if c is not None:
        nasics = c.numberOfAsics()
        msg = 'Config object info:'\
            + ('\n       rows: %d, cols: %d, asics: %d' % (c.numberOfRows(), c.numberOfColumns(), c.numberOfAsics()))\
            + ('\n       version: %d, asicMask: %d' % (c.version(), c.asicMask()))\
            + ('\n       digitalCardId0: %d, 1: %d' % (c.carrierId0(), c.carrierId1()))\
            + ('\n       digitalCardId0: %d, 1: %d' % (c.digitalCardId0(), c.digitalCardId1()))\
            + ('\n       analogCardId0 : %d, 1: %d' % (c.analogCardId0(),  c.analogCardId1()))\
            + ('\n       numberOfAsics        : %d' % nasics)\
            + ('\n       asic trbits          : %s' % str([c.asics(i).trbit() for i in range(nasics)]))
        logger.debug(msg)

#--------------------

def get_panel_id(panel_ids, idx=0):
    panel_id = panel_ids[idx] if panel_ids is not None else None
    if panel_id is None:
        logger.error('get_panel_id: panel_idis None, idx=%d' % idx)
        sys.exit('ERROR EXIT')
    return panel_id

#--------------------
#--------------------
#--------------------
#--------------------

def mean_constrained(arr, lo, hi):
    """Evaluates mean value of the input array for values between low and high limits
    """
    condlist = (np.logical_not(np.logical_or(arr<lo, arr>hi)),)
    arr1 = np.ones(arr.shape, dtype=np.int32)
    arr_of1 = np.select(condlist, (arr1,), 0)
    arr_ofv = np.select(condlist, (arr,), 0)
    ngood = arr_of1.sum()
    return arr_ofv.sum()/ngood if ngood else None

#--------------------

def evaluate_limits(arr, nneg=5, npos=5, lim_lo=1, lim_hi=16000, cmt=''):
    """Evaluates low and high limit of the array, which are used to find bad pixels.
    """
    ave, std = (arr.mean(), arr.std()) if (nneg>0 or npos>0) else (None,None)
    lo = ave-nneg*std if nneg>0 else lim_lo
    hi = ave+npos*std if npos>0 else lim_hi
    lo, hi = max(lo, lim_lo), min(hi, lim_hi)

    logger.debug('  %s: %s ave, std = %.3f, %.3f  low, high limits = %.3f, %.3f'%\
                 (sys._getframe().f_code.co_name, cmt, ave, std, lo, hi))

    return lo, hi

#--------------------

def proc_dark_block(block, **opts):
    """Returns per-panel (352, 384) arrays of mean, rms, ...
       block.shape = (nrecs, 352, 384), where nrecs <= 1024
    """
    exp        = opts.get('exp', None)
    detname    = opts.get('det', None)

    int_lo     = opts.get('int_lo', 1)       # lowest  intensity accepted for dark evaluation
    int_hi     = opts.get('int_hi', 16000)   # highest intensity accepted for dark evaluation
    intnlo     = opts.get('intnlo', 6.0)     # intensity ditribution number-of-sigmas low
    intnhi     = opts.get('intnhi', 6.0)     # intensity ditribution number-of-sigmas high
                                 
    rms_lo     = opts.get('rms_lo', 0.001)   # rms ditribution low
    rms_hi     = opts.get('rms_hi', 16000)   # rms ditribution high
    rmsnlo     = opts.get('rmsnlo', 6.0)     # rms ditribution number-of-sigmas low
    rmsnhi     = opts.get('rmsnhi', 6.0)     # rms ditribution number-of-sigmas high

    fraclm     = opts.get('fraclm', 0.1)     # allowed fraction limit
    nsigma     = opts.get('nsigma', 6.0)     # number of sigmas for gated eveluation

    blockdbl = np.array(block, dtype=np.double)

    logger.debug('in proc_dark_block for exp=%s det=%s, block.shape=%s' % (exp, detname, str(block.shape)))
    nrecs, ny, nx = block.shape
    shape = (ny, nx)

    arr0       = np.zeros(shape, dtype=np.int64)
    arr1       = np.ones (shape, dtype=np.int64)

    arr_sum0   = np.zeros(shape, dtype=np.int64)
    arr_sum1   = np.zeros(shape, dtype=np.double)
    arr_sum2   = np.zeros(shape, dtype=np.double)

    gate_lo    = arr1 * int_lo
    gate_hi    = arr1 * int_hi

    t0_sec = time()

    # 1st loop over recs(non-empty events) in block
    for nrec in range(min(nrecs,500)):
        raw    = block[nrec,:]
        rawdbl = blockdbl[nrec,:]

        cond_lo = raw<gate_lo
        cond_hi = raw>gate_hi
        condlist = (np.logical_not(np.logical_or(cond_lo, cond_hi)),)

        arr_sum0 += np.select(condlist, (arr1,), 0)
        arr_sum1 += np.select(condlist, (rawdbl,), 0)
        arr_sum2 += np.select(condlist, (np.square(rawdbl),), 0)

    arr_av1 = divide_protected(arr_sum1, arr_sum0)
    arr_av2 = divide_protected(arr_sum2, arr_sum0)

    arr_rms = np.sqrt(arr_av2 - np.square(arr_av1))

    #rms_ave = arr_rms.mean()
    rms_ave = mean_constrained(arr_rms, rms_lo, rms_hi)

    logger.debug(info_ndarr(arr_av1, '1st loop proc time = %.3f sec arr_av1' % (time()-t0_sec)))
    gate_half = nsigma*rms_ave
    logger.debug('set gate_half=%.3f for intensity gated average, which is %.3f * sigma' % (gate_half,nsigma))

    # 2nd loop over recs in block to evaluate gated parameters

    sta_int_lo = np.zeros(shape, dtype=np.int64)
    sta_int_hi = np.zeros(shape, dtype=np.int64)

    arr_max = np.zeros(shape, dtype=block.dtype)
    arr_min = np.ones (shape, dtype=block.dtype) * 0x3ffff

    gate_hi = np.minimum(arr_av1 + gate_half, gate_hi).astype(dtype=raw.dtype)
    gate_lo = np.maximum(arr_av1 - gate_half, gate_lo).astype(dtype=raw.dtype)

    arr_sum0 = np.zeros(shape, dtype=np.int64)
    arr_sum1 = np.zeros(shape, dtype=np.double)
    arr_sum2 = np.zeros(shape, dtype=np.double)

    for nrec in range(nrecs):
        raw    = block[nrec,:]
        rawdbl = blockdbl[nrec,:]

        cond_lo = raw<gate_lo
        cond_hi = raw>gate_hi
        condlist = (np.logical_not(np.logical_or(cond_lo, cond_hi)),)

        arr_sum0 += np.select(condlist, (arr1,), 0)
        arr_sum1 += np.select(condlist, (rawdbl,), 0)
        arr_sum2 += np.select(condlist, (np.square(rawdbl),), 0)

        sta_int_lo += np.select((raw<int_lo,), (arr1,), 0)
        sta_int_hi += np.select((raw>int_hi,), (arr1,), 0)

        arr_max = np.maximum(arr_max, raw)
        arr_min = np.minimum(arr_min, raw)

    arr_av1 = divide_protected(arr_sum1, arr_sum0)
    arr_av2 = divide_protected(arr_sum2, arr_sum0)

    frac_int_lo = np.array(sta_int_lo/nrecs, dtype=np.float32)
    frac_int_hi = np.array(sta_int_hi/nrecs, dtype=np.float32)

    arr_rms = np.sqrt(arr_av2 - np.square(arr_av1))
    #rms_ave = arr_rms.mean()
    rms_ave = mean_constrained(arr_rms, rms_lo, rms_hi)
 
    rms_min, rms_max = evaluate_limits(arr_rms, rmsnlo, rmsnhi, rms_lo, rms_hi, cmt='RMS')
    ave_min, ave_max = evaluate_limits(arr_av1, intnlo, intnhi, int_lo, int_hi, cmt='AVE')

    arr_sta_rms_hi = np.select((arr_rms>rms_max,),    (arr1,), 0)
    arr_sta_rms_lo = np.select((arr_rms<rms_min,),    (arr1,), 0)
    arr_sta_int_hi = np.select((frac_int_hi>fraclm,), (arr1,), 0)
    arr_sta_int_lo = np.select((frac_int_lo>fraclm,), (arr1,), 0)
    arr_sta_ave_hi = np.select((arr_av1>ave_max,),    (arr1,), 0)
    arr_sta_ave_lo = np.select((arr_av1<ave_min,),    (arr1,), 0)

    logger.info ('Bad pixel status:'\
                +'\n  status  1: %8d pixel rms       > %.3f' % (arr_sta_rms_hi.sum(), rms_max)\
                +'\n  status  8: %8d pixel rms       < %.3f' % (arr_sta_rms_lo.sum(), rms_min)\
                +'\n  status  2: %8d pixel intensity > %g in more than %g fraction of events' % (arr_sta_int_hi.sum(), int_hi, fraclm)\
                +'\n  status  4: %8d pixel intensity < %g in more than %g fraction of events' % (arr_sta_int_lo.sum(), int_lo, fraclm)\
                +'\n  status 16: %8d pixel average   > %g'   % (arr_sta_ave_hi.sum(), ave_max)\
                +'\n  status 32: %8d pixel average   < %g'   % (arr_sta_ave_lo.sum(), ave_min)\
                )

    #0/1/2/4/8/16/32 for good/hot-rms/saturated/cold/cold-rms/average above limit/average below limit, 
    arr_sta = np.zeros(shape, dtype=np.int64)
    arr_sta += arr_sta_rms_hi    # hot rms
    arr_sta += arr_sta_rms_lo*8  # cold rms
    arr_sta += arr_sta_int_hi*2  # satturated
    arr_sta += arr_sta_int_lo*4  # cold
    arr_sta += arr_sta_ave_hi*16 # too large average
    arr_sta += arr_sta_ave_lo*32 # too small average
    
    #arr_msk  = np.select((arr_sta>0,), (arr0,), 1)

    logger.debug(info_ndarr(arr_av1, 'proc time = %.3f sec arr_av1' % (time()-t0_sec)))
    logger.debug(info_ndarr(arr_rms, 'pixel_rms'))
    logger.debug(info_ndarr(arr_sta, 'pixel_status'))

    #return block.mean(0)
    return arr_av1, arr_rms, arr_sta

#--------------------
#--------------------
#--------------------
#--------------------
#--------------------

def tstamps_run_and_now(env):
    """Returns tstamp_run, tstamp_now
    """
    time_run = env_time(env)
    ts_run = str_tstamp(fmt='%Y%m%d%H%M%S', time_sec=time_run)
    ts_now = str_tstamp(fmt='%Y%m%d%H%M%S', time_sec=None)

    logger.debug('tstamps_run_and_now:'
                 + ('\n  run time stamp      : %s' % ts_run)\
                 + ('\n  current time stamp  : %s' % ts_now))
    return ts_run, ts_now
#--------------------

def tstamp_for_dataset(dsname):
    """Returns tstamp_run for dataset dsname, e.g. "exp=xcsx35617:run=6".
    """
    tsec = dataset_time(dsname)
    return str_tstamp(fmt='%Y%m%d%H%M%S', time_sec=tsec)

#--------------------

def ids_epix10ka_any_for_dataset_detname(dsname, detname):
    ds = DataSource(dsname)
    det = Detector(detname)
    env = ds.env()
    co = get_epix10ka_any_config_object(env, det.source)
    return ids_epix10ka2m(co)

#--------------------

def get_config_info_for_dataset_detname(dsname, detname, idx=0):
    ds = DataSource(dsname)
    det = Detector(detname)
    env = ds.env()
    dco,qco,eco = config_objects(env, det.source, idx)
    co = next(o for o in (dco,qco,eco) if o is not None)

    #print_object_dir(dco)
    #print('dco', dco)
    #print('qco', qco)
    #print('eco', eco)
    logger.debug('Top config. object: %s' % str(co))

    cpdic = {}
    cpdic['expnum'] = env.expNum()
    cpdic['calibdir'] = env.calibDir()
    cpdic['strsrc'] = det.pyda.str_src
    cpdic['shape'] = shape_from_config_epix10ka(eco)
    cpdic['gain_mode'] = find_gain_mode(det, data=None) #data=raw: distinguish 5-modes w/o data
    cpdic['panel_ids'] = ids_epix10ka2m(co)
    cpdic['dettype'] = det.dettype
    for nevt,evt in enumerate(ds.events()):
        raw = det.raw(evt)
        if raw is not None: 
            tstamp, tstamp_now = tstamps_run_and_now(env)
            cpdic['tstamp'] = tstamp
            del ds
            del det
            break
    logger.info('configuration info for %s %s segment=%d:\n%s' % (dsname, detname, idx, str(cpdic)))
    return cpdic

#--------------------

def save_log_record_on_start(dirrepo, fname, fac_mode=0o777):
    """Adds record on start to the log file <dirlog>/logs/log-<fname>-<year>.txt
    """
    rec = log_rec_on_start()
    year = str_tstamp(fmt='%Y')
    create_directory(dirrepo, fac_mode)
    dirlog = '%s/logs' % dirrepo
    create_directory(dirlog, fac_mode)
    logfname = '%s/log_%s_%s.txt' % (dirlog, fname, year)

    fexists = os.path.exists(logfname)
    save_textfile(rec, logfname, mode='a')
    if not fexists: set_file_access_mode(logfname, fac_mode)

    logger.debug('Record on start: %s' % rec)
    logger.info('Saved:  %s' % logfname)

#--------------------

def dir_names(dirrepo, panel_id):
    """Defines structure of subdirectories in calibration repository.
    """
    dir_panel  = '%s/%s' % (dirrepo, panel_id)
    dir_offset = '%s/offset'    % dir_panel
    dir_peds   = '%s/pedestals' % dir_panel
    dir_plots  = '%s/plots'     % dir_panel
    dir_work   = '%s/work'      % dir_panel
    dir_gain   = '%s/gain'      % dir_panel
    dir_rms    = '%s/rms'       % dir_panel
    dir_status = '%s/status'    % dir_panel
    return dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain, dir_rms, dir_status

#--------------------

def dir_merge(dirrepo):
    return '%s/merge_tmp' % dirrepo

#--------------------

def fname_prefix_merge(dmerge, detname, tstamp, exp, irun):
    return '%s/%s-%s-%s-r%04d' % (dmerge, detname, tstamp, exp, irun)

#--------------------

def file_name_prefix(panel_id, tstamp, exp, irun):
    panel_alias = alias_for_id(panel_id, fname=FNAME_PANEL_ID_ALIASES)
    return 'epix10ka_%s_%s_%s_r%04d' % (panel_alias, tstamp, exp, irun), panel_alias

#--------------------

def file_name_npz(dir_work, fname_prefix, expnum, nspace):
    return '%s/%s_sp%02d_df.npz' % (dir_work, fname_prefix, nspace)

#--------------------

def path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain, dir_rms, dir_status):
    prefix_offset= '%s/%s' % (dir_offset, fname_prefix)
    prefix_peds  = '%s/%s' % (dir_peds,   fname_prefix)
    prefix_plots = '%s/%s' % (dir_plots,  fname_prefix)
    prefix_gain  = '%s/%s' % (dir_gain,   fname_prefix)
    prefix_rms   = '%s/%s' % (dir_rms,    fname_prefix)
    prefix_status= '%s/%s' % (dir_status, fname_prefix)
    return prefix_offset, prefix_peds, prefix_plots, prefix_gain, prefix_rms, prefix_status

#--------------------

def calib_group(dettype):
    """Returns subdirecrory name under calib/<subdir>/... for 
       dettype, which is one of EPIX10KA2M, EPIX10KAQUAD, EPIX10KA, 
       i.g. 'Epix10ka::CalibV1'
    """
    return dic_det_type_to_calib_group.get(dettype, None)

#--------------------

def selected_record(nrec):
    return nrec<5\
       or (nrec<50 and not nrec%10)\
       or (nrec<500 and not nrec%100)\
       or (not nrec%1000)

#--------------------

def save_ndarray_in_textfile(nda, fname, fmode, fmt):
    fexists = os.path.exists(fname)
    save_txt(fname, nda, fmt=fmt)
    if not fexists: set_file_access_mode(fname, fmode)
    logger.debug('saved: %s' % fname)

#--------------------

def save_2darray_in_textfile(nda, fname, fmode, fmt):
    fexists = os.path.exists(fname)
    np.savetxt(fname, nda, fmt=fmt)
    if not fexists: set_file_access_mode(fname, fmode)
    logger.info('saved:  %s' % fname)
        
#--------------------

def print_statistics(nevt, nrec):
    logger.debug('statistics nevt:%d nrec:%d lost frames:%d' % (nevt, nrec, nevt-nrec))
         
#--------------------
"""           
name: Epix10ka2M offset scan pvl.value: dark Fixed High Gain
name: Epix10ka2M offset scan pvl.value: dark Fixed Medium Gain
name: Epix10ka2M offset scan pvl.value: dark Fixed Low Gain
name: Epix10ka2M offset scan pvl.value: dark Auto High to Low
name: Epix10ka2M offset scan pvl.value: dark Auto Medium to Low
name: Epix10ka2M offset scan pvl.value: position 0 trbit 0
"""

CALIBCYCLE_NAMES_DARK = [\
    'dark Fixed High Gain',\
    'dark Fixed Medium Gain',\
    'dark Fixed Low Gain',\
    'dark Auto High to Low',\
    'dark Auto Medium to Low',\
]

def calibcycle_names(nspace=7):
  if not hasattr(store, 'cc_names'):
    store.cc_names = list(CALIBCYCLE_NAMES_DARK)
    for trbit in range(2):
      for pos in range(nspace*nspace):
        v = 'position %d trbit %d' % (pos, trbit)
        store.cc_names.append(v)
    s = [v for v in store.cc_names]
    logger.debug('Expected list of calib-cycles:\n%s' % '\n'.join(s))    
  return store.cc_names

#--------------------

def step_counter(cd, nstep_tot, nstep_run, nspace=None): #nspace=7 - for 103 charge injection calib-cycles, =None for 5 dark
    pvl = cd().pvLabels()
    if len(pvl)==0:
        logger.warning('CALIB-CYCLE METADATA IS NOT AVAILABLE nstep_tot:%d, nstep_run:%d' % (nstep_tot, nstep_run))
        return nstep_tot

    cc_name  = pvl[0].name()
    cc_value = pvl[0].value()
    logger.info('cc_name "%s" cc_value "%s"' % (cc_name, cc_value))

    cc_names = CALIBCYCLE_NAMES_DARK if nspace is None else calibcycle_names(nspace)
    ind = cc_names.index(cc_value)
    if ind in list_of_cc_collected():
        logger.warning('CALIB-CYCLE %d: %s HAS ALREADY BEEN PROCESSED. SKIPPING' % (ind, cc_value))
        return None

    if ind != nstep_tot:
        s = 'SEQUENTIAL CALIB-CYCLE nstep_tot:%d, nstep_run:%d' % (nstep_tot, nstep_run)
        s += ' IS NOT CONSISTENT WITH METADATA %d: %s' % (ind, cc_value)
        logger.warning(s)

    return ind

#--------------------

def list_of_cc_collected():
  if not hasattr(store, 'cc_collected'):
    store.cc_collected = []
  return store.cc_collected

#--------------------

def offset_calibration(*args, **opts):

    exp        = opts.get('exp', None)     
    detname    = opts.get('det', None)   
    run        = opts.get('run', None)    
    idx        = opts.get('idx', 0)    
    nbs        = opts.get('nbs', 4600)    
    nspace     = opts.get('nspace', 7)    
    dirxtc     = opts.get('dirxtc', None) 
    dirrepo    = opts.get('dirrepo', CALIB_REPO_EPIX10KA)
    display    = opts.get('display', True)
    fmt_offset = opts.get('fmt_offset', '%.6f')
    fmt_peds   = opts.get('fmt_peds',   '%.3f')
    fmt_rms    = opts.get('fmt_rms',    '%.3f')
    fmt_status = opts.get('fmt_status', '%4i')
    fmt_gain   = opts.get('fmt_gain',   '%.6f')
    dopeds     = opts.get('dopeds', True)
    dooffs     = opts.get('dooffs', True)
    usesmd     = opts.get('usesmd', False)
    dirmode    = opts.get('dirmode', 0o777)
    filemode   = opts.get('filemode', 0o666)
    ixoff      = opts.get('ixoff', 10)
    nperiods   = opts.get('nperiods', True)
    ccnum      = opts.get('ccnum', None)
    ccmax      = opts.get('ccmax', 103)
    skipncc    = opts.get('skipncc', 0)    
    logmode    = opts.get('logmode', 'DEBUG')
    errskip    = opts.get('errskip', False)

    logger.setLevel(DICT_NAME_TO_LEVEL[logmode])

    irun = int(run.split(',',1)[0].split('-',1)[0]) # int first run number from str of run(s)

    dsname = 'exp=%s:run=%s'%(exp,run) if dirxtc is None else 'exp=%s:run=%s:dir=%s'%(exp, run, dirxtc)
    if usesmd: dsname += ':smd'
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))

    save_log_record_on_start(dirrepo, _name, dirmode)

    cpdic = get_config_info_for_dataset_detname(dsname, detname, idx)
    tstamp      = cpdic.get('tstamp', None)
    panel_ids   = cpdic.get('panel_ids', None)
    expnum      = cpdic.get('expnum', None)
    shape       = cpdic.get('shape', None)
    ny,nx = shape

    if display:
        fig2, axim2, axcb2 = fig_img_cbar_axes()
        #fig2.canvas.manager.window.move(500, 0)
        plt.ion() # do not hold control on plt.show()
        #plt.ioff() # hold control on plt.show()

    panel_id = get_panel_id(panel_ids, idx)

    dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain, dir_rms, dir_status = dir_names(dirrepo, panel_id)
    fname_prefix, panel_alias = file_name_prefix(panel_id, tstamp, exp, irun)
    prefix_offset, prefix_peds, prefix_plots, prefix_gain, prefix_rms, prefix_status =\
            path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain, dir_rms, dir_status)
    fname_work = file_name_npz(dir_work, fname_prefix, expnum, nspace)

    create_directory(dir_panel,  mode=dirmode)
    create_directory(dir_offset, mode=dirmode)
    create_directory(dir_peds,   mode=dirmode)
    create_directory(dir_plots,  mode=dirmode)
    create_directory(dir_work,   mode=dirmode)
    create_directory(dir_gain,   mode=dirmode)
    create_directory(dir_rms,    mode=dirmode)
    create_directory(dir_status, mode=dirmode)

    try:
        npz=np.load(fname_work)
        logger.info('Charge-injection data loaded from file: %s' % fname_work)
        logger.info('SKIP CALIBRATION CYCLES')

        darks=npz['darks']
        fits_ml=npz['fits_ml']
        fits_hl=npz['fits_hl']

    except IOError:
        logger.info('Unavailable charge-injection data file: %s' % fname_work)
        logger.info('BEGIN CALIBRATION CYCLES')

        darks=np.zeros((7,ny,nx))
        fits_ml=np.zeros((ny,nx,2,2))
        fits_hl=np.zeros((ny,nx,2,2))
        nsp_ml=np.zeros((ny,nx),dtype=np.int16)
        nsp_hl=np.zeros((ny,nx),dtype=np.int16)

        ds = DataSource(dsname)
        det = Detector(detname)
        cd = Detector('ControlData')

        nstep_tot = -1
        for orun in ds.runs():
          print '==== run:', orun.run()

          for nstep_run, step in enumerate(orun.steps()):
            nstep_tot += 1
            logger.info('=============== calibcycle %02d ===============' % nstep_tot)

            nstep = step_counter(cd, nstep_tot, nstep_run, nspace)
            if nstep is None: continue

            figprefix = 'fig-%s-r%04d-%s-seg%02d-cc%03d'%\
                        (exp, orun.run(), detname.replace(':','-').replace('.','-'), idx, nstep)

            if nstep_tot<skipncc:
                logger.info('skip %d consecutive calib-cycles' % skipncc)
                continue

            elif nstep_tot>=ccmax: 
                logger.info('total number of calib-cycles %d exceeds ccmax %d' % (nstep_tot, ccmax))
                break
    
            elif ccnum is not None:
                # process calibcycle ccnum ONLY if ccnum is specified
                if   nstep < ccnum: continue
                elif nstep > ccnum: break

            mode = find_gain_mode(det, data=None).upper()
    
            if mode in GAIN_MODES_IN and nstep < len(GAIN_MODES_IN):
                mode_in_meta = GAIN_MODES_IN[nstep]
                logger.info('========== calibcycle %d: dark run processing for gain mode in configuration %s and metadata %s'\
                            %(nstep, mode, mode_in_meta))
                if mode != mode_in_meta:
                  logger.warning('INCONSISTENT GAIN MODES IN CONFIGURATION AND METADATA')
                  if not errskip: sys.exit()
                  logger.warning('FLAG ERRSKIP IS %s - keep processing next calib-cycle' % errskip)
                  continue

            nrec,nevt = -1,0
            #First 5 Calib Cycles correspond to darks:
            if dopeds and nstep<5:
                msg = 'DARK Calib Cycle %d ' % nstep
                block=np.zeros((nbs,ny,nx),dtype=np.int16)

                for nevt,evt in enumerate(step.events()):
                    raw = det.raw(evt)
                    do_print = selected_record(nevt)
                    if raw is None: #skip empty frames
                        logger.warning('Ev:%04d rec:%04d panel:%02d raw=None' % (nevt,nrec,idx))
                        msg += 'none'
                        continue
                    if nrec>nbs-2:
                        break
                    else:
                        nrec += 1
                        if raw.ndim > 2: raw=raw[idx,:]
                        if do_print: logger.info(info_ndarr(raw & M14, 'Ev:%04d rec:%04d panel:%02d raw & M14' % (nevt,nrec,idx)))
                        if display and nevt<3:
                            imsh, cbar = imshow_cbar(fig2, axim2, axcb2, raw, amin=None, amax=None, extent=None,\
                                                     interpolation='nearest', aspect='auto', origin='upper',\
                                                     orientation='vertical', cmap='inferno')
                            fig2.canvas.set_window_title('Run:%d calib-cycle:%d' % (orun.run(), nstep)) #, **kwargs)
                            fname = '%s-img-dark' % figprefix
                            axim2.set_title(fname, fontsize=10)
                            plt.savefig(fname+'.png')
                        block[nrec]=raw & M14
                        if nrec%200==0: msg += '.%s' % find_gain_mode(det, raw) 

                print_statistics(nevt, nrec)

                darks[nstep,:,:], nda_rms, nda_status = proc_dark_block(block[:nrec,:,:], **opts)
                logger.debug(msg)

                fname = '%s_rms_%s.dat' % (prefix_rms, GAIN_MODES[nstep])
                save_2darray_in_textfile(nda_rms, fname, filemode, fmt_rms)

                fname = '%s_status_%s.dat' % (prefix_status, GAIN_MODES[nstep])
                save_2darray_in_textfile(nda_status, fname, filemode, fmt_status)

            ####################
            elif not dooffs: 
                logger.debug(info_ndarr(darks, 'darks'))
                if nstep>4: break
                continue
            ####################

            #Next nspace**2 Calib Cycles correspond to pulsing in Auto Medium-to-Low    
            elif nstep>4 and nstep<5+nspace**2:
                msg = ' AML %2d/%2d '%(nstep-5+1,nspace**2)

                block=np.zeros((nbs,ny,nx),dtype=np.int16)
                evnum=np.zeros((nbs,),dtype=np.int16)
                for nevt,evt in enumerate(step.events()):   #read all frames
                    raw = det.raw(evt)
                    do_print = selected_record(nevt)
                    if raw is None:
                        logger.warning('Ev:%04d rec:%04d panel:%02d AML raw=None' % (nevt,nrec,idx))
                        msg += 'none'
                        continue
                    if nrec>nbs-2:
                        break
                    else:
                        nrec += 1
                        if raw.ndim > 2: raw=raw[idx,:]
                        if do_print: logger.info(info_ndarr(raw, 'Ev:%04d rec:%04d panel:%02d AML raw' % (nevt,nrec,idx)))
                        block[nrec]=raw
                        evnum[nrec]=nevt
                        if nevt%200==0: msg+='.'

                if display:
                    imsh, cbar = imshow_cbar(fig2, axim2, axcb2, block[nrec][:100,:100], amin=None, amax=None, extent=None,\
                                             interpolation='nearest', aspect='auto', origin='upper',\
                                             orientation='vertical', cmap='inferno')
                    fig2.canvas.set_window_title('Run:%d calib-cycle:%d events:%d' % (orun.run(), nstep, evnum[nrec])) #, **kwargs)
                    fname = '%s-img-charge' % figprefix
                    axim2.set_title(fname, fontsize=10)
                    plt.savefig(fname+'.png')

                print_statistics(nevt, nrec)

                istep=nstep-5
                jy=istep//nspace
                jx=istep%nspace                    
                block=block[:nrec,jy:ny:nspace,jx:nx:nspace]         # select only pulsed pixels
                evnum=evnum[:nrec]                                   # list of non-empty events
                fits0,nsp0,msgf=fit(block,evnum,display,figprefix,ixoff,nperiods) # fit offset, gain
                fits_ml[jy:ny:nspace,jx:nx:nspace]=fits0             # collect results
                nsp_ml[jy:ny:nspace,jx:nx:nspace]=nsp0               # collect switching points
                s = '\n  block fit results AML'\
                  + info_ndarr(fits0[:,:,0,0],'\n  M gain',   last=5)\
                  + info_ndarr(fits0[:,:,1,0],'\n  L gain',   last=5)\
                  + info_ndarr(fits0[:,:,0,1],'\n  M offset', last=5)\
                  + info_ndarr(fits0[:,:,1,1],'\n  L offset', last=5) 

                logger.info(msg + msgf + s)

            #Next nspace**2 Calib Cycles correspond to pulsing in Auto High-to-Low    
            elif nstep>4+nspace**2 and nstep<5+2*nspace**2:
                msg = ' AHL %2d/%2d '%(nstep-5-nspace**2+1,nspace**2)
                block=np.zeros((nbs,ny,nx),dtype=np.int16)
                evnum=np.zeros((nbs,),dtype=np.int16)
                for nevt,evt in enumerate(step.events()):   #read all frames
                    raw = det.raw(evt)
                    do_print = selected_record(nevt)
                    if raw is None:
                        logger.warning('Ev:%04d rec:%04d panel:%02d AHL raw=None' % (nevt,nrec,idx))
                        msg+='None'
                        continue
                    if nrec>nbs-2:
                        break
                    else:
                        nrec += 1
                        if raw.ndim > 2: raw=raw[idx,:]
                        if do_print: logger.info(info_ndarr(raw, 'Ev:%04d rec:%04d panel:%02d AHL raw' % (nevt,nrec,idx)))
                        block[nrec]=raw
                        evnum[nrec]=nevt
                        if nevt%200==0: msg+='.'

                print_statistics(nevt, nrec)

                istep=nstep-5-nspace**2
                jy=istep//nspace
                jx=istep%nspace                    
                block=block[:nrec,jy:ny:nspace,jx:nx:nspace]       # select only pulsed pixels
                evnum=evnum[:nrec]                                 # list of non-empty events
                fits0,nsp0,msgf=fit(block,evnum,display,figprefix,ixoff,nperiods) # fit offset, gain
                fits_hl[jy:ny:nspace,jx:nx:nspace]=fits0           # collect results
                nsp_hl[jy:ny:nspace,jx:nx:nspace]=nsp0
                s = '\n  block fit results AHL'\
                  + info_ndarr(fits0[:,:,0,0],'\n  H gain',   last=5)\
                  + info_ndarr(fits0[:,:,1,0],'\n  L gain',   last=5)\
                  + info_ndarr(fits0[:,:,0,1],'\n  H offset', last=5)\
                  + info_ndarr(fits0[:,:,1,1],'\n  L offset', last=5) 
                logger.info(msg + msgf + s)

            elif nstep>=5+2*nspace**2:
                break

            list_of_cc_collected().append(nstep)

        logger.debug(info_ndarr(fits_ml, '  fits_ml', last=10)) # shape:(352, 384, 2, 2)
        logger.debug(info_ndarr(fits_hl, '  fits_hl', last=10)) # shape:(352, 384, 2, 2)
        logger.debug(info_ndarr(darks,   '  darks',   last=10)) # shape:(352, 384, 7)

        #darks[6,:,:]=darks[4,:,:]-fits_ml[:,:,1,1] # 2020-06-19 M.D. - commented out, it is done later
        #darks[5,:,:]=darks[3,:,:]-fits_hl[:,:,1,1] # 2020-06-19 M.D. - commented out, it is done later

        #Save diagnostics data, can be commented out:
        #save fitting results
        fexists = os.path.exists(fname_work)
        np.savez_compressed(fname_work, darks=darks, fits_hl=fits_hl, fits_ml=fits_ml, nsp_hl=nsp_hl, nsp_ml=nsp_ml)
        if not fexists: set_file_access_mode(fname_work, filemode)
        logger.info('Saved:  %s' % fname_work)

    #--------------------
    #sys.exit('TEST EXIT')
    #--------------------

    #Save gains:
    gain_ml_m = fits_ml[:,:,0,0]
    gain_ml_l = fits_ml[:,:,1,0]
    gain_hl_h = fits_hl[:,:,0,0]
    gain_hl_l = fits_hl[:,:,1,0]
    fname_gain_AML_M = '%s_gainci_AML-M.dat' % prefix_gain
    fname_gain_AML_L = '%s_gainci_AML-L.dat' % prefix_gain
    fname_gain_AHL_H = '%s_gainci_AHL-H.dat' % prefix_gain
    fname_gain_AHL_L = '%s_gainci_AHL-L.dat' % prefix_gain
    save_2darray_in_textfile(gain_ml_m, fname_gain_AML_M, filemode, fmt_gain)
    save_2darray_in_textfile(gain_ml_l, fname_gain_AML_L, filemode, fmt_gain)
    save_2darray_in_textfile(gain_hl_h, fname_gain_AHL_H, filemode, fmt_gain)
    save_2darray_in_textfile(gain_hl_l, fname_gain_AHL_L, filemode, fmt_gain)

    #Save offsets:
    offset_ml_m = fits_ml[:,:,0,1]
    offset_ml_l = fits_ml[:,:,1,1]
    offset_hl_h = fits_hl[:,:,0,1]
    offset_hl_l = fits_hl[:,:,1,1]
    fname_offset_AML_M = '%s_offset_AML-M.dat' % prefix_offset
    fname_offset_AML_L = '%s_offset_AML-L.dat' % prefix_offset
    fname_offset_AHL_H = '%s_offset_AHL-H.dat' % prefix_offset
    fname_offset_AHL_L = '%s_offset_AHL-L.dat' % prefix_offset
    save_2darray_in_textfile(offset_ml_m, fname_offset_AML_M, filemode, fmt_offset)
    save_2darray_in_textfile(offset_ml_l, fname_offset_AML_L, filemode, fmt_offset)
    save_2darray_in_textfile(offset_hl_h, fname_offset_AHL_H, filemode, fmt_offset)
    save_2darray_in_textfile(offset_hl_l, fname_offset_AHL_L, filemode, fmt_offset)

    #Save offsets:
    offset_ahl = offset_hl_h - offset_hl_l # 2020-06-19 M.D. - difference at 0 is taken as offset for peds
    offset_aml = offset_ml_m - offset_ml_l # 2020-06-19 M.D. - difference at 0 is taken as offset for peds
    fname_offset_AHL = '%s_offset_AHL.dat' % prefix_offset
    fname_offset_AML = '%s_offset_AML.dat' % prefix_offset
    save_2darray_in_textfile(offset_ahl, fname_offset_AHL, filemode, fmt_offset)
    save_2darray_in_textfile(offset_aml, fname_offset_AML, filemode, fmt_offset)

    #Save darks accounting offset whenever appropriate:
    for i in range(5):  #looping through darks measured in Jack's order
        fname = '%s_pedestals_%s.dat' % (prefix_peds, GAIN_MODES[i])
        save_2darray_in_textfile(darks[i,:,:], fname, filemode, fmt_peds)

        if i==3:    # evaluate AHL_L from AHL_H
            ped_hl_h = darks[i,:,:]
            #ped_hl_l = ped_hl_h - offset_ahl # V0
            #ped_hl_l = ped_hl_h - offset_ahl + (offset_hl_h - ped_hl_h) * divide_protected(gain_hl_l, gain_hl_h) #V2
            ped_hl_l = offset_hl_l - (offset_hl_h - ped_hl_h) * divide_protected(gain_hl_l, gain_hl_h) #V3 Gabriel's
            fname = '%s_pedestals_AHL-L.dat' % prefix_peds
            save_2darray_in_textfile(ped_hl_l, fname, filemode, fmt_peds)

        elif i==4:  # evaluate AML_L from AML_M
            ped_ml_m = darks[i,:,:]
            #ped_ml_l = ped_ml_m - offset_aml # V0
            #ped_ml_l = ped_ml_m - offset_aml + (offset_ml_m - ped_ml_m) * divide_protected(gain_ml_l, gain_ml_m) #V2
            ped_ml_l = offset_ml_l - (offset_ml_m - ped_ml_m) * divide_protected(gain_ml_l, gain_ml_m) #V3 Gabriel's
            fname = '%s_pedestals_AML-L.dat' % prefix_peds
            save_2darray_in_textfile(ped_ml_l, fname, filemode, fmt_peds)
        
    if display:
        plt.close("all")
        fnameout='%s_plot_AML.pdf' % prefix_plots
        gm='AML'; titles=['M Gain','M Pedestal', 'L Gain', 'M-L Offset']
        plot_fit_results(0, fits_ml, fnameout, filemode, gm, titles)

        fnameout='%s_plot_AHL.pdf' % prefix_plots
        gm='AHL'; titles=['H Gain','H Pedestal', 'L Gain', 'H-L Offset']
        plot_fit_results(1, fits_hl, fnameout, filemode, gm, titles)

        plt.pause(5)

#--------------------

def plot_fit_results(ifig, fitres, fnameout, filemode, gm, titles): 
        plt.figure(ifig,facecolor='w',figsize=(11,8.5),dpi=72.27);plt.clf()
        plt.suptitle(gm)
        for i in range(4):
            plt.subplot(2,2,i+1)
            test=fitres[:,:,i//2,i%2]; testm=np.median(test); tests=3*np.std(test)
            plt.imshow(test,interpolation='nearest',cmap='Spectral',vmin=testm-tests,vmax=testm+tests)
            plt.colorbar()
            plt.title(gm+': '+titles[i])
        plt.pause(0.1)
        fexists = os.path.exists(fnameout)
        plt.savefig(fnameout)
        if not fexists: set_file_access_mode(fnameout, filemode)

#--------------------
#--------------------
#--------------------

def pedestals_calibration(*args, **opts):
    """NEWS significant ACCELERATION is acheived:
       - accumulate data for entire epix10kam_2m/quad array
       - use MPI 
       all-panel or selected-panel one-calibcycle (gain range) or all calibcycles calibration of pedestals
    """
    exp        = opts.get('exp', None)
    detname    = opts.get('det', None)
    run        = opts.get('run', None)
    nbs        = opts.get('nbs', 1024)
    ccnum      = opts.get('ccnum', None)
    ccmax      = opts.get('ccmax', 5)
    dirxtc     = opts.get('dirxtc', None)
    dirrepo    = opts.get('dirrepo', CALIB_REPO_EPIX10KA)
    fmt_peds   = opts.get('fmt_peds', '%.3f')
    fmt_rms    = opts.get('fmt_rms',  '%.3f')
    fmt_status = opts.get('fmt_status', '%4i')
    idx_sel    = opts.get('idx', None)
    dirmode    = opts.get('dirmode', 0o777)
    filemode   = opts.get('filemode', 0o666)
    usesmd     = opts.get('usesmd', False)
    logmode    = opts.get('logmode', 'DEBUG')
    errskip    = opts.get('errskip', False)

    logger.setLevel(DICT_NAME_TO_LEVEL[logmode])

    irun = int(run.split(',',1)[0].split('-',1)[0]) # int first run number from str of run(s)

    dsname = 'exp=%s:run=%s'%(exp,run) if dirxtc is None else 'exp=%s:run=%s:dir=%s'%(exp, run, dirxtc)
    if usesmd: dsname += ':smd'
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))

    save_log_record_on_start(dirrepo, _name, dirmode)

    cpdic = get_config_info_for_dataset_detname(dsname, detname)
    tstamp      = cpdic.get('tstamp', None)
    panel_ids   = cpdic.get('panel_ids', None)
    expnum      = cpdic.get('expnum', None)
    dettype     = cpdic.get('dettype', None)
    shape       = cpdic.get('shape', None)
    ny,nx = shape

    #panel_id = get_panel_id(panel_ids, idx)
    logger.debug('Found panel ids:\n%s' % ('\n'.join(panel_ids)))

    #read input xtc file and accumulate block of data

    #================= MPI

    #from mpi4py import MPI
    #comm = MPI.COMM_WORLD
    #rank = comm.Get_rank()
    #size = comm.Get_size() # number of MPI nodes; 1 for regular python command

    #=================

    ds = DataSource(dsname)
    det = Detector(detname)
    cd = Detector('ControlData')

    #print 'det.shape', det.shape()
    shape_block = [nbs,] + list(det.shape()) # [1024, 16, 352, 384]
    print 'Accumulate raw frames in block shape = %s' % str(shape_block)

    mode = None # gain_mode

    nstep_tot = -1
    for orun in ds.runs():
      print '==== run:', orun.run()

      for nstep_run, step in enumerate(orun.steps()): #(loop through calyb cycles, using only the first):
        nstep_tot += 1
        logger.info('=============== calibcycle %02d ===============' % nstep_tot)

        nstep = step_counter(cd, nstep_tot, nstep_run)
        if nstep is None: continue

        #if size > 1:
        #    # if MPI is on process all calibcycles, calibcycle per rank
        #    if nstep < rank: continue
        #    if nstep > rank: break

        if nstep_tot>=ccmax: break

        elif ccnum is not None:
            # process calibcycle ccnum ONLY if ccnum is specified and MPI is not used!!!
            if   nstep < ccnum: continue
            elif nstep > ccnum: break

        mode = find_gain_mode(det, data=None).upper()

        if mode in GAIN_MODES_IN:
            mode_in_meta = GAIN_MODES_IN[nstep]
            logger.info('========== calibcycle %d: dark run processing for gain mode in configuration %s and metadata %s'\
                        %(nstep, mode, mode_in_meta))
            if mode != mode_in_meta:
              logger.warning('INCONSISTENT GAIN MODES IN CONFIGURATION AND METADATA')
              if not errskip: sys.exit()
              logger.warning('FLAG ERRSKIP IS %s - keep processing next calib-cycle' % errskip)
              continue
        else:
            logger.warning('UNRECOGNIZED GAIN MODE: %s, DARKS NOT UPDATED...'%mode)
            sys.exit()
            #return

        #============================
        #continue # TEST
        #============================

        block=np.zeros(shape_block,dtype=np.int16)
        nrec,nevt = -1,0

        for nevt,evt in enumerate(step.events()):
            raw = det.raw(evt)
            do_print = selected_record(nevt)
            if raw is None: #skip empty frames
                if do_print: logger.info('Ev:%04d rec:%04d raw=None' % (nevt,nrec))
                continue
            if nrec>nbs-2:       # stop after collecting sufficient frames
                break
            else:
                #if raw.ndim > 2: raw=raw[idx,:]
                nrec += 1
                if do_print: logger.info(info_ndarr(raw & M14, 'Ev:%04d rec:%04d raw & M14' % (nevt,nrec)))
                block[nrec]=raw & M14

        print_statistics(nevt, nrec)

        #---- process statistics in block-array for panels

        for idx, panel_id in enumerate(panel_ids):

            if idx_sel is not None and idx_sel != idx: continue # skip panels if idx_sel is specified

            logger.info('\n%s\nprocess panel:%02d id:%s' % (100*'=', idx, panel_id))

            #if mode is None:
            #    msg = 'Gain mode for dark processing is not defined "%s" try to set option -m <gain-mode>' % mode
            #    logger.warning(msg)
            #    sys.exit(msg)

            dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain, dir_rms, dir_status = dir_names(dirrepo, panel_id)
            fname_prefix, panel_alias = file_name_prefix(panel_id, tstamp, exp, irun)
            #prefix_offset, prefix_peds, prefix_plots, prefix_gain = path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain)
            prefix_offset, prefix_peds, prefix_plots, prefix_gain, prefix_rms, prefix_status =\
                path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain, dir_rms, dir_status)

            #logger.debug('Directories under %s\n  SHOULD ALREADY EXIST after charge-injection offset_calibration' % dir_panel)
            #assert os.path.exists(dir_offset), 'Directory "%s" DOES NOT EXIST' % dir_offset
            #assert os.path.exists(dir_peds),   'Directory "%s" DOES NOT EXIST' % dir_peds        

            create_directory(dir_panel,  mode=dirmode)
            create_directory(dir_peds,   mode=dirmode)
            create_directory(dir_offset, mode=dirmode)
            create_directory(dir_gain,   mode=dirmode)
            create_directory(dir_rms,    mode=dirmode)
            create_directory(dir_status, mode=dirmode)

            #dark=block[:nrec,:].mean(0)  #Calculate mean

            #block.sahpe = (1024, 16, 352, 384)
            dark, rms, status = proc_dark_block(block[:nrec,idx,:], **opts) # process pedestals per-panel (352, 384)

            fname = '%s_pedestals_%s.dat' % (prefix_peds, mode)
            save_2darray_in_textfile(dark, fname, filemode, fmt_peds)

            fname = '%s_rms_%s.dat' % (prefix_rms, mode)
            save_2darray_in_textfile(rms, fname, filemode, fmt_rms)

            fname = '%s_status_%s.dat' % (prefix_status, mode)
            save_2darray_in_textfile(status, fname, filemode, fmt_status)

            #if this is an auto gain ranging mode, also calculate the corresponding _L pedestal:
            if mode=='AML-M':
                fname_offset_AML = find_file_for_timestamp(dir_offset, 'offset_AML', tstamp)
                offset=None
                if fname_offset_AML is not None and os.path.exists(fname_offset_AML):
                    offset=np.loadtxt(fname_offset_AML)
                    logger.info('Loaded: %s' % fname_offset_AML)
                else:
                    logger.warning('file with offsets DOES NOT EXIST: %s' % fname_offset_AML)
                    logger.warning('DO NOT save AML-L pedestals w/o offsets')

                if offset is not None:
                    fname = '%s_pedestals_AML-L.dat' % prefix_peds
                    save_2darray_in_textfile(dark if offset is None else (dark-offset), fname, filemode, fmt_peds)

            elif mode=='AHL-H':
                fname_offset_AHL = find_file_for_timestamp(dir_offset, 'offset_AHL', tstamp)
                offset=None
                if fname_offset_AHL is not None and os.path.exists(fname_offset_AHL):
                    offset=np.loadtxt(fname_offset_AHL)
                    logger.info('Loaded: %s' % fname_offset_AHL)
                else:
                    logger.warning('file with offsets DOES NOT EXIST: %s' % fname_offset_AHL)
                    logger.warning('DO NOT save AHL-L pedestals w/o offsets')

                if offset is not None:
                    fname = '%s_pedestals_AHL-L.dat' % prefix_peds
                    save_2darray_in_textfile(dark if offset is None else (dark-offset), fname, filemode, fmt_peds)

    #logger.info('==== Completed pedestal calibration for rank %d ==== ' % rank)

#--------------------
#--------------------
#--------------------
#--------------------

def merge_panel_gain_ranges(dir_ctype, panel_id, ctype, tstamp, shape, ofname, fmt='%.3f', fac_mode=0o777):

    logger.debug('In merge_panel_gain_ranges for\n  dir_ctype: %s\n  id: %s\n  ctype=%s tstamp=%s shape=%s'%\
                 (dir_ctype, panel_id, ctype, str(tstamp), str(shape)))

    nda_def = np.ones(shape, dtype=np.float32) if ctype in ('gain', 'gainci', 'rms') else\
              np.zeros(shape, dtype=np.float32)

    lstnda = []
    for igm,gm in enumerate(GAIN_MODES):
       fname = find_file_for_timestamp(dir_ctype, '%s_%s' % (ctype,gm), tstamp)
       nda = np.loadtxt(fname, dtype=np.float32) if fname is not None else\
             nda_def*GAIN_FACTOR_DEF[igm] if ctype in ('gain', 'gainci') else\
             nda_def 

       if fname is not None and ctype == 'gainci': # normalize gain factors
           med_nda = np.median(nda)
           if med_nda != 0:
               f_adu_to_kev = GAIN_FACTOR_DEF[igm] / med_nda
               nda = nda * f_adu_to_kev

       lstnda.append(nda if nda is not None else nda_def)
       #logger.debug(info_ndarr(nda, 'nda for %s' % gm))
       #logger.info('%5s : %s' % (gm,fname))

    nda = np.stack(tuple(lstnda))
    logger.debug('merge_panel_gain_ranges - merged with shape %s' % str(nda.shape))

    nda.shape = (7, 1, 352, 384)
    logger.debug(info_ndarr(nda, 'merged %s'%ctype))
    save_ndarray_in_textfile(nda, ofname, fac_mode, fmt)

    nda.shape = (7, 1, 352, 384) # because save_ndarray_in_textfile changes shape
    return nda

#--------------------

def merge_panels(lst):
    """ stack of 16 (or 4 or 1) arrays from list shaped as (7, 1, 352, 384) to (7, 16, 352, 384)
    """
    npanels = len(lst)   # 16 or 4 or 1
    shape = lst[0].shape # (7, 1, 352, 384)
    ngmods = shape[0]    # 7

    logger.debug('In merge_panels: number of panels %d number of gain modes %d' % (npanels,ngmods))

    # make list for merging of (352,384) blocks in right order
    mrg_lst = []
    for igm in range(ngmods):
        nda1gm = np.stack([lst[ind][igm,0,:] for ind in range(npanels)])
        mrg_lst.append(nda1gm)
    return np.stack(mrg_lst)

#--------------------

def add_links_for_gainci_fixed_modes(dir_gain, fname_prefix, verbose=True):
    """FH->AHL-H, FM->AML-M, FL->AML-L/AHL-L"""
    logger.debug('in add_links_for_gainci_fixed_modes, prefix: %s' % (fname_prefix))
    list_of_files = '\n    '.join([name for name in os.listdir(dir_gain)])
    logger.debug('list_of_files in %s:\n    %s' %(dir_gain, list_of_files))

    dic_links = {'FH': 'AHL-H',
                 'FM': 'AML-M',
                 'FL': 'AML-L'} # 'AHL-L'

    for k,v in dic_links.iteritems():
        fname_auto  = '%s/%s_gainci_%s.dat' % (dir_gain, fname_prefix, v)
        fname_fixed = '%s/%s_gainci_%s.dat' % (dir_gain, fname_prefix, k)
        #print 'file %s existx %s' % (fname_auto, os.path.exists(fname_auto))
        if os.path.exists(fname_auto) and not os.path.lexists(fname_fixed): 
            
            os.symlink(os.path.abspath(fname_auto), fname_fixed)

    return

#--------------------

def deploy_constants(*args, **opts):

    from PSCalib.NDArrIO import save_txt; global save_txt

    exp        = opts.get('exp', None)     
    detname    = opts.get('det', None)   
    irun       = opts.get('run', None)    
    tstamp     = opts.get('tstamp', None)    
    dirxtc     = opts.get('dirxtc', None) 
    dirrepo    = opts.get('dirrepo', CALIB_REPO_EPIX10KA)
    dircalib   = opts.get('dircalib', None)
    deploy     = opts.get('deploy', False)
    fmt_peds   = opts.get('fmt_peds', '%.3f')
    fmt_gain   = opts.get('fmt_gain', '%.6f')
    fmt_rms    = opts.get('fmt_rms',  '%.3f')
    fmt_status = opts.get('fmt_status', '%4i')
    logmode    = opts.get('logmode', 'DEBUG')
    dirmode    = opts.get('dirmode',  0o777)
    filemode   = opts.get('filemode', 0o666)
    high       = opts.get('high',   16.40) # ADU/keV #High gain: 132 ADU / 8.05 keV = 16.40 ADU/keV
    medium     = opts.get('medium', 5.466) # ADU/keV #Medium gain: 132 ADU / 8.05 keV / 3 = 5.466 ADU/keV
    low        = opts.get('low',    0.164) # ADU/keV#Low gain: 132 ADU / 8.05 keV / 100 = 0.164 ADU/keV
    proc       = opts.get('proc', None)

    logger.setLevel(DICT_NAME_TO_LEVEL[logmode])

    dsname = 'exp=%s:run=%d'%(exp,irun) if dirxtc is None else 'exp=%s:run=%d:dir=%s'%(exp, irun, dirxtc)
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))
 
    save_log_record_on_start(dirrepo, _name, dirmode)

    cpdic = get_config_info_for_dataset_detname(dsname, detname)
    tstamp_run  = cpdic.get('tstamp',    None)
    expnum      = cpdic.get('expnum',    None)
    shape       = cpdic.get('shape',     None)
    calibdir    = cpdic.get('calibdir',  None)
    strsrc      = cpdic.get('strsrc',    None)
    panel_ids   = cpdic.get('panel_ids', None)
    dettype     = cpdic.get('dettype',   None)

    global GAIN_FACTOR_DEF
    #GAIN_MODES     = ['FH','FM','FL','AHL-H','AML-M','AHL-L','AML-L']
    GAIN_FACTOR_DEF = [high, medium, low, high, medium, low, low]

    CTYPE_FMT = {'pedestals'   : fmt_peds,
                 'pixel_gain'  : fmt_gain,
                 'pixel_rms'   : fmt_rms,
                 'pixel_status': fmt_status}

    logger.debug('detector %s panel ids:\n%s' % (detname, '\n'.join(panel_ids)))

    tstamp = tstamp_run if tstamp is None else\
             tstamp if int(tstamp)>9999 else\
             tstamp_for_dataset('exp=%s:run=%d'%(exp,tstamp))

    logger.debug('search for calibration files with tstamp <= %s' % tstamp)

    # dict_consts for constants octype: 'pixel_gain', 'pedestals', etc.
    dic_consts = {} 
    for ind, panel_id in enumerate(panel_ids):
        logger.info('%s\nmerge constants for panel:%02d id: %s' % (110*'_', ind, panel_id))

        dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain, dir_rms, dir_status = dir_names(dirrepo, panel_id)
        fname_prefix, panel_alias = file_name_prefix(panel_id, tstamp, exp, irun)
        #prefix_offset, prefix_peds, prefix_plots, prefix_gain = path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain)
        prefix_offset, prefix_peds, prefix_plots, prefix_gain, prefix_rms, prefix_status =\
            path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain, dir_rms, dir_status)

        #mpars = (('pedestals', 'pedestals',    prefix_peds,   dir_peds),\
        #         ('rms',       'pixel_rms',    prefix_rms,    dir_rms),\
        #         ('status',    'pixel_status', prefix_status, dir_status),\
        #         ('gain',      'pixel_gain',   prefix_gain,   dir_gain))

        mpars = []
        if 'p' in proc: mpars.append(('pedestals', 'pedestals',    prefix_peds,   dir_peds))
        if 'r' in proc: mpars.append(('rms',       'pixel_rms',    prefix_rms,    dir_rms))
        if 's' in proc: mpars.append(('status',    'pixel_status', prefix_status, dir_status))
        if 'g' in proc: mpars.append(('gain',      'pixel_gain',   prefix_gain,   dir_gain))
        if 'c' in proc: mpars.append(('gainci',    'pixel_gain',   prefix_gain,   dir_gain))
        if 'c' in proc:
             add_links_for_gainci_fixed_modes(dir_gain, fname_prefix) # FH->AHL-H, FM->AML-M, FL->AML-L/AHL-L

        for (ctype, octype, prefix, dir_ctype) in mpars:
            fmt = CTYPE_FMT.get(octype,'%.5f')
            logger.debug('begin merging for ctype:%s, octype:%s, fmt:%s,\n  prefix:%s' % (ctype, octype, fmt, prefix))
            fname = '%s_%s.txt' % (prefix, ctype)
            nda = merge_panel_gain_ranges(dir_ctype, panel_id, ctype, tstamp, shape, fname, fmt, filemode)
            if octype in dic_consts: dic_consts[octype].append(nda) # append for panel per ctype
            else:                    dic_consts[octype] = [nda,]

    #--------------------
    #sys.exit('TEST EXIT')
    #--------------------

    logger.info('\n%s\nmerge panel constants and deploy them' % (80*'_'))

    dmerge = dir_merge(dirrepo)
    create_directory(dmerge, mode=dirmode)
    fmerge_prefix = fname_prefix_merge(dmerge, detname, tstamp, exp, irun)

    for octype, lst in dic_consts.iteritems():
        mrg_nda = merge_panels(lst)
        logger.info(info_ndarr(mrg_nda, 'merged constants for %s' % octype))
        fmerge = '%s-%s.txt' % (fmerge_prefix, octype)
        fmt = CTYPE_FMT.get(octype,'%.5f')
        save_ndarray_in_textfile(mrg_nda, fmerge, filemode, fmt)

        if dircalib is not None: calibdir = dircalib
        #ctypedir = .../calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'
        calibgrp = calib_group(dettype) # 'Epix10ka::CalibV1'
        ctypedir = '%s/%s/%s' % (calibdir, calibgrp, strsrc)
        #----------
        if deploy:
            ofname   = '%d-end.data' % irun
            lfname   = None
            verbos   = True
            logger.info('deploy calib files under %s' % ctypedir)
            deploy_file(fmerge, ctypedir, octype, ofname, lfname, verbos=(logmode=='DEBUG'))
        else:
            logger.warning('Add option -D to deploy files under directory %s' % ctypedir)
        #----------

#--------------------

if __name__ == "__main__":

    DIR_XTC_TEST = '/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/combined'

    def test_offset_calibration_epix10ka(tname):
        offset_calibration(exp     = 'mfxx32516',\
                           det     = 'NoDetector.0:Epix10ka.3',\
                           run     = 1021,\
                           nbs     = 4600,\
                           nspace  = 2,\
                           dirxtc  = DIR_XTC_TEST,\
                           dirrepo = './work',\
                           display = True)

#--------------------

    def test_pedestals_calibration_epix10ka(tname):
        pedestals_calibration(exp  = 'mfxx32516',\
                           det     = 'NoDetector.0:Epix10ka.3',\
                           run     = 1021,\
                           nbs     = 1024,\
                           #nspace  = 2,\
                           mode    = 'AML-M',\
                           dirxtc  = DIR_XTC_TEST,\
                           dirrepo = './work')

#--------------------

    def test_deploy_constants_epix10ka(tname):
        deploy_constants(  exp     = 'mfxx32516',\
                           det     = 'NoDetector.0:Epix10ka.3',\
                           run     = 1021,\
                           #tstamp  = None,\
                           #tstamp  = 20180314120622,\
                           tstamp  = 20180914120622,\
                           dirxtc  = DIR_XTC_TEST,\
                           #dirrepo = './work',\
                           dircalib= './calib',\
                           deploy  = True)

#--------------------

    def test_offset_calibration_epix10ka2m(tname):
        #offset_calibration(exp     = 'detdaq17',\
        #                   det     = 'DetLab.0:Epix10ka2M.0',\
        offset_calibration(exp     = 'xcsx35617',\
                           det     = 'XcsEndstation.0:Epix10ka2M.0',\
                           run     = 6,\
                           idx     = 1,\
                           nbs     = 4600,\
                           nspace  = 4,\
                           #dirxtc  = DIR_XTC_TEST,\
                           dirrepo = './work',\
                           display = True)

#--------------------

#runs=[#[1020,4],
#      [1021,2],
#      [1022,6],
#      [1023,4],
#      [1024,2],
#      [1025,6],
#      #[1026,],  #incomplete?   #-20C
#      [1027,2],
#      [1028,6],
#      [1029,4]]

#--------------------

if __name__ == "__main__":
    print(80*'_')
    logging.basicConfig(format='[%(levelname).1s] L%(lineno)04d: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname == '1': test_offset_calibration_epix10ka(tname)
    elif tname == '2': test_pedestals_calibration_epix10ka(tname)
    elif tname == '3': test_deploy_constants_epix10ka(tname)
    elif tname == '4': test_offset_calibration_epix10ka2m(tname)
    elif tname == '5': test_pedestals_calibration_epix10ka2m(tname)
    elif tname == '6': test_deploy_constants_epix10ka2m(tname)
    else: sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#--------------------
