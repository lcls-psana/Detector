from __future__ import print_function
#from __future__ import division

"""
:py:class:`UtilsJungfrauCalib`
==============================

Usage::
    from Detector.UtilsJungfrauCalib import *

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2021-04-05 by Mikhail Dubrovin
"""

import logging
logger = logging.getLogger(__name__)

from time import time
import os
import sys
import psana
import numpy as np
from time import time #, localtime, strftime
from Detector.GlobalUtils import info_command_line_parameters

import PSCalib.GlobalUtils as gu
from Detector.PyDataAccess import get_jungfrau_gain_mode_object #get_jungfrau_data_object, get_jungfrau_config_object
from Detector.GlobalUtils import info_ndarr
import Detector.UtilsCalib as uc
from Detector.UtilsJungfrau import info_jungfrau, jungfrau_uniqueid, jungfrau_config_object, shape_from_config_jungfrau
from Detector.dir_root import DIR_ROOT, DIR_LOG_AT_START

SCRNAME = os.path.basename(sys.argv[0])

NUMBER_OF_GAIN_MODES = 3

DIC_GAIN_MODE = {'FixedGain1':  1,
                 'FixedGain2':  2,
                 'ForcedGain1': 1,
                 'ForcedGain2': 2,
                 'HighGain0':   0,
                 'Normal':      0}

#BW1 =  040000 # 16384 or 1<<14 (14-th bit starting from 0)
#BW2 = 0100000 # 32768 or 2<<14 or 1<<15
#BW3 = 0140000 # 49152 or 3<<14
M14 =  0x3fff # 16383 or (1<<14)-1 - 14-bit mask
#M14 =  037777 # 16383 or (1<<14)-1

DIR_REPO = os.path.join(DIR_ROOT, 'detector/gains/jungfrau')  # for jungfrau_gain_constants
CALIB_REPO_JUNGFRAU = os.path.join(DIR_ROOT, 'detector/gains/jungfrau/panels')  # for jungfrau_dark_proc, jungfrau_deploy_constants
FNAME_PANEL_ID_ALIASES = '%s/.aliases_jungfrau.txt' % CALIB_REPO_JUNGFRAU
JUNGFRAU_REPO_SUBDIRS = ('pedestals', 'rms', 'status', 'dark_min', 'dark_max', 'plots')

# jungfrau repository naming scheme:
# /reg/g/psdm/detector/gains/jungfrau/panels/logs/2021/2021-04-21T101714_log_jungfrau_dark_proc_dubrovin.txt
# /reg/g/psdm/detector/gains/jungfrau/panels/logs/2021_log_jungfrau_dark_proc.txt
# /reg/g/psdm/detector/gains/jungfrau/panels/190408-181206-50c246df50010d/pedestals/jungfrau_0001_20201201085333_cxilu9218_r0238_pedestals_gm0-Normal.dat

class DarkProcJungfrau(uc.DarkProc):

    """dark data accumulation and processing for Jungfrau.
       Extends DarkProc to account for bad gain mode switch state in self.bad_switch array and pixel_status.
    """
    def __init__(self, **kwa):
        kwa.setdefault('datbits', 0x3fff)
        uc.DarkProc.__init__(self, **kwa)
        self.modes = ['Normal-00', 'Med-01', 'Low-11', 'UNKNOWN-10']


    def init_proc(self):
        uc.DarkProc.init_proc(self)
        shape_raw = self.arr_med.shape
        self.bad_switch = np.zeros(shape_raw, dtype=np.uint8)


    def add_event(self, raw, irec):
        uc.DarkProc.add_event(self, raw, irec)
        self.add_statistics_bad_gain_switch(raw, irec)


    def add_statistics_bad_gain_switch(self, raw, irec, evgap=10):
        #if irec%evgap: return #parsify events

        igm    = self.gmindex
        gmname = self.gmname

        t0_sec = time()
        gbits = raw>>14 # 00/01/11 - gain bits for mode 0,1,2
        fg0, fg1, fg2 = gbits==0, gbits==1, gbits==3
        bad = (np.logical_not(fg0),\
               np.logical_not(fg1),\
               np.logical_not(fg2))[igm]

        if irec%evgap==0:
           dt_sec = time()-t0_sec
           fgx = gbits==2
           sums = [fg0.sum(), fg1.sum(), fg2.sum(), fgx.sum()]
           logger.debug('Rec: %4d found pixels %s gain definition time: %.6f sec igm=%d:%s'%\
                    (irec,' '.join(['%s:%d' % (self.modes[i], sums[i]) for i in range(4)]), dt_sec, igm, gmname))

        np.logical_or(self.bad_switch, bad, self.bad_switch)


    def summary(self):
        t0_sec = time()
        uc.DarkProc.summary(self)
        logger.info('\n  status 64: %8d pixel with bad gain mode switch' % self.bad_switch.sum())
        self.arr_sta += self.bad_switch*64 # add bad gain mode switch to pixel_status
        self.arr_msk = np.select((self.arr_sta>0,), (self.arr0,), 1) #re-evaluate mask
        self.block = None
        self.irec = -1
        logger.info('summary consumes %.3f sec' % (time()-t0_sec))


    def info_results(self, cmt='DarkProc results'):
        return uc.DarkProc.info_results(self, cmt)\
         +info_ndarr(self.bad_switch, '\n  badswch')\


    def plot_images(self, titpref=''):
        uc.DarkProc.plot_images(self, titpref)
        plotim = self.plotim
        #if plotim &   1: plot_image(self.arr_av1, tit=titpref + 'average')
        if plotim &2048: plot_image(self.bad_switch, tit=titpref + 'bad gain mode switch')


def info_gain_modes(gm):
    s = 'gm.names:'
    for name in gm.names.items(): s += '\n    %s' % str(name)
    s += '\ngm.values:'
    for value in gm.values.items(): s += '\n    %s' % str(value)
    return s


def selected_record(i, events):
    return i<5\
       or (i<50 and not i%10)\
       or (i<200 and not i%20)\
       or not i%100\
       or i>events-5


def jungfrau_dark_proc(parser):
    """jungfrau dark data processing for single (of 3) gain mode.
    """
    t0_sec = time()
    tdt = t0_sec

    (popts, pargs) = parser.parse_args()

    kwargs = vars(popts) # dict of options

    evskip = popts.evskip
    evstep = popts.evstep
    events = popts.events
    source = popts.source
    dsname = popts.dsname
    stepnum= popts.stepnum
    stepmax= popts.stepmax
    evcode = popts.evcode
    segind = popts.segind

    dirrepo = popts.dirrepo

    dirmode  = kwargs.get('dirmode',  0o2777)
    filemode = kwargs.get('filemode', 0o666)

    #clbdir = popts.clbdir
    #if clbdir is not None: psana.setOption('psana.calib-dir', clbdir)

    logger.info(info_command_line_parameters(parser))

    ecm = False
    if evcode is not None:
        from Detector.EventCodeManager import EventCodeManager
        ecm = EventCodeManager(evcode, verbos=0)
        logger.info('requested event-code list %s' % str(ecm.event_code_list()))

    s = 'DIC_GAIN_MODE {<name> : <number>}'
    for k,v in DIC_GAIN_MODE.items(): s += '\n%16s: %d' % (k,v)
    logger.info(s)

    #_name = sys._getframe().f_code.co_name
    #uc.save_log_record_at_start(dirrepo, _name, dirmode, filemode)

    ds  = psana.DataSource(dsname)
    det = psana.Detector(source)
    env = ds.env()

    dpo = None
    igm0 = None
    is_single_run = uc.is_single_run_dataset(dsname)

    nevtot = 0
    nevsel = 0
    nsteptot = 0
    ss = ''

    logger.info('dsname: %s  detname: %s  is_single_run: %s' % (dsname, det.name, is_single_run))

    #info_jungfrau(ds, source)
    jf_id = jungfrau_uniqueid(ds, source)
    s = 'panel_ids:'
    for i,pname in enumerate(jf_id.split('_')):
        s += '\n  %02d panel id %s' % (i, pname)
        if i == segind: s += '  <-- selected for processing'
    logger.info(s)

    terminate_runs = False

    ts_run, ts_now = uc.tstamps_run_and_now(env, fmt=uc.TSTAMP_FORMAT)

    for irun, run in enumerate(ds.runs()):
        logger.info('\n%s Run %d %s' % (20*'=', run.run(), 20*'='))
        terminate_steps = False
        nevrun = 0
        for istep, step in enumerate(run.steps()):
            nsteptot += 1

            if stepmax is not None and nsteptot>stepmax:
                logger.info('==== Step:%02d loop is terminated, --stepmax=%d' % (nsteptot, stepmax))
                terminate_runs = True
                break

            if stepnum is not None:
                # process calibcycle stepnum ONLY if stepnum is specified
                if istep < stepnum:
                    logger.info('Skip step %d < --stepnum = %d' % (istep, stepnum))
                    continue
                elif istep > stepnum:
                    logger.info('Break further processing due to step %d > --stepnum = %d' % (istep, stepnum))
                    terminate_runs = True
                    break

            env = step.env()
            gmo = get_jungfrau_gain_mode_object(env, source)
            igm = DIC_GAIN_MODE[gmo.name]

            if dpo is None:
               kwargs['dettype'] = det.dettype
               dpo = DarkProcJungfrau(**kwargs)
               #dpo = uc.DarkProc(**kwargs)
               dpo.runnum = run.run()
               dpo.exp = env.experiment()
               dpo.calibdir = env.calibDir().replace('//','/')
               dpo.ts_run, dpo.ts_now = ts_run, ts_now #uc.tstamps_run_and_now(env, fmt=uc.TSTAMP_FORMAT)
               dpo.detid = jf_id
               dpo.gmindex = igm
               dpo.gmname = gmo.name

               igm0 = igm

            if igm != igm0:
               logger.warning('event for wrong gain mode index %d, expected %d' % (igm, igm0))

            if istep==0:
                logger.info('gain mode info from jungfrau configuration\n%s' % info_gain_modes(gmo))

            logger.info('\n== begin step %d gain mode "%s" index %d' % (istep, gmo.name, igm))

            for ievt, evt in enumerate(step.events()):

                nevrun += 1
                nevtot += 1

                #print('xxx event %d'%ievt)#, end='\r')

                if ievt<evskip:
                    s = 'skip event %d < --evskip=%d' % (ievt, evskip)
                    #print(s, end='\r')
                    if (selected_record(ievt+1, events) and ievt<evskip-1)\
                    or ievt==evskip-1: logger.info(s)
                    continue

                if ievt>=evstep:
                    print()
                    logger.info('break at ievt %d == --evstep=%d' % (ievt, evstep))
                    break

                if nevtot>=events:
                    print()
                    logger.info('break at nevtot %d == --events=%d' % (nevtot, events))
                    terminate_steps = True
                    terminate_runs = True
                    break

                if ecm:
                  if not ecm.select(evt):
                    print('    skip event %d due to --evcode=%s selected %d ' % (ievt, evcode, nevsel), end='\r')
                    continue
                  #else: print()

                raw = det.raw(evt)
                if raw is None:
                    logger.info('det.raw(evt) is None in event %d' % ievt)
                    continue

                raw = (raw if segind is None else raw[segind,:]) # NO & M14 herte

                nevsel += 1

                tsec = time()
                dt   = tsec - tdt
                tdt  = tsec
                if selected_record(ievt+1, events):
                    #print()
                    ss = 'run[%d] %d  step %d  events total/run/step/selected: %4d/%4d/%4d/%4d  time=%7.3f sec dt=%5.3f sec'%\
                         (irun, run.run(), istep, nevtot, nevrun, ievt+1, nevsel, time()-t0_sec, dt)
                    if ecm:
                       print()
                       ss += ' event codes: %s' % str(ecm.event_codes(evt))
                    logger.info(ss)
                #else: print(ss, end='\r')

                if dpo is not None:
                    status = dpo.event(raw,ievt)
                    if status == 2:
                        logger.info('requested statistics --nrecs=%d is collected - terminate loops' % popts.nrecs)
                        #if ecm:
                        #    terminate_runs = True
                        #    terminate_steps = True
                        break # evt loop

                # End of event-loop

            print()
            ss = 'run[%d] %d  end of step %d  events total/run/step/selected: %4d/%4d/%4d/%4d'%\
                 (irun, run.run(), istep, nevtot, nevrun, ievt+1, nevsel)
            logger.info(ss)

            if ecm:
                logger.info('continue to accumulate statistics, due to --evcode=%s' % evcode)
            else:
                logger.info('reset statistics for next step')

                if dpo is not None:
                    dpo.summary()
                    dpo.show_plot_results()
                    save_results(dpo, **kwargs)
                    del(dpo)
                    dpo=None

            if terminate_steps:
                logger.info('terminate_steps')
                break

            # End of step-loop

        logger.info(ss)
        logger.info('run %d, number of steps processed %d' % (run.run(), istep+1))

        #if is_single_run:
        #    logger.info('terminated due to is_single_run:%s' % is_single_run)
        #    break

        if dpo is not None:
            dpo.summary()
            dpo.show_plot_results()
            save_results(dpo, **kwargs)
            del(dpo)
            dpo=None

        if terminate_runs:
            logger.info('terminate_runs')
            break

        # End of run-loop

    logger.info('number of runs processed %d' % (irun+1))
    logger.info('%s\ntotal consumed time = %.3f sec.' % (40*'_', time()-t0_sec))


def save_results(dpo, **kwa):
    logger.info('save_results')

    dirrepo    = kwa.get('dirrepo', CALIB_REPO_JUNGFRAU)
    segind     = kwa.get('segind', None)
    panel_type = kwa.get('panel_type', 'jungfrau')
    dirmode    = kwa.get('dirmode', 0o2777)
    filemode   = kwa.get('filemode', 0o666)
    fmt_peds   = kwa.get('fmt_peds',   '%.3f')
    fmt_rms    = kwa.get('fmt_rms',    '%.3f')
    fmt_status = kwa.get('fmt_status', '%4i')
    fmt_minmax = kwa.get('fmt_status', '%6i')

    runnum     = dpo.runnum
    exp        = dpo.exp
    calibdir   = dpo.calibdir
    ts_run     = dpo.ts_run
    ts_now     = dpo.ts_now
    detid      = dpo.detid
    gmindex    = dpo.gmindex
    gmname     = dpo.gmname

    logger.info('exp:%s run:%d ts_run:%s ts_now:%s' % (exp, runnum, ts_run, ts_now))
    logger.info('calibdir: %s' % calibdir)
    logger.info('detid: %s' % detid)
    logger.info('gmindex: %d gmname: %s' % (gmindex, gmname))

    logger.info(dpo.info_results(cmt='dark data processing results to save'))

    list_save = (\
      ('pedestals', dpo.arr_av1, fmt_peds),\
      ('rms',       dpo.arr_rms, fmt_rms),\
      ('status',    dpo.arr_sta, fmt_status),\
      ('dark_min',  dpo.arr_min, fmt_minmax),\
      ('dark_max',  dpo.arr_max, fmt_minmax),\
    )
    #  dpo.arr_msk
    #  dpo.gate_lo
    #  dpo.gate_hi

    #ctypes = list_save[:][0]

    repoman = uc.RepoManager(dirrepo, dirmode=dirmode, filemode=filemode, dir_log_at_start=DIR_LOG_AT_START)
    #dlog = repoman.dir_logs_year()

    panel_ids = detid.split('_')

    for i, panel_id in enumerate(panel_ids):
        if segind is not None and i != segind:
            logger.info('skip saving data for panel %d due to --segind=%d' % (i,segind))
            continue

        dirpanel = repoman.dir_panel(panel_id)
        logger.info('panel %02d dir: %s' % (i, dirpanel))

        fname_prefix, panel_alias = uc.file_name_prefix(panel_type, panel_id, ts_run, exp, runnum, FNAME_PANEL_ID_ALIASES)
        logger.debug('fname_prefix: %s' % fname_prefix)

        for ctype, arr, fmt in list_save:
            dirname = repoman.makedir_type(panel_id, ctype)
            fname = '%s/%s_%s_gm%d-%s.dat' % (dirname, fname_prefix, ctype, gmindex, gmname)
            arr2d = arr[i,:] if segind is None else arr
            uc.save_2darray_in_textfile(arr2d, fname, filemode, fmt)


def info_object_dir(o, sep=',\n  '):
    return 'dir(%s):\n  %s' % (str(o), sep.join([v for v in dir(o) if v[:1]!='_']))


def jungfrau_config_info(dsname, detname, idx=0):
    from psana import DataSource, Detector
    ds = DataSource(dsname)
    det = Detector(detname)
    env = ds.env()
    co = jungfrau_config_object(env, det.source)

    #print(info_object_dir(env))
    #print(info_object_dir(co))
    logger.debug('jungfrau config. object: %s' % str(co))

    cpdic = {}
    cpdic['expname'] = env.experiment()
    cpdic['calibdir'] = env.calibDir().replace('//','/')
    cpdic['strsrc'] = det.pyda.str_src
    cpdic['shape'] = shape_from_config_jungfrau(co)
    cpdic['panel_ids'] = jungfrau_uniqueid(ds, detname).split('_')
    cpdic['dettype'] = det.dettype
    #cpdic['gain_mode'] = find_gain_mode(det, data=None) #data=raw: distinguish 5-modes w/o data
    for nevt,evt in enumerate(ds.events()):
        raw = det.raw(evt)
        if raw is not None:
            tstamp, tstamp_now = uc.tstamps_run_and_now(env)
            cpdic['tstamp'] = tstamp
            del ds
            del det
            break
    logger.info('configuration info for %s %s segment=%d:\n%s' % (dsname, detname, idx, str(cpdic)))
    return cpdic


def merge_jf_panel_gain_ranges(dir_ctype, panel_id, ctype, tstamp, shape, ofname, fmt='%.3f', fac_mode=0o666, errskip=True):

    logger.debug('In merge_panel_gain_ranges for\n  dir_ctype: %s\n  id: %s\n  ctype=%s tstamp=%s shape=%s'%\
                 (dir_ctype, panel_id, ctype, str(tstamp), str(shape)))

    # define default constants to substitute missing
    nda_def = np.ones(shape, dtype=np.float32) if ctype in ('gain', 'rms', 'dark_max') else\
              np.zeros(shape, dtype=np.float32) # 'pedestals', 'status', 'dark_min'
    if ctype == 'dark_max': nda_def *= M14

    # fillout dict {igm:nda} of gain range constants for panel
    dicnda = {0:None, 1:None, 2:None}
    dic_fnames = {}
    for gm, igm in DIC_GAIN_MODE.items():
        pattern = '%s_gm%d-%s' % (ctype,igm,gm)
        fname = uc.find_file_for_timestamp(dir_ctype, pattern, tstamp)
        if fname is not None:
            dicnda[igm] = np.loadtxt(fname, dtype=np.float32)
            dic_fnames[igm] = fname

    # convert dict to list of gain range constants for panel
    lstnda = []
    for igm in range(NUMBER_OF_GAIN_MODES):
        nda = dicnda[igm]
        fname = dic_fnames.get(igm, 'use default')
        check_exists(fname, errskip, 'panel constants "%s" for gm:%d and tstamp %s NOT FOUND %s' % (ctype, igm, str(tstamp), fname))
        logger.info('merge gm:%d %s' % (igm, fname))
        lstnda.append(nda if nda is not None else nda_def)
        #logger.debug(info_ndarr(nda, 'nda for %s' % gm))
        #logger.info('%5s : %s' % (gm,fname))

    nda = np.stack(tuple(lstnda))
    logger.debug('merge_panel_gain_ranges - merged with shape %s' % str(nda.shape))

    nda.shape = (3, 1, 512, 1024)
    logger.debug(info_ndarr(nda, 'merged %s'%ctype))
    uc.save_ndarray_in_textfile(nda, ofname, fac_mode, fmt)

    nda.shape = (3, 1, 512, 1024) # because save_ndarray_in_textfile changes shape
    return nda


def fname_prefix_merge(dmerge, detname, tstamp, exp, irun):
    return '%s/%s-%s-%s-r%04d' % (dmerge, detname, tstamp, exp, irun)


def check_exists(path, errskip, msg):
    if path is None or (not os.path.exists(path)):
        if errskip: logger.warning(msg)
        else:
            msg += '\n  to fix this issue please process this or previous dark run using command jungfrau_dark_proc'\
                   '\n  or add the command line parameter -E or --errskip to skip missing file errors, use default, and force to deploy constants.'
            logger.error(msg)
            sys.exit(1)


def jungfrau_deploy_constants(parser):
    """jungfrau deploy constants
    """
    t0_sec = time()
    logger.info(info_command_line_parameters(parser))

    (popts, pargs) = parser.parse_args()
    kwa = vars(popts) # dict of options

    exp        = kwa.get('exp', None)
    detname    = kwa.get('det', None)
    irun       = kwa.get('run', None)
    tstamp     = kwa.get('tstamp', None)
    dirxtc     = kwa.get('dirxtc', None)
    dirrepo    = kwa.get('dirrepo', CALIB_REPO_JUNGFRAU)
    dircalib   = kwa.get('dircalib', None)
    deploy     = kwa.get('deploy', False)
    errskip    = kwa.get('errskip', False)
    logmode    = kwa.get('logmode', 'DEBUG')
    dirmode    = kwa.get('dirmode',  0o2777)
    filemode   = kwa.get('filemode', 0o666)
    gain0      = kwa.get('gain0', 41.5)    # ADU/keV ? /reg/g/psdm/detector/gains/jungfrau/MDEF/g0_gain.npy
    gain1      = kwa.get('gain1', -1.39)   # ADU/keV ? /reg/g/psdm/detector/gains/jungfrau/MDEF/g1_gain.npy
    gain2      = kwa.get('gain2', -0.11)   # ADU/keV ? /reg/g/psdm/detector/gains/jungfrau/MDEF/g2_gain.npy
    offset0    = kwa.get('offset0', 0.01)  # ADU
    offset1    = kwa.get('offset1', 300.0) # ADU
    offset2    = kwa.get('offset2', 50.0)  # ADU
    proc       = kwa.get('proc', None)
    paninds    = kwa.get('paninds', None)
    panel_type = kwa.get('panel_type', 'jungfrau')
    fmt_peds   = kwa.get('fmt_peds',   '%.3f')
    fmt_rms    = kwa.get('fmt_rms',    '%.3f')
    fmt_status = kwa.get('fmt_status', '%4i')
    fmt_minmax = kwa.get('fmt_status', '%6i')
    fmt_gain   = kwa.get('fmt_gain',   '%.6f')
    fmt_offset = kwa.get('fmt_offset', '%.6f')

    panel_inds = None if paninds is None else [int(i) for i in paninds.split(',')] # conv str '0,1,2,3' to list [0,1,2,3]
    dsname = 'exp=%s:run=%d'%(exp,irun) if dirxtc is None else 'exp=%s:run=%d:dir=%s'%(exp, irun, dirxtc)
    _name = sys._getframe().f_code.co_name

    logger.info('In %s\n      dataset: %s\n      detector: %s' % (_name, dsname, detname))

    #uc.save_log_record_at_start(dirrepo, _name, dirmode, filemode)

    cpdic = jungfrau_config_info(dsname, detname)
    tstamp_run  = cpdic.get('tstamp',    None)
    expname     = cpdic.get('expname',   None)
    shape       = cpdic.get('shape',     None)
    calibdir    = cpdic.get('calibdir',  None)
    strsrc      = cpdic.get('strsrc',    None)
    panel_ids   = cpdic.get('panel_ids', None)
    dettype     = cpdic.get('dettype',   None)

    shape_panel = shape[-2:]
    logger.info('shape of the detector: %s panel: %s' % (str(shape), str(shape_panel)))

    tstamp = tstamp_run if tstamp is None else\
             tstamp if int(tstamp)>9999 else\
             uc.tstamp_for_dataset('exp=%s:run=%d'%(exp,tstamp))

    logger.debug('search for calibration files with tstamp <= %s' % tstamp)

    repoman = uc.RepoManager(dirrepo, dirmode=dirmode, filemode=filemode, dir_log_at_start=DIR_LOG_AT_START)

    mpars = {\
      'pedestals':    ('pedestals', fmt_peds),\
      'pixel_rms':    ('rms',       fmt_rms),\
      'pixel_status': ('status',    fmt_status),\
      'dark_min':     ('dark_min',  fmt_minmax),\
      'dark_max':     ('dark_max',  fmt_minmax),\
    }

    # dict_consts for constants octype: 'pedestals','status', 'rms',  etc. {ctype:<list-of-per-panel-constants-merged-for-3-gains>}
    dic_consts = {}
    for ind, panel_id in enumerate(panel_ids):

        if panel_inds is not None and not (ind in panel_inds):
            logger.info('skip panel %d due to -I or --paninds=%s' % (ind, panel_inds)),
            continue # skip non-selected panels

        dirpanel = repoman.dir_panel(panel_id)
        logger.info('%s\nmerge gain range constants for panel %02d dir: %s' % (110*'_', ind, dirpanel))

        check_exists(dirpanel, errskip, 'panel directory does not exist %s' % dirpanel)

        fname_prefix, panel_alias = uc.file_name_prefix(panel_type, panel_id, tstamp, exp, irun, FNAME_PANEL_ID_ALIASES)
        logger.debug('fname_prefix: %s' % fname_prefix)

        for octype, (ctype, fmt) in mpars.items():
            dir_ctype = repoman.dir_type(panel_id, ctype)
            #logger.info('  dir_ctype: %s' % dir_ctype)
            fname = '%s/%s_%s.txt' % (dir_ctype, fname_prefix, ctype)
            nda = merge_jf_panel_gain_ranges(dir_ctype, panel_id, ctype, tstamp, shape_panel, fname, fmt, filemode, errskip=errskip)
            logger.info('-- save array of panel constants "%s" merged for 3 gain ranges shaped as %s in file\n%s%s\n'\
                        % (ctype, str(nda.shape), 21*' ', fname))

            if octype in dic_consts: dic_consts[octype].append(nda) # append for panel per ctype
            else:                    dic_consts[octype] = [nda,]

    logger.info('\n%s\nmerge all panel constants and deploy them' % (80*'_'))

    dmerge = repoman.makedir_merge()
    fmerge_prefix = fname_prefix_merge(dmerge, detname, tstamp, exp, irun)

    logger.info('fmerge_prefix: %s' % fmerge_prefix)

    for octype,lst in dic_consts.items():
        lst_nda = uc.merge_panels(lst)
        logger.info(info_ndarr(lst_nda, 'merged constants for %s' % octype))
        fmerge = '%s-%s.txt' % (fmerge_prefix, octype)
        fmt = mpars[octype][1]
        uc.save_ndarray_in_textfile(lst_nda, fmerge, filemode, fmt)

        if dircalib is not None: calibdir = dircalib
        #ctypedir = .../calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'
        calibgrp = uc.calib_group(dettype) # 'Epix10ka::CalibV1'
        ctypedir = '%s/%s/%s' % (calibdir, calibgrp, strsrc)

        if deploy:
            ofname   = '%d-end.data' % irun
            lfname   = None
            verbos   = True
            logger.info('deploy file %s/%s/%s' % (ctypedir, octype, ofname))
            gu.deploy_file(fmerge, ctypedir, octype, ofname, lfname, verbos=(logmode=='DEBUG'))
        else:
            logger.warning('Add option -D to deploy files under directory %s' % ctypedir)

# EOF
