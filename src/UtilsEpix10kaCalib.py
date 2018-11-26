# -*- coding: utf-8 -*-
"""
Created on Fri May 11 18:25:48 2018 
CALIBRATION - TEST PULSES

@author: blaj
"""
#--------------------
import os
import sys
import logging
logger = logging.getLogger(__name__)

from time import sleep
from psana import DataSource, Detector
import numpy as np

from PSCalib.DCUtils import env_time, str_tstamp
from Detector.UtilsEpix import id_epix, CALIB_REPO_EPIX10KA, FNAME_PANEL_ID_ALIASES, alias_for_id, create_directory
from Detector.UtilsEpix10ka import config_objects, get_epix10ka_any_config_object,\
                            gain_maps_epix10ka_any # cbits_total_epix10ka_any

from Detector.UtilsEpix10ka2M import ids_epix10ka2m, print_object_dir # id_epix10ka, print_object_dir

#from Detector.PyDataAccess import get_epix_data_object, get_epix10ka_config_object,\
#                                  get_epix10kaquad_config_object, get_epix10ka2m_config_object,\
#                                  get_epix10ka_any_config_object

from PSCalib.GlobalUtils import log_rec_on_start, deploy_file, save_textfile # str_tstamp, replace
from Detector.GlobalUtils import info_ndarr, print_ndarr #, divide_protected

import matplotlib.pyplot as plt
#from numba import jit

# supress matplotlib deprication warnings
import warnings
warnings.filterwarnings("ignore",".*GUI is implemented.*")

#--------------------

GAIN_MODES    = ['FH','FM','FL','AHL-H','AML-M','AHL-L','AML-L']
GAIN_MODES_IN = ['FH','FM','FL','AHL-H','AML-M']

M14 = 0x3fff # 16383 or (1<<14)-1 - 14-bit mask

#--------------------

def init_plot(x,xx,itrim):
    f0=plt.figure(0,facecolor='w');f0.clf()
    ax0=f0.add_subplot(111)
    col='r' if itrim else 'g' # 'g'-medium 'r'-high gain
    line0,=ax0.plot(x,x,'ko',markersize=1)
    line1,=ax0.plot(xx,xx,'-',color=col,linewidth=1)
    line2,=ax0.plot(xx,xx,'b-',linewidth=1)
    ax0.set_xlim(0,1024);ax0.set_ylim(0,16384)
    ax0.set_xticks(np.arange(0,1025,128))
    ax0.set_yticks(np.arange(0,16385,2048))
    handle=f0,ax0,line0,line1,line2
    return handle

#--------------------

def update_plot(handle,trace,xx,pf0,pf1):
    f0,ax0,line0,line1,line2=handle
    line0.set_ydata(trace & M14) # (trace%16384)
    line1.set_ydata(np.polyval(pf0,xx))
    line2.set_ydata(np.polyval(pf1,xx))
    plt.pause(0.1)    







#--------------------

#@jit
def fit(block, itrim, ny=352, nx=384, display=True):

    mf,my,mx=block.shape
    fits=np.zeros((my,mx,2,2))
    nsp=np.zeros((my,mx),dtype=np.int16)
    
    x=np.arange(3*1024)%1024
    xx=np.linspace(1024,0,100)
    
    if display:
        handle=init_plot(x,xx,itrim)
    msg = ' fit '
    for iy in range(my):
        for ix in range(mx):
            trace=block[:,iy,ix]
            ixoff=np.argmin(np.diff(trace[:1025],axis=0),axis=0)+1 #find pulser value 0
            trace=trace[ixoff:ixoff+3*1024]                        #select the first 3 complete pulser cycles (0 to 1023)
            try:
                isp=int(np.median(np.where(np.diff(trace)>1000)[0]%1024))  #estimate median position of switching point
                nsp[iy,ix]=isp
            except ValueError:
                testval=np.median(trace%16384)
                ixoff=1024 if testval<0.5 else 0
            
            idx0=x<isp-50; idx1=x>isp+50                           #select data to the left and right of switching point
            if idx0.sum()>10:
                pf0=np.polyfit(x[idx0],trace[idx0]%16384,1)        #fit high/medium gain trace
            else:
                pf0=np.array([0,0])                                #or set to 0 if not enough data points
            if idx1.sum()>10:
                #pf1=np.polyfit(x[idx1],trace[idx1]%16384,1)       #this doesn't work!
                gl=pf0[0]/(100.0 if itrim else 33.33)               #Medium to Low
                ol=np.mean(trace[idx1]%16384-gl*x[idx1])           #calculate offset
                pf1=np.array([gl,ol])
            else:
                pf1=np.array([0,0])                                #ore st to zero if not enough data points
            fits[iy,ix,0]=pf0
            fits[iy,ix,1]=pf1
            
            i=iy*mx+ix
            if i%256==255:  #display a subset of plots
                #print '\b.',
                msg+='.'
                if display:
                    update_plot(handle,trace,xx,pf0,pf1)
    return fits,nsp,msg

#--------------------
#--------------------
#--------------------
#--------------------
#--------------------

#@jit
def fit_new(block, itrim, display=True):

    mf,my,mx=block.shape

    print info_ndarr(block, 'XXXX block')

    fits=np.zeros((my,mx,2,2))
    nsp=np.zeros((my,mx),dtype=np.int16)
    
    x=np.arange(3*1024)%1024
    xx=np.linspace(1024,0,100)

    if display:
        handle=init_plot(x,xx,itrim)
    msg = ' fit '
    for iy in range(my):
        for ix in range(mx):
            trace=block[:,iy,ix] & M14
            ixoff=np.argmin(np.diff(trace[:1025],axis=0),axis=0)+1 #find pulser value 0
            trace=trace[ixoff:ixoff+3*1024]                        #select the first 3 complete pulser cycles (0 to 1023)
            #trace=trace[ixoff:]                        #select the first 3 complete pulser cycles (0 to 1023)
            try:
                isp=int(np.median(np.where(np.diff(trace)>1000)[0]%1024))  #estimate median position of switching point
                nsp[iy,ix]=isp
            except ValueError:
                testval=np.median(trace) # %16384)
                ixoff=1024 if testval<0.5 else 0

            idx0=x<isp-50; idx1=x>isp+50                           #select data to the left and right of switching point

            #print 'XXXX ixoff:', ixoff
            #print info_ndarr(trace, 'XXXX trace')
            #print 'XXXX isp:', isp
            #print info_ndarr(idx0, 'XXXX idx0')
            #print info_ndarr(idx1, 'XXXX idx1')
            #print 'XXXX idx0.sum():', idx0.sum()

            if idx0.sum()>10:
                pf0=np.polyfit(x[idx0],trace[idx0],1) # %16384,1)        #fit high/medium gain trace
            else:
                pf0=np.array([0,0])                                #or set to 0 if not enough data points


            if idx1.sum()>10:
                #pf1=np.polyfit(x[idx1],trace[idx1]%16384,1)       #this doesn't work!
                gl=pf0[0]/(100.0 if itrim else 33.33)               #Medium to Low
                ol=np.mean(trace[idx1]-gl*x[idx1])       #trace[idx1]%16384    #calculate offset
                pf1=np.array([gl,ol])
            else:
                pf1=np.array([0,0])                                #ore st to zero if not enough data points

            fits[iy,ix,0]=pf0
            fits[iy,ix,1]=pf1
            
            i=iy*mx+ix
            if i%256==255:  #display a subset of plots
                #print '\b.',
                msg+='.'
                if display:
                    update_plot(handle,trace,xx,pf0,pf1)
    return fits,nsp,msg

#--------------------

def find_file_for_timestamp(dirname, pattern, tstamp) :
    # list of file names in directory, dirname, containing pattern
    fnames = [name for name in os.listdir(dirname) if pattern in name]

    # list of int tstamps 
    # !!! here we assume specific name structure generated by file_name_prefix
    itstamps = [int(name.split('_',3)[2]) for name in fnames]

    # reverse-sort int timestamps in the list
    itstamps.sort(key=int,reverse=True)

    # find the nearest to requested timestamp
    for its in itstamps :
        if its <= int(tstamp) :
            # find and return the full file name for selected timestamp
            ts = str(its)

            for name in fnames :
                if ts in name : 
                     fname = '%s/%s' % (dirname, name)
                     logger.debug('  selected %s for %s and %s' % (os.path.basename(fname),pattern,tstamp))
                     return fname

    logger.warning('Directory %s\n DOES NOT CONTAIN file for pattern %s and timestamp %s' % (dirname,pattern,tstamp))
    return None

#--------------------

#def shape_from_config(det) :
#    """DEPRICATED single-panel version
#    """
#    c = get_epix10ka_config_object(det.env, det.source)
#    shape = (c.numberOfRows(), c.numberOfColumns())
#    #logger.debug('shape_from_config: %s' % str(shape))
#    return shape

#--------------------

def shape_from_config_epix10ka(eco) :
    """Returns element/panel/sensor shape (352,384) from element configuration object
       psana.Epix.Config10ka or psana.Epix.Config10kaV1
    """
    #print_object_dir(eco)
    return (eco.numberOfRows(), eco.numberOfColumns())

#--------------------

def print_config_info(c) :
    """Prints config infor for single panel objectpsana.Epix.Config10kaV1
    """
    if c is not None :
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

def get_panel_id(panel_ids, idx=0) :
    panel_id = panel_ids[idx] if panel_ids is not None else None
    if panel_id is None :
        logger.error('get_panel_id: panel_idis None, idx=%d' % idx)
        sys.exit('ERROR EXIT')
    return panel_id

#--------------------

def find_gain_mode(det, data=None) :
    """Returns str gain mode from the list GAIN_MODES or None.
       if data=None : distinguish 5-modes w/o data
    """
    gmaps = gain_maps_epix10ka_any(det, data)
    if gmaps is None : return None
    gr0, gr1, gr2, gr3, gr4, gr5, gr6 = gmaps

    arr1 = np.ones_like(gr0)
    npix = arr1.size
    pix_stat = (np.select((gr0,), (arr1,), 0).sum(),\
                np.select((gr1,), (arr1,), 0).sum(),\
                np.select((gr2,), (arr1,), 0).sum(),\
                np.select((gr3,), (arr1,), 0).sum(),\
                np.select((gr4,), (arr1,), 0).sum(),\
                np.select((gr5,), (arr1,), 0).sum(),\
                np.select((gr6,), (arr1,), 0).sum())

    #logger.debug('Statistics in gain groups: %s' % str(pix_stat))

    f = 1.0/arr1.size
    grp_prob = [npix*f for npix in pix_stat]
    #logger.debug('grp_prob: %s' % str(grp_prob))

    ind = next(i for i,fr in enumerate(grp_prob) if fr>0.5)
    gain_mode = GAIN_MODES[ind] if ind<len(grp_prob) else None 
    #logger.debug('Gain mode %s is selected from %s' % (gain_mode, ', '.join(GAIN_MODES)))

    return gain_mode

#--------------------

def tstamps_run_and_now(env) :
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

def ids_epix10ka_any_for_dataset_detname(dsname, detname) :
    ds = DataSource(dsname)
    det = Detector(detname)
    env = ds.env()
    co = get_epix10ka_any_config_object(env, det.source)
    return ids_epix10ka2m(co)

#--------------------

def get_config_info_for_dataset_detname(dsname, detname, idx=0) :
    ds = DataSource(dsname)
    det = Detector(detname)
    env = ds.env()
    dco,qco,eco = config_objects(env, det.source, idx)
    co = next(o for o in (dco,qco,eco) if o is not None)

    #print_object_dir(dco)
    #print('dco', dco)
    #print('qco', qco)
    #print('eco', eco)
    print('XXXX highest co', co)

    cpdic = {}
    cpdic['expnum'] = env.expNum()
    cpdic['calibdir'] = env.calibDir()
    cpdic['strsrc'] = det.pyda.str_src
    cpdic['shape'] = shape_from_config_epix10ka(eco)
    cpdic['gain_mode'] = find_gain_mode(det, data=None) #data=raw: distinguish 5-modes w/o data
    cpdic['panel_ids'] = ids_epix10ka2m(co)

    for nevt,evt in enumerate(ds.events()):
        raw = det.raw(evt)
        if raw is not None: 
            tstamp, tstamp_now = tstamps_run_and_now(env)
            cpdic['tstamp'] = tstamp
            del ds
            del det
            return cpdic
    return cpdic

#--------------------

def save_log_record_on_start(dirrepo, fname) :
    """Adds record on start to the log file <dirlog>/logs/log-<fname>-<year>.txt
    """
    rec = log_rec_on_start()
    year = str_tstamp(fmt='%Y')
    dirlog = '%s/logs' % dirrepo
    create_directory(dirlog, mode=0777)
    logfname = '%s/log_%s_%s.txt' % (dirlog, fname, year)
    save_textfile(rec, logfname, mode='a')
    logger.debug('Record on start: %s' % rec)
    logger.info('Saved:  %s' % logfname)

#--------------------

def dir_names(dirrepo, panel_id) :
    """Defines structure of subdirectories in calibration repository.
    """
    dir_panel  = '%s/%s' % (dirrepo, panel_id)
    dir_offset = '%s/offset'    % dir_panel
    dir_peds   = '%s/pedestals' % dir_panel
    dir_plots  = '%s/plots'     % dir_panel
    dir_work   = '%s/work'      % dir_panel
    dir_gain   = '%s/gain'      % dir_panel
    return dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain
    
#--------------------

def file_name_prefix(panel_id, tstamp, exp, irun) :
    panel_alias = alias_for_id(panel_id, fname=FNAME_PANEL_ID_ALIASES)
    return 'epix10ka_%s_%s_%s_r%04d' % (panel_alias, tstamp, exp, irun)

#--------------------

def file_name_npz(dir_work, fname_prefix, expnum, nspace) :
    return '%s/%s_sp%02d_df.npz' % (dir_work, fname_prefix, nspace)

#--------------------

def path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain) :
    prefix_offset= '%s/%s' % (dir_offset, fname_prefix)
    prefix_peds  = '%s/%s' % (dir_peds,  fname_prefix)
    prefix_plots = '%s/%s' % (dir_plots, fname_prefix)
    prefix_gain  = '%s/%s' % (dir_gain,  fname_prefix)
    return prefix_offset, prefix_peds, prefix_plots, prefix_gain
#--------------------

def selected_record(nrec) :
    return nrec<5\
       or (nrec<50 and not nrec%10)\
       or (nrec<500 and not nrec%100)\
       or (not nrec%1000)

#--------------------

def offset_calibration(*args, **opts) :

    exp        = opts.get('exp', None)     
    detname    = opts.get('det', None)   
    irun       = opts.get('run', None)    
    idx        = opts.get('idx', 0)    
    nbs        = opts.get('nbs', 4600)    
    nspace     = opts.get('nspace', 7)    
    dirxtc     = opts.get('dirxtc', None) 
    dirrepo    = opts.get('dirrepo', CALIB_REPO_EPIX10KA)
    display    = opts.get('display', True)
    fmt_peds   = opts.get('fmt_peds', '%.3f')
    fmt_offset = opts.get('fmt_offset', '%.6f')

    dsname = 'exp=%s:run=%d'%(exp,irun) if dirxtc is None else 'exp=%s:run=%d:dir=%s'%(exp, irun, dirxtc)
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))
 
    save_log_record_on_start(dirrepo, _name)

    cpdic = get_config_info_for_dataset_detname(dsname, detname, idx)
    tstamp      = cpdic.get('tstamp', None)
    panel_ids   = cpdic.get('panel_ids', None)
    expnum      = cpdic.get('expnum', None)
    shape       = cpdic.get('shape', None)
    ny,nx = shape

    panel_id = get_panel_id(panel_ids, idx)

    dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain = dir_names(dirrepo, panel_id)
    fname_prefix = file_name_prefix(panel_id, tstamp, exp, irun)
    prefix_offset, prefix_peds, prefix_plots, prefix_gain = path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain)
    fname_work = file_name_npz(dir_work, fname_prefix, expnum, nspace)

    create_directory(dir_offset, mode=0777)
    create_directory(dir_peds,   mode=0777)
    create_directory(dir_plots,  mode=0777)
    create_directory(dir_work,   mode=0777)
    create_directory(dir_gain,   mode=0777)

    #--------------------
    #sys.exit('TEST EXIT')
    #--------------------

    try:
        npz=np.load(fname_work)
        logger.info('Loaded: %s' % fname_work)

        darks=npz['darks']
        fits_ml=npz['fits_ml']
        fits_hl=npz['fits_hl']

    except IOError:
        darks=np.zeros((ny,nx,7))
        fits_ml=np.zeros((ny,nx,2,2))
        fits_hl=np.zeros((ny,nx,2,2))
        nsp_ml=np.zeros((ny,nx),dtype=np.int16)
        nsp_hl=np.zeros((ny,nx),dtype=np.int16)

        #ds = DataSource('/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/pslab03/e0-r1013-s00-c00.xtc')
        ds = DataSource(dsname)
        det = Detector(detname)

        #print 'XXXXXX number of steps', len(steps)
        #print_object_dir(ds)

        for nstep, step in enumerate(ds.steps()):
            
            #First 5 Calib Cycles correspond to darks:
            if nstep<5:
                #dark
                msg = 'DARK %d ' % nstep
                nrec = 0
                block=np.zeros((nbs,ny,nx),dtype=np.int16)
                for nevt,evt in enumerate(step.events()):
                    raw = det.raw(evt)
                    if selected_record(nrec) :
                        logger.debug(info_ndarr(raw, 'Ev:%04d rec:%04d raw' % (nevt,nrec)))
                    if raw is None:
                        msg += 'none'
                        continue
                    if nevt>=nbs:
                        break
                    else:
                        #block=insert_subframe(block,raw,nevt,nspace,nevt-5)
                        if raw.ndim > 2 : raw=raw[idx,:]
                        block[nrec]=raw
                        nrec += 1
                        if nevt%128==0:
                            msg += '.%s' % find_gain_mode(det, raw) 

                darks[:,:,nstep]=block[:nrec,:].mean(0)
                logger.debug(msg)

            ####################
            elif False: # True - terminates further loops over calib cycles
                logger.debug(info_ndarr(darks, 'XXXXXXX darks'))
                if nstep>4 : break
                continue
            ####################

            #Next nspace**2 Calib Cycles correspond to pulsing in Auto Medium-to-Low    
            elif nstep<5+nspace**2:
                #data
                msg = ' AML %2d/%2d '%(nstep-5+1,nspace**2)
                nrec = 0
                block=np.zeros((nbs,ny,nx),dtype=np.int16)
                for nevt,evt in enumerate(step.events()):   #read all frames
                    raw = det.raw(evt)
                    if selected_record(nrec) :
                        logger.debug(info_ndarr(raw, 'Ev:%04d rec:%04d AM_L' % (nevt,nrec)))
                    if raw is None:
                        msg += 'none'
                        continue
                    if nevt>=nbs:
                        break
                    else:
                        #block=insert_subframe(block,raw,nevt,nspace,nevt-5)
                        if raw.ndim > 2 : raw=raw[idx,:]
                        block[nrec]=raw
                        nrec += 1
                        if nevt%200==0:
                            msg+='.'
                nrec -= 1
                print 'XXXX nevt:%d nrec:%d' % (nevt, nrec)

                istep=nstep-5
                jy=istep//nspace
                jx=istep%nspace                    
                block=block[:,jy:ny:nspace,jx:nx:nspace]   #select only pulsed pixels
                #block=block[:nrec,jy:ny:nspace,jx:nx:nspace]   #select only pulsed pixels
                fits0,nsp0,msgf=fit(block,0,display=display)    #fit offset, gain
                fits_ml[jy:ny:nspace,jx:nx:nspace]=fits0   #collect results
                nsp_ml[jy:ny:nspace,jx:nx:nspace]=nsp0
                #print 'NEVT='+str(nevt)
                darks[:,:,6]=darks[:,:,4]-fits_ml[:,:,1,1]

                logger.debug(msg + msgf)
                

            #Next nspace**2 Calib Cycles correspond to pulsing in Auto High-to-Low    
            elif nstep<5+2*nspace**2:
                msg = ' AHL %2d/%2d '%(nstep-5-nspace**2+1,nspace**2)
                nrec = 0
                block=np.zeros((nbs,ny,nx),dtype=np.int16)
                for nevt,evt in enumerate(step.events()):   #read all frames
                    raw = det.raw(evt)
                    if selected_record(nrec) :
                        logger.debug(info_ndarr(raw, 'Ev:%04d rec:%04d AH_L' % (nevt,nrec)))
                    if raw is None:
                        msg+='none'
                        continue
                    if nevt>=nbs:
                        break
                    else:
                        #block=insert_subframe(block,raw,nevt,nspace,nevt-5)
                        if raw.ndim > 2 : raw=raw[idx,:]
                        block[nrec]=raw
                        nrec += 1
                        if nevt%200==0:
                            msg+='.'
                nrec -= 1
                print 'XXXX nevt:%d nrec:%d' % (nevt, nrec)

                istep=nstep-5-nspace**2
                jy=istep//nspace
                jx=istep%nspace                    
                block=block[:,jy:ny:nspace,jx:nx:nspace]   #select only pulsed pixels
                #block=block[:nrec,jy:ny:nspace,jx:nx:nspace]   #select only pulsed pixels
                fits0,nsp0,msgf=fit(block,1,display=display)    #fit offset, gain
                fits_hl[jy:ny:nspace,jx:nx:nspace]=fits0   #collect results
                nsp_hl[jy:ny:nspace,jx:nx:nspace]=nsp0
                #print 'NEVT='+str(nevt)
                darks[:,:,5]=darks[:,:,3]-fits_hl[:,:,1,1]
                
                logger.debug(msg + msgf)

                #test=update_test(test,block,nspace,nstep-5)

            if nstep>=5+2*nspace**2:
                break
        #Save diagnostics data, can be commented out:
        #save fitting results
        np.savez_compressed(fname_work, darks=darks, fits_hl=fits_hl, fits_ml=fits_ml, nsp_hl=nsp_hl, nsp_ml=nsp_ml) 
        logger.info('Saved:  %s' % fname_work)

    #--------------------
    #sys.exit('TEST EXIT')
    #--------------------

    #Calculate and save offsets:
    offset_ahl=fits_hl[:,:,1,1]
    offset_aml=fits_ml[:,:,1,1]
    fname_offset_AHL = '%s_offset_AHL.dat' % prefix_offset
    fname_offset_AML = '%s_offset_AML.dat' % prefix_offset
    np.savetxt(fname_offset_AHL, offset_ahl, fmt=fmt_offset)
    np.savetxt(fname_offset_AML, offset_aml, fmt=fmt_offset)
    logger.info('Saved:  %s' % fname_offset_AHL)
    logger.info('Saved:  %s' % fname_offset_AML)

    #Save darks in separate files:
    for i in range(5):  #looping through darks measured in Jack's order
        fnameped = '%s_pedestals_%s.dat' % (prefix_peds, GAIN_MODES[i])
        np.savetxt(fnameped, darks[:,:,i], fmt=fmt_peds)
        logger.info('Saved:  %s' % fnameped)
        if i==3:    #if AHL_H, we can calculate AHL_L
            fnameped = '%s_pedestals_AHL-L.dat' % prefix_peds
            np.savetxt(fnameped, darks[:,:,i]-offset_ahl, fmt=fmt_peds)
            logger.info('Saved:  %s' % fnameped)
        elif i==4:  #if AML_M, we can calculate AML_L
            fnameped = '%s_pedestals_AML-L.dat' % prefix_peds
            np.savetxt(fnameped, darks[:,:,i]-offset_aml, fmt=fmt_peds)
            logger.info('Saved:  %s' % fnameped)
        
    if display:
        plt.close("all")
        fnameout='%s_plot_AML.pdf' % prefix_plots
        gm='AML'; titles=['M Gain','M Pedestal', 'L Gain', 'M-L Offset']
        plt.figure(1,facecolor='w',figsize=(11,8.5),dpi=72.27);plt.clf()
        plt.suptitle(gm)
        for i in range(4):
            plt.subplot(2,2,i+1)
            test=fits_ml[:,:,i//2,i%2]; testm=np.median(test); tests=3*np.std(test)
            plt.imshow(test,interpolation='nearest',cmap='Spectral',vmin=testm-tests,vmax=testm+tests)
            plt.colorbar()
            plt.title(gm+': '+titles[i])
        plt.pause(0.1)
        plt.savefig(fnameout)
        logger.info('Saved:  %s' % fnameout)

        fnameout='%s_plot_AHL.pdf' % prefix_plots
        gm='AHL'; titles=['H Gain','H Pedestal', 'L Gain', 'H-L Offset']
        plt.figure(2,facecolor='w',figsize=(11,8.5),dpi=72.27);plt.clf()
        for i in range(4):
            plt.subplot(2,2,i+1)
            test=fits_hl[:,:,i//2,i%2]; testm=np.median(test); tests=3*np.std(test)
            plt.imshow(test,interpolation='nearest',cmap='Spectral',vmin=testm-tests,vmax=testm+tests)
            plt.colorbar()
            plt.title(gm +': '+titles[i])
        plt.pause(0.1)
        plt.savefig(fnameout)
        logger.info('Saved:  %s' % fnameout)
        plt.pause(5)

#--------------------

def pedestals_calibration(*args, **opts) :

    exp        = opts.get('exp', None)
    detname    = opts.get('det', None)
    irun       = opts.get('run', None)
    idx        = opts.get('idx', 0)    
    nbs        = opts.get('nbs', 1024)
    nspace     = opts.get('nspace', 7)    
    dirxtc     = opts.get('dirxtc', None)
    dirrepo    = opts.get('dirrepo', CALIB_REPO_EPIX10KA)
    fmt_peds   = opts.get('fmt_peds', '%.3f')
    mode       = opts.get('mode', None)    

    dsname = 'exp=%s:run=%d'%(exp,irun) if dirxtc is None else 'exp=%s:run=%d:dir=%s'%(exp, irun, dirxtc)
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))

    save_log_record_on_start(dirrepo, _name)

    cpdic = get_config_info_for_dataset_detname(dsname, detname, idx)
    tstamp      = cpdic.get('tstamp', None)
    panel_ids   = cpdic.get('panel_ids', None)
    gain_mode   = cpdic.get('gain_mode', None)
    expnum      = cpdic.get('expnum', None)
    shape       = cpdic.get('shape', None)
    ny,nx = shape
    panel_id = get_panel_id(panel_ids, idx)

    if mode is None : mode = gain_mode 
    logger.info('Process dark run for gain mode %s' % mode)
    
    if mode is None : 
        msg = 'Gain mode for dark processing is not defined "%s" try to set option -m <gain-mode>' % mode
        logger.warning(msg)
        sys.exit(msg)

    dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain = dir_names(dirrepo, panel_id)
    fname_prefix = file_name_prefix(panel_id, tstamp, exp, irun)
    prefix_offset, prefix_peds, prefix_plots, prefix_gain = path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain)

    logger.debug('Directories under %s\n  SHOULD ALREADY EXIST after offset_calibration' % dir_panel)
    assert os.path.exists(dir_offset), 'Directory "%s" DOES NOT EXIST' % dir_offset
    assert os.path.exists(dir_peds),   'Directory "%s" DOES NOT EXIST' % dir_peds

    mode=mode.upper()

    if not (mode in GAIN_MODES_IN) :
        logger.warning('UNRECOGNIZED GAIN MODE: %s, DARKS NOT UPDATED.'%mode)
        return

    #read input xtc file and calculate pedestal
    #(currently misusing the first calib cycle of an existing file)

    ds = DataSource(dsname)
    det = Detector(detname)

    msg='READING RAW FRAMES (200 per ".") assuming %s mode '%(mode)
    for nstep, step in enumerate(ds.steps()): #(loop through calyb cycles, using only the first):
        block=np.zeros((nbs,ny,nx),dtype=np.int16)
        nrec=0;
        for nevt,evt in enumerate(step.events()):
            raw = det.raw(evt)
            if selected_record(nrec) :
                logger.debug(info_ndarr(raw, 'Ev:%04d rec:%04d raw' % (nevt,nrec)))
            if raw is None:     #skip empty frames
                msg+='none'
                continue
            if nrec>=nbs:       #stop after collecting sufficient frames
                break
            else:
                #block=insert_subframe(block,raw,nevt,nspace,nevt-5);
                if raw.ndim > 2 : raw=raw[idx,:]
                block[nrec]=raw;
                nrec+=1;
                if nevt%200==0: # simple progress bar
                    msg+='.'
                    
        if nstep>=0:    #only process the first CalibCycle (stop after 0)
            break

    logger.debug(msg)

    dark=block[:nrec,:].mean(0)  #Calculate mean 
    
    #save dark in proper place
    #fnameout=path_pedestal+'pedestal_%s_R%04d.dat'%(mode,irun);
    #np.savetxt(fnameout,dark);
    #print 'SAVED %s PEDESTALS.'%mode,
    fnameped = '%s_pedestals_%s.dat' % (prefix_peds, mode)
    np.savetxt(fnameped, dark, fmt=fmt_peds)
    logger.info('Saved:  %s' % fnameped)

    #if this is an auto gain ranging mode, also calculate the corresponding _L pedestal:
    if mode=='AML-M':
        fname_offset_AML = find_file_for_timestamp(dir_offset, 'offset_AML', tstamp)
        offset=np.loadtxt(fname_offset_AML);
        logger.info('Loaded: %s' % fname_offset_AML) 
        fnameped = '%s_pedestals_AML-L.dat' % prefix_peds
        np.savetxt(fnameped, dark-offset, fmt=fmt_peds)
        logger.info('Saved:  %s' % fnameped) 

        #fnameout=path_pedestal+'pedestal_%s_R%04d.dat'%('AML_L',irun);
        #np.savetxt(fnameout,dark-offset);
        #print 'SAVED AML_L PEDESTALS.',

    elif mode=='AHL-H':
        fname_offset_AHL = find_file_for_timestamp(dir_offset, 'offset_AHL', tstamp)
        offset=np.loadtxt(fname_offset_AHL);
        logger.info('Loaded: %s' % fname_offset_AHL) 
        fnameped = '%s_pedestals_AHL-L.dat' % prefix_peds
        np.savetxt(fnameped, dark-offset, fmt=fmt_peds)
        logger.info('Saved:  %s' % fnameped)

        #fnameout=path_pedestal+'pedestal_%s_R%04d.dat'%('AHL_L',irun);
        #np.savetxt(fnameout,dark-offset);
        #print 'SAVED AHL_L PEDESTALS.',

#--------------------

def merge_panel_constants(dirrepo, panel_id, ctype, tstamp, shape, ofname, fmt='%.3f') :

    from PSCalib.NDArrIO import save_txt

    logger.debug('In merge_panel_constants for\n  repo: %s\n  id: %s\n  ctype=%s tstamp=%s shape=%s'%\
                 (dirrepo, panel_id, ctype, str(tstamp), str(shape)))

    dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain = dir_names(dirrepo, panel_id)

    dir_ctype = dir_peds      if ctype == 'pedestals' else dir_gain
    nda_def = np.zeros(shape) if ctype == 'pedestals' else np.ones(shape)
    
    logger.debug('dir_ctype: %s' % dir_ctype)

    lstnda = []
    for gm in GAIN_MODES :
       fname = find_file_for_timestamp(dir_ctype, '%s_%s' % (ctype,gm), tstamp)
       nda = nda_def if fname is None else\
             np.loadtxt(fname, dtype=np.float32)
       lstnda.append(nda if nda is not None else nda_def)
       #logger.debug(info_ndarr(nda, 'nda for %s' % gm))
       #logger.info('%5s : %s' % (gm,fname))

    nda = np.stack(tuple(lstnda))
    #logger.debug(info_ndarr(nda, 'nda for %s' % gm))
    logger.debug('merge_panel_constants - merged with shape %s' % str(nda.shape))

    nda.shape = (7, 1, 352, 384)
    #nda = nda.astype(dtype=np.float32)
    logger.warning('SINGLE PANEL %s ARRAY RE-SHAPED TO %s' % (ctype, str(nda.shape)))

    logger.debug(info_ndarr(nda, 'merged %s'%ctype))

    save_txt(ofname, nda, fmt=fmt)
    logger.debug('Merged saved: %s' % ofname)

#--------------------

def deploy_constants(*args, **opts) :
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
    logmode    = opts.get('logmode', 'DEBUG')

    dsname = 'exp=%s:run=%d'%(exp,irun) if dirxtc is None else 'exp=%s:run=%d:dir=%s'%(exp, irun, dirxtc)
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))
 
    save_log_record_on_start(dirrepo, _name)

    cpdic = get_config_info_for_dataset_detname(dsname, detname)
    tstamp_run  = cpdic.get('tstamp', None)
    expnum      = cpdic.get('expnum', None)
    shape       = cpdic.get('shape', None)
    calibdir    = cpdic.get('calibdir', None)
    strsrc      = cpdic.get('strsrc', None)
    panel_ids   = cpdic.get('panel_ids', None)

    print 'XXX ids:\n', '\n'.join(panel_ids)

    tstamp = tstamp_run if tstamp is None else tstamp

    #########
    sys.exit('TEST EXIT')
    #########

    dir_panel, dir_offset, dir_peds, dir_plots, dir_work, dir_gain = dir_names(dirrepo, panel_id)
    fname_prefix = file_name_prefix(panel_id, tstamp, exp, irun)
    prefix_offset, prefix_peds, prefix_plots, prefix_gain = path_prefixes(fname_prefix, dir_offset, dir_peds, dir_plots, dir_gain)

    mpars = (('pedestals', 'pedestals', prefix_peds, fmt_peds),\
             ('gain',     'pixel_gain', prefix_gain, fmt_gain))

    for (ctype, octype, prefix, fmt) in mpars :

        logger.info('Begin merging for ctype:%s, octype:%s, prefix:%s, fmt:%s' % (ctype, octype, prefix, fmt))
        
        fname = '%s_%s.txt' % (prefix, ctype)
        merge_panel_constants(dirrepo, panel_id, ctype, tstamp, shape, fname, fmt)
        
        #----------
        if deploy :
            if dircalib is not None : calibdir = dircalib
            #ctypedir = /reg/d/psdm/mfx/mfxx32516/calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'
            ctypedir = '%s/Epix10ka::CalibV1/%s' % (calibdir, strsrc)
            ofname   = '%d-end.data' % irun
            lfname   = None
            verbos   = True
            logger.info('Deploy calib files under %s' % ctypedir)
            deploy_file(fname, ctypedir, octype, ofname, lfname, verbos=(logmode=='DEBUG'))
        else :
            logger.warning('Add option -D to deploy files under calib directory')
        #----------

#--------------------

if __name__ == "__main__" :

    DIR_XTC_TEST = '/reg/d/psdm/mfx/mfxx32516/scratch/gabriel/pulser/xtc/combined'

    def test_offset_calibration_epix10ka(tname) :
        offset_calibration(exp     = 'mfxx32516',\
                           det     = 'NoDetector.0:Epix10ka.3',\
                           run     = 1021,\
                           nbs     = 4600,\
                           nspace  = 2,\
                           dirxtc  = DIR_XTC_TEST,\
                           dirrepo = './work',\
                           display = True)

#--------------------

    def test_pedestals_calibration_epix10ka(tname) :
        pedestals_calibration(exp  = 'mfxx32516',\
                           det     = 'NoDetector.0:Epix10ka.3',\
                           run     = 1021,\
                           nbs     = 1024,\
                           nspace  = 2,\
                           mode    = 'AML-M',\
                           dirxtc  = DIR_XTC_TEST,\
                           dirrepo = './work')

#--------------------

    def test_deploy_constants_epix10ka(tname) :
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

    def test_offset_calibration_epix10ka2m(tname) :
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

if __name__ == "__main__" :
    print(80*'_')
    logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
    tname = sys.argv[1] if len(sys.argv)>1 else '1'
    if   tname == '1' : test_offset_calibration_epix10ka(tname)
    elif tname == '2' : test_pedestals_calibration_epix10ka(tname)
    elif tname == '3' : test_deploy_constants_epix10ka(tname)
    elif tname == '4' : test_offset_calibration_epix10ka2m(tname)
    elif tname == '5' : test_pedestals_calibration_epix10ka2m(tname)
    elif tname == '6' : test_deploy_constants_epix10ka2m(tname)
    else : sys.exit ('Not recognized test name: "%s"' % tname)
    sys.exit('End of %s' % sys.argv[0])

#--------------------
