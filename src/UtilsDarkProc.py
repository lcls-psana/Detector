
"""import Detector.UtilsDarkProc as udp"""

import logging
logger = logging.getLogger(__name__)
import psana
from time import time
from Detector.GlobalUtils import selected_record  # print_ndarr, divide_protected

from time import localtime, strftime

import Detector.UtilsCalib as uc

def event_time_fiducials(evt):
    evtid = evt.get(psana.EventId)
    tsec, tnsec = evtid.time()
    return tsec, tnsec, evtid.fiducials()

def replace(in_tmp, pattern, subst):
    """If pattern in the in_tmp replace it with subst.
       Returns str object in_tmp with replaced patterns.
    """
    fields = in_tmp.split(pattern, 1)
    if len(fields) > 1:
        return '%s%s%s' % (fields[0], subst, fields[1])
    else:
        return in_tmp

def str_tstamp(fmt='%Y-%m-%dT%H:%M:%S', time_sec=None):
    return strftime(fmt, localtime(time_sec))

def fname_template(evt, exp, src, ofname, nevts):
    """Replaces parts of the file name specified as
       #src, #exp, #run, #evts, #type, #date, #time, #fid, #sec, #nsec
       with actual values
    """
    tsec, tnsec, fid = event_time_fiducials(evt)
    template = replace(ofname,   '#src', src)
    template = replace(template, '#exp', exp)
    template = replace(template, '#run', 'r%04d'%evt.run())
    template = replace(template, '#type', '%s')
    template = replace(template, '#date', str_tstamp('%Y-%m-%d', tsec))
    template = replace(template, '#time', str_tstamp('%H:%M:%S', tsec))
    template = replace(template, '#fid',  str(fid))
    template = replace(template, '#sec',  '%d' % tsec)
    template = replace(template, '#nsec', '%09d' % tnsec)
    template = replace(template, '#evts', 'e%06d' % nevts)
    if not '%s' in template: template += '-%s'
    return template


class DarkProcDet(uc.DarkProc):

    def __init__(self, src, **kwa):

        uc.DarkProc.__init__(self, **kwa)
        self.src = src
        self.det = None
        self.ofname = kwa.get('ofname', 'nda-#exp-#run-#src-#evts-#type-#date-#time-#fid-#sec-#nsec.txt')
        self.dsname = kwa['dsname']
        self.expname = kwa['expname']
        logger.info('create DarkProcDet object for %s' % src)

    def event(self, evt, env, ievt):
        if self.det is None: self.det = psana.Detector(self.src)
        raw = self.det.raw(evt)
        if raw is None:
            logger.info('det.raw(evt) is None in event %d' % ievt)
            return None
        return uc.DarkProc.event(self, raw, ievt)

    def summary(self, evt, env):
        uc.DarkProc.summary(self)
        if self.plotim: self.show_plot_results()
        if self.savebw: self.save_results(evt, env)

    def save_results(self, evt, env):
        det = self.det
        savebw = self.savebw
        ofname = self.ofname
        src = self.src
        counter = self.counter
        verbos = 0o177777
        addmetad = True

        exp = self.expname if self.expname is not None else env.experiment()

        #cmod = self._common_mode_pars(arr_av1, arr_rms, arr_msk)
        cmts = ['DATASET  %s' % self.dsname, 'STATISTICS  %d' % counter]

        # Save n-d array in text file %
        template = fname_template(evt, exp, src, ofname, counter)

        if savebw &  1: det.save_asdaq(template % 'ave', self.arr_av1, cmts + ['ARR_TYPE  average'], '%8.2f', verbos, addmetad)
        if savebw &  2: det.save_asdaq(template % 'rms', self.arr_rms, cmts + ['ARR_TYPE  RMS'],     '%8.2f', verbos, addmetad)
        if savebw &  4: det.save_asdaq(template % 'sta', self.arr_sta, cmts + ['ARR_TYPE  status'],  '%d',    verbos, addmetad)
        if savebw &  8: det.save_asdaq(template % 'msk', self.arr_msk, cmts + ['ARR_TYPE  mask'],    '%1d',   verbos, addmetad)
        if savebw & 16: det.save_asdaq(template % 'max', self.arr_max, cmts + ['ARR_TYPE  max'],     '%d',    verbos, addmetad)
        if savebw & 32: det.save_asdaq(template % 'min', self.arr_min, cmts + ['ARR_TYPE  min'],     '%d',    verbos, addmetad)
        #if savebw & 64 and cmod is not None:
        #    np.savetxt(template % 'cmo', cmod, fmt='%d', delimiter=' ', newline=' ')
        #    det.save_asdaq(template % 'cmm', cmod, cmts + ['ARR_TYPE  common_mode'],'%d', verbos, False)

def det_ndarr_raw_proc(**kwa):

    evskip = kwa['evskip']
    events = kwa['events']
    dsname = kwa['dsname']
    evcode = kwa['evcode']
    verbos = kwa['verbos']
    source = kwa['source']
    plotim = kwa['plotim']

    t0_sec = time()
    tdt = t0_sec

    # Non-standard calib directory
    #psana.setOption('psana.calib-dir', './calib')

    SKIP   = evskip
    EVENTS = events + SKIP

    logger.info('Raw data processing of dataset: %s' % (dsname))

    ecm = False
    if evcode is not None:
        from Detector.EventCodeManager import EventCodeManager
        ecm = EventCodeManager(evcode, verbos)
        logger.info('requested event-code list %s' % str(ecm.event_code_list()))

    # rename parameters to use in class DarkProc
    kwa['int_lo'] = kwa['intlow']
    kwa['int_hi'] = kwa['inthig']
    kwa['rms_lo'] = kwa['rmslow']
    kwa['rms_hi'] = kwa['rmshig']

    lst_dpo = [DarkProcDet(src, **kwa) for src in source.split(',')]

    ds  = psana.DataSource(dsname)
    env = ds.env()

    for i, evt in enumerate(ds.events()):
        if i<SKIP:
            logger.debug('==== Ev:%04d is skipped --evskip=%d' % (ievt,evskip))
            continue
        elif SKIP>0 and (i == SKIP):
            s = 'Events < --evskip=%d are skipped' % SKIP
            #print(s)
            logger.info(s)

        if not i<EVENTS:
            logger.info('\n==== Ev:%04d event loop is terminated --events=%d' % (i,EVENTS))
            break

        if ecm and not ecm.select(evt):
            logger.debug('==== Ev:%04d is skipped due to selection code' % i)
            continue

        status = None
        for dpo in lst_dpo:
            status = dpo.event(evt, env, i)

        if selected_record(i):
            tsec = time()
            dt   = tsec - tdt
            tdt  = tsec
            logger.info('  Event: %4d,  time=%7.3f sec,  dt=%5.3f sec' % (i, time()-t0_sec, dt))

        if status == 2: break

    for dpo in lst_dpo: dpo.summary(evt, env)

    logger.info('%s\nTotal consumed time = %f sec.' % (80*'_', time()-t0_sec))

# EOF
