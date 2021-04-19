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

import os
import sys
import psana
import numpy as np
from time import time #, localtime, strftime
from pyimgalgos.GlobalUtils import info_command_line_parameters
import PSCalib.GlobalUtils as gu
from Detector.PyDataAccess import get_jungfrau_gain_mode_object #get_jungfrau_data_object, get_jungfrau_config_object, time_pars_evt
from Detector.GlobalUtils import info_ndarr
from Detector.UtilsCalib import DarkProc, save_log_record_on_start, RepoManager, TSTAMP_FORMAT,\
                                save_2darray_in_textfile, tstamps_run_and_now, file_name_prefix,\
                                is_single_run_dataset 
from Detector.UtilsJungfrau import info_jungfrau, jungfrau_uniqueid
from PSCalib.UtilsPanelAlias import alias_for_id #, id_for_alias

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

CALIB_REPO_JUNGFRAU = '/reg/g/psdm/detector/gains/jungfrau/panels'
FNAME_PANEL_ID_ALIASES = '%s/.aliases_jungfrau.txt' % CALIB_REPO_JUNGFRAU

JUNGFRAU_REPO_SUBDIRS = ('pedestals', 'rms', 'status', 'plots')


# epix10ka file naming scheme:
# /reg/g/psdm/detector/gains/epix10k/panels/logs/log_pedestals_calibration_2021.txt
# /reg/g/psdm/detector/gains/epix10k/panels/logs/2020-08-19-r92-xcsc00118-epix10ka2m.0-offset-log10
# /reg/g/psdm/detector/gains/epix10k/panels/0000000001-0172862721-2919235606-1014046789-0019435010-0000000000-0000000000/pedestals/
# gain/  0 offset/  0 pedestals/  0 plots/  0 rms/  0 status/
# 1188 epix10ka_0045_20210406054111_xcslu8918_r0057_pedestals_AHL-H.dat
# 8320 epix10ka_0045_20210406054111_xcslu8918_r0057_pedestals.txt


# /reg/g/psdm/detector/gains/jungfrau/panels/190408-181206-50c246df50010d-20200202020202
LOG_FILE = '/reg/g/psdm/logs/calibman/#YYYY-MM/jungfrau_ndarr_dark_proc.txt'

SCRNAME = os.path.basename(sys.argv[0])


class JungfrauNDArrDarkProc(object):

    # Jungfrau gain range coding
    # bit: 15,14,...,0   Gain range, ind
    #       0, 0       - Normal,       0
    #       0, 1       - ForcedGain1,  1
    #       1, 1       - FixedGain2,   2

    def __init__(self, parser, igm):
        self.gmind = igm

    def save_ndarrays(self):
        """Saves n-d array in text files"""

        if self.counter:
            print(' save_ndarrays()')
        else:
            print(' save_ndarrays(): counter=0 - do not save files')
            return 

        addmetad = True

        det      = self.det
        ofname   = self.ofname
        verbos   = self.verbos
        savebw   = self.savebw
        counter  = self.counter

        cmts = ['DATASET  %s' % self.dsname, 'STATISTICS  %d' % counter]        
        template = gu.calib_fname_template(self.exp, self.runnum, self.tsec, self.tnsec, self.fid,\
                                           self.tsdate, self.tstime, self.src, counter, ofname)

        if savebw &  1: det.save_asdaq(template % 'ave', self.arr_av1, cmts + ['ARR_TYPE  average'], '%8.2f', verbos, addmetad)
        if savebw &  2: det.save_asdaq(template % 'rms', self.arr_rms, cmts + ['ARR_TYPE  RMS'],     '%8.2f', verbos, addmetad)
        if savebw &  4: det.save_asdaq(template % 'sta', self.arr_sta, cmts + ['ARR_TYPE  status'],  '%d',    verbos, addmetad)
        if savebw &  8: det.save_asdaq(template % 'msk', self.arr_msk, cmts + ['ARR_TYPE  mask'],    '%1d',   verbos, addmetad)
        if savebw & 16: det.save_asdaq(template % 'max', self.arr_max, cmts + ['ARR_TYPE  max'],     '%d',    verbos, addmetad)
        if savebw & 32: det.save_asdaq(template % 'min', self.arr_min, cmts + ['ARR_TYPE  min'],     '%d',    verbos, addmetad)
        if savebw & 64:
            cmod = self._common_mode_pars(self.arr_av1, self.arr_rms, self.arr_msk)
            if cmod is None: return
            np.savetxt(template % 'cmo', cmod, fmt='%d', delimiter=' ', newline=' ')
            det.save_asdaq(template % 'cmm', cmod, cmts + ['ARR_TYPE  common_mode'],'%d', verbos, False)

        #if verbos & 1: print('Data summary for %s is completed, dt=%7.3f sec' % (self.src, time()-t0_sec))


class JungfrauDarkProc(object):
    """Takes care about jungfrau dark data processing for a few (currently 3) gain modes.
    """
    def __init__(self, parser=None):
        # make gain-mode processing modules:
        self.lst_jdp = [JungfrauNDArrDarkProc(parser, igm) for igm in range(NUMBER_OF_GAIN_MODES)]
        self.status = None


    def stack_ndarrays(self):
        self.arr_av1 = np.stack([o.arr_av1 for o in self.lst_jdp])
        self.arr_rms = np.stack([o.arr_rms for o in self.lst_jdp])
        self.arr_sta = np.stack([o.arr_sta for o in self.lst_jdp])
        self.arr_msk = np.stack([o.arr_msk for o in self.lst_jdp])
        self.arr_max = np.stack([o.arr_max for o in self.lst_jdp])
        self.arr_min = np.stack([o.arr_min for o in self.lst_jdp])


    def save_ndarrays(self, addmetad=True):
        print('%s\nSave arrays:' % (80*'_'))

        jdp0 = self.lst_jdp[0]

        det      = jdp0.det
        ofname   = jdp0.ofname
        verbos   = jdp0.verbos
        savebw   = jdp0.savebw
        counter  = jdp0.counter
        str_src  = gu.string_from_source(det.source) # 'CxiEndstation.0:Jungfrau.0'

        cmts = ['DATASET  %s' % jdp0.dsname, 'STATISTICS  %d' % counter]        
        template = gu.calib_fname_template(jdp0.exp, jdp0.runnum, jdp0.tsec, jdp0.tnsec, jdp0.fid,\
                                           jdp0.tsdate, jdp0.tstime, str_src, counter, ofname)

        if verbos: print('File name template: %s' % template)

        gu.create_path(template, depth=0, mode=0o770, verb=True) # in case if template is work/...

        if savebw &  1: det.save_asdaq(template % 'ave', self.arr_av1, cmts + ['ARR_TYPE  average'], '%8.2f', verbos, addmetad)
        if savebw &  2: det.save_asdaq(template % 'rms', self.arr_rms, cmts + ['ARR_TYPE  RMS'],     '%8.2f', verbos, addmetad)
        if savebw &  4: det.save_asdaq(template % 'sta', self.arr_sta, cmts + ['ARR_TYPE  status'],  '%d',    verbos, addmetad)
        if savebw &  8: det.save_asdaq(template % 'msk', self.arr_msk, cmts + ['ARR_TYPE  mask'],    '%1d',   verbos, addmetad)
        if savebw & 16: det.save_asdaq(template % 'max', self.arr_max, cmts + ['ARR_TYPE  max'],     '%d',    verbos, addmetad)
        if savebw & 32: det.save_asdaq(template % 'min', self.arr_min, cmts + ['ARR_TYPE  min'],     '%d',    verbos, addmetad)

        if verbos: print('All files saved')

        if jdp0.upload:
            calibgrp = gu.dic_det_type_to_calib_group[gu.JUNGFRAU] # 'Jungfrau::CalibV1'
            clbdir = jdp0.clbdir if jdp0.clbdir is not None else '/reg/d/psdm/%s/%s/calib' % (jdp0.exp[:3], jdp0.exp)
            ctypedir = '%s/%s/%s' % (clbdir, calibgrp, str_src) # jdp0.src)
            fname = '%d-end.data' % jdp0.runnum

            #print('Deploy files in %s' % clbdir)
            print('Deploy files in %s' % ctypedir)

            if savebw &  1: gu.deploy_file(template % 'ave', ctypedir, 'pedestals',    fname, LOG_FILE, verbos)
            if savebw &  2: gu.deploy_file(template % 'rms', ctypedir, 'pixel_rms',    fname, LOG_FILE, verbos)
            if savebw &  4: gu.deploy_file(template % 'sta', ctypedir, 'pixel_status', fname, LOG_FILE, verbos)
            if savebw &  8: gu.deploy_file(template % 'msk', ctypedir, 'pixel_mask',   fname, LOG_FILE, verbos)
            if savebw & 16: gu.deploy_file(template % 'max', ctypedir, 'pixel_max',    fname, LOG_FILE, verbos)
            if savebw & 32: gu.deploy_file(template % 'min', ctypedir, 'pixel_min',    fname, LOG_FILE, verbos)


#===
#===
#===
#===
#===
#===
#===
#===
#===
#===
#===


def info_gain_modes(gm):
    s = 'gm.names:'
    for name in gm.names.items(): s += '\n    %s' % str(name)
    s += '\ngm.values:'
    for value in gm.values.items(): s += '\n    %s' % str(value)
    return s


def selected_record(i, events):
    return i<5\
       or not i%10\
       or i>events-5
    #   or (i<50 and not i%10)\
    #   or not i%100\
    #   or i>events-5


def jungfrau_dark_proc(parser):
    """jungfrau dark data processing for single (of 3) gain mode.
    """
    t0_sec = time()
    tdt = t0_sec

    (popts, pargs) = parser.parse_args()

    kwargs = vars(popts) # dict of options

    evskip = popts.evskip
    events = popts.events
    source = popts.source
    dsname = popts.dsname
    stepnum= popts.stepnum
    stepmax= popts.stepmax
    evcode = popts.evcode
    segind = popts.segind

    dirrepo = popts.dirrepo

    dirmode  = 0o777 # opts.get('dirmode',  0o777)
    filemode = 0o664 # opts.get('filemode', 0o666)

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

    #rec = gu.log_rec_on_start()
    #logger.info('log_rec_on_start:\n  %s' % rec)
    #gu.add_rec_to_log(LOG_FILE, rec, 0o377)
    _name = sys._getframe().f_code.co_name
    save_log_record_on_start(dirrepo, _name, filemode)

    #sys.exit('TEST EXIT')

    ds  = psana.DataSource(dsname)
    det = psana.Detector(source)
    env = ds.env()

    dpo = None
    igm0 = None
    is_single_run = is_single_run_dataset(dsname)

    nevtot = 0
    nevsel = 0
    nsteptot = 0
    ss = ''

    logger.info('dsname : %s' % dsname)
    logger.info('detname: %s' % det.name)

    #info_jungfrau(ds, source)
    jf_id = jungfrau_uniqueid(ds, source)
    s = 'panel_ids:'
    for i,pname in enumerate(jf_id.split('_')):
        s += '\n  %02d panel id %s' % (i, pname)
        if i == segind: s += '  <-- selected for processing'
    logger.info(s)

    #sys.exit('TEST EXIT')

    terminate_runs = False

    for irun, run in enumerate(ds.runs()):
        logger.info('\n%s Run %d %s' % (20*'=', run.run(), 20*'='))
        
        terminate_steps = False
        nevrun = 0
        for istep, step in enumerate(run.steps()):
            nsteptot += 1
            env = step.env()
            gmo = get_jungfrau_gain_mode_object(env, source)
            igm = DIC_GAIN_MODE[gmo.name]

            if dpo is None:
               dpo = DarkProc(**kwargs)
               dpo.runnum = run.run()
               dpo.exp = env.experiment()
               dpo.calibdir = env.calibDir()
               dpo.ts_run, dpo.ts_now = tstamps_run_and_now(env, fmt=TSTAMP_FORMAT)
               dpo.detid = jf_id
               dpo.gmindex = igm
               dpo.gmname = gmo.name

               igm0 = igm

            if igm != igm0:
               logger.warning('event for wrong gain mode index %d, expected %d' % (igm, igm0))

            if istep==0:
                logger.info('gain mode info from jungfrau configuration\n%s' % info_gain_modes(gmo))

            logger.info('\n== begin step %d gain mode "%s" index %d' % (istep, gmo.name, igm))

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

            for ievt, evt in enumerate(step.events()):
            
                nevrun += 1
                nevtot += 1

                #print('xxx event %d'%ievt)#, end='\r')

                if ievt<evskip:
                    s = 'skip event %d < --evskip=%d' % (ievt, evskip)
                    #print(s, end='\r')
                    if (selected_record(ievt, events) and ievt<evskip-1)\
                    or ievt==evskip-1: logger.info(s)
                    continue

                if not nevtot<events:
                    print()
                    logger.info('break at nevtot %d == --events=%d' % (nevtot, events))
                    terminate_steps = True
                    terminate_runs = True
                    break

                if ecm:
                  if not ecm.select(evt):
                    print('    skip event %d due to --evcode=%s selected %d ' % (ievt, evcode, nevsel), end='\r')
                    continue
                  else: print()

                raw = det.raw(evt)
                if raw is None:
                    logger.info('det.raw(evt) is None in event %d' % ievt)
                    continue

                raw = (raw if segind is None else raw[segind,:]) & M14 # for JFG, epix etc

                nevsel += 1

                tsec = time()
                dt   = tsec - tdt
                tdt  = tsec
                ss = 'run[%d] %d  step %d  events total/run/step/selected: %4d/%4d/%4d/%4d  time=%7.3f sec dt=%5.3f sec'%\
                     (irun, run.run(), istep, nevtot, nevrun, ievt+1, nevsel, time()-t0_sec, dt)
                if selected_record(ievt, events):
                    #print()
                    if ecm:
                       print()
                       ss += ' event codes: %s' % str(ecm.event_codes(evt))
                    logger.info(ss)
                #else: print(ss, end='\r')

                if dpo is not None:
                    status = dpo.event(raw,ievt)
                    if status == 2:
                        logger.info('requested statistics --nrecs=%d is collected - terminate loops' % popts.nrecs)
                        if ecm: terminate_runs = True
                        terminate_steps = True
                        break # evt loop

            print()
            logger.info('end of step %d in run[%d] %d number of events total/run/step/selected: %4d/%4d/%4d/%4d'%\
                  (istep, irun, run.run(), nevtot, nevrun, ievt+1, nevsel)) #, gmo.name))

            if ecm:
                logger.info('keep accumulate statistics, due to --evcode=%s' % evcode)
            else:
                logger.info('reset statistics for next step')
                
                if dpo is not None:
                    dpo.summary()
                    save_results(dpo, **kwargs)
                    del(dpo)
                    dpo=None

            if terminate_steps:
                logger.info('terminate_steps')
                break

        logger.info(ss)
        logger.info('run %d, number of steps processed %d' % (run.run(), istep+1))

        if is_single_run or terminate_runs:
            logger.info('terminated due to terminate_runs:%s or is_single_run:%s' % (terminate_runs, is_single_run))
            break

    if dpo is not None:
       dpo.summary()
       save_results(dpo, **kwargs)

    logger.info('number of runs processed %d' % (irun+1))
    logger.info('%s\ntotal consumed time = %.3f sec.' % (40*'_', time()-t0_sec))


def save_results(dpo, **kwa):
    logger.info('save_results')

    dirrepo    = kwa.get('dirrepo', CALIB_REPO_JUNGFRAU)
    segind     = kwa.get('segind', None)
    panel_type = kwa.get('panel_type', 'jungfrau')
    filemode   = kwa.get('filemode', 0o664)
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

    list_save = [\
      ['pedestals', dpo.arr_av1, fmt_peds],\
      ['rms',       dpo.arr_rms, fmt_rms],\
      ['status',    dpo.arr_sta, fmt_status],\
      ['dark_min',  dpo.arr_min, fmt_minmax],\
      ['dark_max',  dpo.arr_max, fmt_minmax],\
    ]
    #  dpo.arr_msk
    #  dpo.gate_lo
    #  dpo.gate_hi

    #ctypes = list_save[:][0]

    repoman = RepoManager(dirrepo)
    #dlog = repoman.dir_logs_year()

    panel_ids = detid.split('_')

    for i, panel_id in enumerate(panel_ids):
        if segind is not None and i != segind:
            logger.info('skip saving data for panel %d due to --segind=%d' % (i,segind))
            continue

        dirpanel = repoman.dir_panel(panel_id)
        logger.info('panel %02d dir: %s' % (i, dirpanel))

        fname_prefix, panel_alias = file_name_prefix(panel_type, panel_id, ts_run, exp, runnum, FNAME_PANEL_ID_ALIASES)
        logger.info('fname_prefix: %s' % fname_prefix)

        for ctype, arr, fmt in list_save:
            dirname = repoman.makedir_type(panel_id, ctype)
            fname = '%s/%s_%s_gm%d-%s.dat' % (dirname, fname_prefix, ctype, gmindex, gmname)
            arr2d = arr[i,:] if segind is None else arr
            save_2darray_in_textfile(arr2d, fname, filemode, fmt)

# EOF
