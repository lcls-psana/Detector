
""" UtilsRawPixelStatus.py - utilities for command det_raw_pixel_status

    import Detector.UtilsRawPixelStatus as us

    us.save_constants_in_repository(arr, **kwargs) # saves user's array of constants in reppository defined bu **kwargs
"""

from time import time
import os
import sys
import numpy as np

import Detector.UtilsLogging as ul
logger = ul.logging.getLogger(__name__)  # where __name__ = 'Detector.UtilsRawPixelStatus'
from psana import DataSource, Detector
from Detector.GlobalUtils import info_ndarr  # print_ndarr, divide_protected
import PSCalib.GlobalUtils as gu
import Detector.UtilsCalib as uc
import Detector.RepoManager as rm


def metadata(ds, orun, det):
    """ returns (dict) metadata evaluated from input objects"""
    import Detector.UtilsDeployConstants as udc
    env = ds.env()
    dettype = det.pyda.dettype
    ts_run, ts_now = uc.tstamps_run_and_now(env, fmt=uc.TSTAMP_FORMAT)
    #print('\nXXX dir(env)', dir(env))
    runnum = orun.run()
    return {
      'dettype': dettype,
      'typename': gu.dic_det_type_to_name.get(dettype, None).lower(),
      'detid': udc.id_det(det, env),
      'detname': det.name,
      'ts_run': ts_run,
      'ts_now': ts_now,
      'expname': env.experiment(),
      'calibdir': env.calibDir(),
      'runnum': runnum,
      'pedestals': det.pedestals(runnum),
      'rms': det.rms(runnum),
      }


def fplane(x, y, p):
    return x*p[0] + y*p[1] + p[2]


def fit_to_plane(xs, ys, zs):
    """xs, ys, zs - np.arrays (OF THE SAME SIZE) of (x,y) points and value z.
       Input coordinates xs, ys are not necessarily on grid.
    """
    assert isinstance(xs, np.ndarray)
    assert isinstance(ys, np.ndarray)
    assert isinstance(zs, np.ndarray)
    A = np.matrix([[x, y, 1] for x,y in zip(xs.ravel(), ys.ravel())])
    b = np.matrix([z for z in zs.ravel()]).T
    pars = (A.T * A).I * A.T * b
    resids = b - A * pars
    pars = [p[0] for p in pars.tolist()]  # np.matrix -> list
    resids = np.array([r[0] for r in resids.tolist()])
    return pars, resids


def residuals_to_plane(a):
    """use a.shape to make a grid, fit array to plane on grid, find and return residuals.
    """
    assert isinstance(a, np.ndarray)
    sh = a.shape
    cs, rs = np.meshgrid(range(sh[1]), range(sh[0]))
    logger.debug('in residuals_to_plane input to fit_to_plane:\n  %s\n  %s\n  %s'%\
                 (info_ndarr(a,  '   arr '),
                  info_ndarr(cs, '   cols'),
                  info_ndarr(rs, '   rows')))
    _, res = fit_to_plane(cs, rs, a)
    res.shape = sh
    return res


def find_outliers(arr, title='', vmin=None, vmax=None):
    assert isinstance(arr, np.ndarray)
    size = arr.size
    arr0 = np.zeros_like(arr, dtype=bool)
    arr1 = np.ones_like(arr, dtype=np.uint64)
    bad_lo = arr0 if vmin is None else arr <= vmin
    bad_hi = arr0 if vmax is None else arr >= vmax
    arr1_lo = np.select((bad_lo,), (arr1,), 0)
    arr1_hi = np.select((bad_hi,), (arr1,), 0)
    sum_lo = arr1_lo.sum()
    sum_hi = arr1_hi.sum()
    s_lo = '%8d / %d (%6.3f%%) pixels %s <= %s'%\
            (sum_lo, size, 100*sum_lo/size, title, 'unlimited' if vmin is None else '%.3f' % vmin)
    s_hi = '%8d / %d (%6.3f%%) pixels %s >= %s'%\
            (sum_hi, size, 100*sum_hi/size, title, 'unlimited' if vmax is None else '%.3f' % vmax)
    return bad_lo, bad_hi, arr1_lo, arr1_hi, s_lo, s_hi


def evaluate_pixel_status(arr, title='', vmin=None, vmax=None, snrmax=8):
    """vmin/vmax - absolutly allowed min/max of the value
    """
    assert isinstance(arr, np.ndarray)
    bad_lo, bad_hi, arr1_lo, arr1_hi, s_lo, s_hi = find_outliers(arr, title=title, vmin=vmin, vmax=vmax)

    arr_sel = arr[np.logical_not(np.logical_or(bad_lo, bad_hi))]
    med = np.median(arr_sel)
    spr = np.median(np.absolute(arr_sel-med))  # axis=None, out=None, overwrite_input=False, keepdims=False
    if spr == 0:
       spr = np.std(arr_sel)
       logger.warning('MEDIAN OF SPREAD FOR INT VALUES IS 0 replaced with STD = % .3f' % spr)

    _vmin = med - snrmax*spr if vmin is None else max(med - snrmax*spr, vmin)
    _vmax = med + snrmax*spr if vmax is None else min(med + snrmax*spr, vmax)

    s_sel = '%s selected %d of %d pixels in' % (title, arr_sel.size, arr.size)\
          + ' range (%s, %s)' % (str(vmin), str(vmax))\
          + ' med: %.3f spr: %.3f' % (med, spr)

    s_range = u're-defined range for med \u00B1 %.1f*spr: (%.3f, %.3f)' % (snrmax, _vmin, _vmax)
    _, _, _arr1_lo, _arr1_hi, _s_lo, _s_hi = find_outliers(arr, title=title, vmin=_vmin, vmax=_vmax)

    gap = 13*' '
    logger.info('%s\n    %s\n  %s\n  %s\n%s%s\n%s%s\n  %s\n  %s' %\
        (20*'=', info_ndarr(arr, title, last=0), s_lo, s_hi, gap, s_sel, gap, s_range, _s_lo, _s_hi))

    return _arr1_lo, _arr1_hi, _s_lo, _s_hi


def set_pixel_status_bits(status, arr, title='', vmin=None, vmax=None, snrmax=8, bit_lo=1<<0, bit_hi=1<<1):
    assert isinstance(arr, np.ndarray)
    arr1_lo, arr1_hi, s_lo, s_hi = evaluate_pixel_status(arr, title=title, vmin=vmin, vmax=vmax, snrmax=snrmax)
    status += arr1_lo * bit_lo
    status += arr1_hi * bit_hi
    s_lo = '%20s: %s' % (oct(bit_lo), s_lo)
    s_hi = '%20s: %s' % (oct(bit_hi), s_hi)
    return s_lo, s_hi


def edges1d(size, step):
    """returns (list) [0, step, 2*step, ..., (size-step)]"""
    assert isinstance(size, int)
    assert isinstance(step, int)
    assert size>step
    es = list(range(0, size, step))
    if es[-1] > (size-step): es[-1] = size-step
    return es


def corners2d(shf, shw):
    """returns list of 2-d corner indices [(r0,c0), (r0,c1), ...]
       parameters: 2-d shape of the frame and 2-d shape of the window
    """
    assert len(shf) == 2
    assert len(shw) == 2
    rows = edges1d(shf[0], shw[0])
    cols = edges1d(shf[1], shw[1])
    cs, rs = np.meshgrid(cols, rows)
    return list(zip(rs.ravel(), cs.ravel()))


def selected_number(n):
    return n<5\
       or (n<50 and not n%10)\
       or (n<500 and not n%100)\
       or (not n%1000)


class DataProc:
    """data accumulation and processing"""
    def __init__(self, args, metad, **kwa):
        self.args = args
        self.kwa = kwa
        self.aslice = eval('np.s_[%s]' % args.slice)
        self.segind = args.segind
        self.nrecs  = args.nrecs
        self.snrmax  = args.snrmax
        self.gainbits = args.gainbits
        self.databits = args.databits
        self.irec   = -1
        self.status = 0
        self.shwind = eval('(%s)' % args.shwind)
        self.block  = None
        self.features = eval('(%s)' % args.features)
        self.metad = metad
        self.fname = fname_block(args, metad)
        logger.info('file name for data block: %s' % self.fname)


    def init_block(self, raw):
        self.shape_fr = tuple(raw.shape)
        self.shape_bl = (self.nrecs,) + self.shape_fr
        self.load_data_file()
        if self.block is not None: return
        self.block = np.zeros(self.shape_bl, dtype=raw.dtype)
        logger.info(info_ndarr(self.block, 'created empty data block'))
        self.irec = -1
        self.status = 0


    def add_record(self, raw):
        self.block[self.irec,:] = raw


    def feature_01(self):
        logger.info("""Feature 1: mean intensity of frames""")
        block_data = self.block & self.databits
        intensity_mean = np.sum(block_data, axis=(-2,-1)) / self.ssize
        logger.info(info_ndarr(intensity_mean, '\n  per-record intensity MEAN IN FRAME:', last=20))

        intensity_med = np.median(block_data, axis=(-2,-1))
        logger.info(info_ndarr(intensity_med, '\n  per-record intensity MEDIAN IN FRAME:', last=20))
        arr1_lo, arr1_hi, s_lo, s_hi = evaluate_pixel_status(intensity_med, title='Feat.1: intensity_med',\
                                             vmin=0, vmax=self.databits, snrmax=self.snrmax)
        arr0 = np.zeros_like(arr1_lo, dtype=np.uint64)  # dtype=bool
        arr1_good_frames = np.select((arr1_lo>0, arr1_hi>0), (arr0, arr0), 1)
        logger.info('Total number of good events: %d' % arr1_good_frames.sum())
        return arr1_good_frames


    def feature_02(self):
        logger.info("""Feature 2: dark mean in good range""")
        block_good = self.block[self.bool_good_frames,:] & self.databits
        logger.info(info_ndarr(block_good, 'block of good records:', last=5))
        return np.mean(block_good, axis=0, dtype=np.float)


    def feature_03(self):
        logger.info("""Feature 3: dark RMS in good range""")
        block_good = self.block[self.bool_good_frames,:] & self.databits
        logger.info(info_ndarr(block_good, 'block of good records:', last=5))
        return np.std(block_good, axis=0, dtype=np.float)


    def feature_04(self):
        logger.info("""Feature 4: TBD""")
        return None


    def feature_05(self):
        logger.info("""Feature 5: TBD""")
        return None


    def feature_06(self):
        logger.info("""Feature 6: average SNR of pixels over time""")

        ngframes = self.inds_good_frames.size
        shape_res = (ngframes,) + self.shape_fr
        block_res = np.zeros(shape_res, dtype=np.float)

        for i, igood in enumerate(self.inds_good_frames):
            frame = self.block[igood,:] & self.databits
            logger.debug(info_ndarr(frame, '%04d frame data' % igood))
            block_res[i,:] = res = self.residuals_frame_f06(frame) #  self.block[0,:])

            res_med = np.median(res)
            res_spr = np.median(np.absolute(res - res_med))

            s = 'frame: %04d res_med: %.3f res_spr: %.3f frame residuals' % (igood, res_med, res_spr)
            logger.info(info_ndarr(res, s, last=3))

        return block_res


    def feature_11(self):
        logger.info("""Feature 11: Chuck's aftifact catcher""")
        #block_good = self.block[self.bool_good_frames,:] & self.databits
        block_data = self.block & self.databits
        logger.info(info_ndarr(block_data, 'block of data records:', last=5))
        peds = self.metad['pedestals']
        logger.info(info_ndarr(peds, 'pedestals:', last=5))
        std = np.std(block_data, axis=0, dtype=np.float)
        arr = np.mean(block_data, axis=0, dtype=np.float) - peds
        med = np.median(block_data, axis=0) - peds

        np.save('blk_std.npy', std)
        np.save('blk_mean.npy', arr)
        np.save('blk_med.npy', med)
        logger.info('Saved files blk_*.npy')

        return arr


    def residuals_frame_f06(self, frame):
        assert isinstance(frame, np.ndarray)
        assert frame.ndim==2
        corners = corners2d(frame.shape, self.shwind)
        logger.debug('Feature 6: in frame %s window %s corners:\n %s\nNumber of corners: %d'%\
                     (str(frame.shape), str(self.shwind), str(corners), len(corners)))

        residuals = np.zeros_like(frame, dtype=np.float)
        wr, wc = self.shwind
        for r,c in corners: # evaluate residuals to the plane fit in frame windows
            sl = np.s_[r:r+wr, c:c+wc]
            arrw = frame[sl]
            res = residuals_to_plane(arrw)
            res_med = np.median(res)
            res_spr = np.median(np.absolute(res - res_med))
            residuals[sl] = res
            logger.debug('  corner r: %d c:%d %s\n   residuals med: %.3f spr: %.3f'%\
                         (r, c, info_ndarr(res, 'residuals'), res_med, res_spr))
        return residuals


    def summary(self):
        logger.info(info_ndarr(self.block, '\nSummary for data block:'))
        #logger.info('%s\nraw data found/selected in %d events' % (80*'_', self.irec+1))
        self.block = self.block[:self.irec,:]
        logger.info(info_ndarr(self.block, 'block of all records:', last=5))
        bsh = self.block.shape
        self.ssize = bsh[-1]*bsh[-2]

        if 1 in self.features:
            arr1_good_frames = self.feature_01()
            logger.info(info_ndarr(arr1_good_frames, 'arr1_good_frames:'))
            self.bool_good_frames = arr1_good_frames>0
            self.inds_good_frames = np.where(self.bool_good_frames)[0] # array if indices for good frames
            logger.info('%s\n%s' % (info_ndarr(self.inds_good_frames, 'inds_good_frames:', last=0),\
                    str(self.inds_good_frames)))
        else:
            logger.info('Feature 1 for mean intensity of frames is not requested. All frames are used for further processing.')
            self.inds_good_frames = np.arange(self.irec, dtype=np.uint)
            self.bool_good_frames = np.ones(self.irec, dtype=np.bool)

        arr_sta = np.zeros(self.shape_fr, dtype=np.uint64)

        f = '\n  %s\n  %s'
        ss = '\n\nSummary of the bad pixel status evaluation for SNR=%.2f, %s array' % (self.snrmax, self.args.ctype)

        if 2 in self.features:
            arr_mean = self.feature_02()
            logger.info(info_ndarr(arr_mean, 'median over good records:', last=5))
            ss += f % set_pixel_status_bits(arr_sta, arr_mean, title='Feat.2 mean', vmin=0, vmax=self.databits,
                                            snrmax=self.snrmax, bit_lo=1<<0, bit_hi=1<<1)

        if 3 in self.features:
            arr_std = self.feature_03()
            logger.info(info_ndarr(arr_std, 'std over good records:', last=5))
            ss += f % set_pixel_status_bits(arr_sta, arr_std, title='Feat.3 std', vmin=0, vmax=self.databits,
                                            snrmax=self.snrmax, bit_lo=1<<2, bit_hi=1<<3)

        if 4 in self.features:
            arr = self.feature_04()

        if 5 in self.features:
            arr = self.feature_05()

        if 6 in self.features:
            block_res = self.feature_06()

            res_med = np.median(block_res, axis=0)
            res_spr = np.median(np.absolute(block_res - res_med), axis=0)

            logger.info(info_ndarr(block_res, 'block of residuals:', last=20))
            logger.info(info_ndarr(res_med, 'median over frames per-pixel residuals:', last=20))
            logger.info(info_ndarr(res_spr, 'median over frames per-pixel spread of res:', last=20))

            ss += f % set_pixel_status_bits(arr_sta, res_med, title='Feat.6 res_med', vmin=-self.databits, vmax=self.databits,
                                            snrmax=self.snrmax, bit_lo=1<<4, bit_hi=1<<5)
            ss += f % set_pixel_status_bits(arr_sta, res_spr, title='Feat.6 res_spr', vmin=-self.databits, vmax=self.databits,\
                                            snrmax=self.snrmax, bit_lo=1<<6, bit_hi=1<<7)
        if 11 in self.features:
            arr = self.feature_11()

        arr1 = np.ones(self.shape_fr, dtype=np.uint64)
        stus_bad_total = np.select((arr_sta>0,), (arr1,), 0)
        num_bad_pixels = stus_bad_total.sum()

        size = arr_sta.size
        ss += '\n    Any bad status bit: %8d / %d (%6.3f%%) pixels' % (num_bad_pixels, size, 100*num_bad_pixels/size)
        logger.info(ss)

        return arr_sta
        #sys.exit('TEST EXIT')


    def event(self, raw, evnum):
        logger.debug(info_ndarr(raw, 'event %d raw:' % evnum))

        if raw is None: return self.status

        ndim = raw.ndim
        assert ndim > 1, 'raw.ndim: %d' % ndim
        assert ndim < 4, 'raw.ndim: %d' % ndim
        #if ndim >3: raw = gu.reshape_to_3d(raw)

        _raw = raw[self.aslice] if ndim==2 else\
               raw[self.segind,:][self.aslice]

        if self.block is None:
            self.init_block(_raw)

        self.irec +=1
        if self.irec < self.nrecs:
            self.add_record(_raw)

        else:
            logger.info('nevt:%d accumulated requested number of records --nrecs: %d - break' % (evnum, self.irec))
            #self.summary()
            self.status = 1

        return self.status


    def load_data_file(self):
        fname = self.fname
        if fname is None: return
        if not os.path.exists(fname): return
        self.block = np.load(fname)
        logger.warning('DATA BLOCK IS LOADED FROM FILE: %s' % fname)
        logger.info(info_ndarr(self.block, 'loaded data block'))
        self.irec = self.block.shape[0] # - 2
        #self.status = 1


    def save_data_file(self):
        fname = self.fname
        s = ''
        if fname is None:
           s = 'file name for data block is not defined\n    DO NOT SAVE'
        elif os.path.exists(fname):
           s = 'EXISTING FILE %s\n    DO NOT SAVE' % fname
        elif self.block is None:
           s = 'data block is None\n    DO NOT SAVE'
        else:
           np.save(fname, self.block)
           s = info_ndarr(self.block, 'data block') + '\n    saved in %s' % fname
        logger.info(s)


def fname_block(args, metad):
    detname = args.source.replace(':','-').replace('.','-')
    sslice = str(args.slice).replace(':','-').replace(',','_')
    return 'blk-%s-r%04d-%s-seg%s-nrecs%04d-slice%s.npy' % (metad['expname'], metad['runnum'],\
             detname, args.segind, min(args.events, args.nrecs), sslice)


def event_loop(parser):

    args = parser.parse_args() # namespace # kwargs = vars(args) # dict
    logger.debug('Arguments: %s\n' % str(args))

    dsname  = args.dsname
    detname = args.source
    events  = args.events
    evskip  = args.evskip
    steps   = args.steps
    stskip  = args.stskip
    evcode  = args.evcode
    segind  = args.segind
    logmode = args.logmode
    aslice  = eval('np.s_[%s]' % args.slice)
    repoman = args.repoman = rm.init_repoman_and_logger(args, parser)

    t0_sec = time()

    ds  = DataSource(dsname)
    det = Detector(detname)
    #cd  = Detector('ControlData')

    ecm = False
    if evcode is not None:
        from Detector.EventCodeManager import EventCodeManager
        ecm = EventCodeManager(evcode, verbos=0)
        logger.info('requested event-code list %s' % str(ecm.event_code_list()))

    nrun_tot  = 0
    nstep_tot = 0
    nevt_tot  = 0
    metad = None
    kwa_dpo = {}
    dpo = None

    for orun in ds.runs():
      nrun_tot += 1
      if metad is None:
         metad = metadata(ds, orun, det)
         logger.info(' '.join(['\n%s: %s'%(k.ljust(10), str(v)) for k, v in metad.items()]))

         peds = metad['pedestals']
         rms  = metad['rms']
         logger.info(info_ndarr(peds, 'pedestals:', last=5))
         logger.info(info_ndarr(rms, 'rms:', last=5))
         np.save('cc_peds.npy', peds)
         np.save('cc_rms.npy', rms)

         dpo = DataProc(args, metad, **kwa_dpo)

      logger.info('==== run %s' % str(orun.run()))

      break_runs = False

      for nstep_run, step in enumerate(orun.steps()):
        nstep_tot += 1
        logger.info('  == calibcycle %02d ==' % nstep_tot)

        if steps is not None and nstep_tot >= steps:
            logger.info('nstep_tot:%d >= number of steps:%d - break' % (nstep_tot, steps))
            break

        elif stskip is not None and nstep < stskip:
            logger.info('nstep:%d < number of steps to skip:%d - continue' % (nstep, stskip))
            continue

        break_steps = False

        for nevt, evt in enumerate(step.events()):

            nevt_tot += 1
            raw = det.raw(evt)

            if raw is None: #skip empty frames
                logger.info('Ev:%04d rec:%04d raw=None' % (nevt, dpo.irec))
                continue

            if evskip is not None and nevt < evskip:
                logger.info('nevt:%d < number of events in cc to skip --evskip:%d - continue' % (nevt_tot, evskip))
                continue

            if selected_number(nevt):
                logger.info(info_ndarr(raw, 'Ev:%04d rec:%04d raw' % (nevt_tot, dpo.irec)))

            if ecm and not ecm.select(evt):
                logger.debug('==== Ev:%04d is skipped due to event code selection - continue' % nevt_tot)
                continue

            resp = dpo.event(raw, nevt_tot)

            if resp == 1:
                break_steps = True
                break_runs = True
                logger.info('BREAK EVENTS')
                break

            if events is not None and nevt >= events:
                logger.info('BREAK EVENTS nevt:%d >= number of events in cc to collect --events:%d' % (nevt_tot, events))
                break_steps = True
                break_runs = True
                break

        if break_steps:
            logger.info('BREAK STEPS')
            break

      if break_runs:
          logger.info('BREAK RUNS')
          break

    arr_status = dpo.summary()
    save_constants(arr_status, args, metad)

    dpo.save_data_file()

    logger.info('Consumed time %.3f sec' % (time()-t0_sec))
    repoman.logfile_save()


def save_constants(arr_status, args, dmd):
    fmt        = '%d'
    runnum     = dmd['runnum']
    itype      = dmd['dettype']
    typename   = dmd['typename']
    expname    = dmd['expname']
    ts_run     = dmd['ts_run']
    panel_ids  = dmd['detid'].split('_')
    detname    = dmd['detname']
    ctype      = args.ctype # 'status_data'
    dirrepo    = args.dirrepo
    filemode   = args.filemode
    group      = args.group
    is_slice   = args.slice != '0:,0:'
    segind     = args.segind
    gmode      = args.gmode
    panel_id   = panel_ids[segind]
    repoman    = args.repoman
    #source     = args.source # detname
    #dirdettype = repoman.makedir_dettype(dettype=typename)
    fname_aliases = repoman.fname_aliases(dettype=typename) # , fname='.aliases_%s.txt' % typename)
    dirpanel   = repoman.dir_panel(panel_id)
    fname_prefix, panel_alias = uc.file_name_prefix(typename, panel_id, ts_run, expname, runnum, fname_aliases, **{'detname':str(detname)})
    logger.debug('panel index: %02d alias: %s dir: %s\n  fname_prefix: %s' % (segind, panel_alias, dirpanel, fname_prefix))
    dirname = repoman.makedir_ctype(panel_id, ctype)
    fname = '%s/%s_%s' % (dirname, fname_prefix, ctype)
    if gmode is not None: fname += '_%s' % gmode
    if is_slice: fname += '_slice'
    fname += '.dat'
    uc.save_2darray_in_textfile(arr_status, fname, filemode, fmt, umask=0o0, group=group)


class Empty:
    """reserved for name sapace"""
    pass


def save_constants_in_repository(arr, **kwa):
    """User's interface method to save any constants in repository.

    PARAMETERS of **kwa
    -------------------

    dsname (str) - parameter for DataSource
    detname (str) - detector name
    ctype (str) - calibration constants type, ex. pedestals, gain, offset, status_user, etc.
    dirrepo (str) - root level of repository
    segind (int) - segment index for multipanel detectors
    gmodes (tuple) - gain mode names, ex. for epix10ka ('FH', 'FM', 'FL', 'AHL-H','AML-H', 'AHL-L','AML-L')
    slice (str) - numpy style af array sloce for debugging
    """
    logger.debug('kwargs: %s' % str(kwa))
    from Detector.dir_root import DIR_REPO_STATUS, DIR_LOG_AT_START # os, DIR_ROOT
    #import Detector.UtilsEpix10ka as ue

    args = Empty()
    args.dsname   = kwa.get('dsname', None) # 'exp=xpplw3319:run=293'
    args.detname  = kwa.get('detname', None) # 'XppGon.0:Epix100a.3' or its alias 'epix_alc3'
    args.ctype    = kwa.get('ctype', 'status_user')
    args.dirrepo  = kwa.get('dirrepo', DIR_REPO_STATUS)
    args.filemode = kwa.get('filemode', 0o664)
    args.dirmode  = kwa.get('filemode', 0o2775)
    args.group    = kwa.get('group', 'ps-users')
    args.segind   = kwa.get('segind', 0)
    args.gmodes   = kwa.get('gmodes', None)
    args.slice    = kwa.get('slice', '0:,0:')
    args.repoman = rm.RepoManager(dirrepo=args.dirrepo, dir_log_at_start=DIR_LOG_AT_START,\
                                  dirmode=args.dirmode, filemode=args.filemode, group=args.group)
    args.gmode    = None

    ndim = arr.ndim
    shape = arr.shape

    assert isinstance(arr, np.ndarray)
    assert ndim >= 2
    assert ndim <= 4
    assert args.dsname is not None
    assert args.detname is not None

    ds  = DataSource(args.dsname)
    det = Detector(args.detname)
    args.detname = det.name
    orun = next(ds.runs())
    metad = metadata(ds, orun, det)
    logger.info(' '.join(['\n%s: %s'%(k.ljust(10), str(v)) for k, v in metad.items()]))
    panel_ids = metad['detid'].split('_')
    nsegs = len(panel_ids)

    if ndim == 2:
        save_constants(arr, args, metad)

    elif ndim == 3:
        assert arr.shape[0] == nsegs, 'number of segments in the array shape %s should be the same as in metadata %s' % (str(shape), nsegs)
        for i in range(nsegs):
            args.segind = i
            save_constants(arr[i,:], args, metad)

    elif ndim == 4:
        assert isinstance(args.gmodes, tuple),\
            'gain mode names should be defined in tuple, gmodes=%s' % str(args.gmodes)
        assert arr.shape[0] == len(args.gmodes),\
            'number of gain modes in the array shape %s should be the same as in tuple gmodes %s' % (str(shape), str(args.gmodes))
        assert arr.shape[1] == nsegs,\
            'number of segments in the array shape %s should be the same as in metadata %s' % (str(shape), nsegs)
        for n, gm in enumerate(args.gmodes):
          for i in range(nsegs):
            args.segind = i
            args.gmode = gm
            save_constants(arr[n,i,:], args, metad)


det_raw_pixel_status = event_loop
#def det_raw_pixel_status(parser): event_loop(parser)

# EOF
