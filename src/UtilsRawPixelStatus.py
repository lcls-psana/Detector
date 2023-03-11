
"""UtilsRawPixelStatus.py - utilities for command det_raw_pixel_status

Test data sample with command like
    datinfo -e xpplw3319 -r 293 -d epix_alc3
"""

from time import time
import sys
import Detector.UtilsLogging as ul
logger = ul.logging.getLogger(__name__)  # where __name__ = 'Detector.UtilsRawPixelStatus'
from psana import DataSource, Detector
from Detector.GlobalUtils import info_ndarr  # print_ndarr, divide_protected
import PSCalib.GlobalUtils as gu
import Detector.UtilsCalib as uc

import numpy as np


def metadata(ds, orun, det):
    """ returns (dict) metadata evaluated from input objects"""
    import Detector.UtilsDeployConstants as udc
    env = ds.env()
    dettype = det.pyda.dettype
    ts_run, ts_now = uc.tstamps_run_and_now(env, fmt=uc.TSTAMP_FORMAT)
    #print('\nXXX dir(env)', dir(env))
    return {
      'dettype': dettype,
      'typename': gu.dic_det_type_to_name.get(dettype, None).lower(),
      'detid': udc.id_det(det, env),
      'ts_run': ts_run,
      'ts_now': ts_now,
      'expname': env.experiment(),
      'calibdir': env.calibDir(),
      'runnum': orun.run()
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


def evaluate_pixel_status(arr, title='', vmin=None, vmax=None, snrmax=8, prefix=''):
    """vmin/vmax - absolutly allowed min/max of the value
    """
    assert isinstance(arr, np.ndarray)
    bad_lo, bad_hi, arr1_lo, arr1_hi, s_lo, s_hi = find_outliers(arr, title=title, vmin=vmin, vmax=vmax)

    arr_sel = arr[np.logical_not(np.logical_or(bad_lo, bad_hi))]
    med = np.median(arr_sel)
    spr = np.median(np.absolute(arr_sel-med))  # axis=None, out=None, overwrite_input=False, keepdims=False
    if spr == 0:
       spr = np.std(arr_sel)/4
       logger.warning('MEDIAN OF SPREAD FOR INT VALUES IS 0 replaced with STD/4 = % .3f' % spr)

    _vmin = med - snrmax*spr if vmin is None else max(med - snrmax*spr, vmin)
    _vmax = med + snrmax*spr if vmax is None else min(med + snrmax*spr, vmax)

    #if prefix: plot_array(arr, title=title, vmin=_vmin, vmax=_vmax, prefix=prefix)

    s_sel = '%s selected %d of %d pixels in' % (title, arr_sel.size, arr.size)\
          + ' range (%s, %s)' % (str(vmin), str(vmax))\
          + ' med: %.3f spr: %.3f' % (med, spr)

    s_range = u're-defined range for med \u00B1 %.1f*spr: (%.3f, %.3f)' % (snrmax, _vmin, _vmax)
    _, _, _arr1_lo, _arr1_hi, _s_lo, _s_hi = find_outliers(arr, title=title, vmin=_vmin, vmax=_vmax)

    gap = 13*' '
    logger.info('%s\n    %s\n  %s\n  %s\n%s%s\n%s%s\n  %s\n  %s' %\
        (20*'=', info_ndarr(arr, title, last=0), s_lo, s_hi, gap, s_sel, gap, s_range, _s_lo, _s_hi))

    return _arr1_lo, _arr1_hi, _s_lo, _s_hi


def set_pixel_status_bits(status, arr, title='', vmin=None, vmax=None, snrmax=8, bit_lo=1<<0, bit_hi=1<<1, prefix=''):
    assert isinstance(arr, np.ndarray)
    arr1_lo, arr1_hi, s_lo, s_hi = evaluate_pixel_status(arr, title=title, vmin=vmin, vmax=vmax, snrmax=snrmax, prefix=prefix)
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
    def __init__(self, args, **kwa):
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


    def init_block(self, raw):
        self.shape_fr = tuple(raw.shape)
        self.shape_bl = (self.nrecs,) + self.shape_fr
        self.block = np.zeros(self.shape_bl, dtype=raw.dtype)
        logger.info(info_ndarr(self.block, 'created empty data block'))
        self.irec = -1
        self.status = 0


    def add_record(self, raw):
        self.block[self.irec,:] = raw


    def feature_01(self):
        """Feature 1: mean intensity of frames"""
        block_data = self.block & self.databits
        intensity_mean = np.sum(block_data, axis=(-2,-1)) / self.ssize
        logger.info(info_ndarr(intensity_mean, '\n  per-record intensity MEAN IN FRAME:', last=20))

        intensity_med = np.median(block_data, axis=(-2,-1))
        logger.info(info_ndarr(intensity_med, '\n  per-record intensity MEDIAN IN FRAME:', last=20))
        arr1_lo, arr1_hi, s_lo, s_hi = evaluate_pixel_status(intensity_med, title='Feat.1: intensity_med', vmin=0, vmax=self.databits, snrmax=self.snrmax, prefix='')
        arr0 = np.zeros_like(arr1_lo, dtype=np.uint64)  # dtype=bool
        arr1_good_frames = np.select((arr1_lo>0, arr1_hi>0), (arr0, arr0), 1)
        logger.info('Total number of good events: %d' % arr1_good_frames.sum())
        return arr1_good_frames


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


    def feature_06(self):
        """Feature 6: average SNR of pixels over time"""

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


    def summary(self):
        logger.info(info_ndarr(self.block, '\nSummary for data block:'))
        #logger.info('%s\nraw data found/selected in %d events' % (80*'_', self.irec+1))

        bsh = self.block.shape
        self.ssize = bsh[-1]*bsh[-2]

        arr1_good_frames = self.feature_01()
        logger.info(info_ndarr(arr1_good_frames, 'arr1_good_frames:'))
        self.inds_good_frames = np.where(arr1_good_frames>0)[0] # array if indices for good frames
        logger.info('%s\n%s' % (info_ndarr(self.inds_good_frames, 'inds_good_frames:', last=0),\
                    str(self.inds_good_frames)))

        block_res = self.feature_06()

        res_med = np.median(block_res, axis=0)
        res_spr = np.median(np.absolute(block_res - res_med), axis=0)

        logger.info(info_ndarr(block_res, 'block of residuals:', last=20))
        logger.info(info_ndarr(res_med, 'median over frames per-pixel residuals:', last=20))
        logger.info(info_ndarr(res_spr, 'median over frames per-pixel spread of res:', last=20))

        prefix = 'prefix'

        arr_sta = np.zeros(self.shape_fr, dtype=np.uint64)
        f = '\n  %s\n  %s'
        s = '\n\nSummary of the bad pixel status evaluation, %s array' % self.args.ctype
        s += f % set_pixel_status_bits(arr_sta, res_med, title='Feat.6 res_med', vmin=-self.databits, vmax=self.databits, snrmax=self.snrmax, bit_lo=1<<0, bit_hi=1<<1, prefix=prefix)
        s += f % set_pixel_status_bits(arr_sta, res_spr, title='Feat.6 res_spr', vmin=-self.databits, vmax=self.databits, snrmax=self.snrmax, bit_lo=1<<2, bit_hi=1<<3, prefix=prefix)

        #stus_bad_total = np.select((arr_sta>0,), (arr1[myslice],), 0)
        arr1 = np.ones(self.shape_fr, dtype=np.uint64)
        stus_bad_total = np.select((arr_sta>0,), (arr1,), 0)
        num_bad_pixels = stus_bad_total.sum()

        size = arr_sta.size
        s += '\n    Any bad status bit: %8d / %d (%6.3f%%) pixels' % (num_bad_pixels, size, 100*num_bad_pixels/size)
        logger.info(s)

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


def event_loop(args):

    dsname = args.dsname
    detname= args.source
    events = args.events
    evskip = args.evskip
    steps  = args.steps
    stskip = args.stskip
    evcode = args.evcode
    segind = args.segind
    aslice = eval('np.s_[%s]' % args.slice)

    t0_sec = time()

    ds  = DataSource(dsname)
    det = Detector(detname)
    cd  = Detector('ControlData')

    ecm = False
    if evcode is not None:
        from Detector.EventCodeManager import EventCodeManager
        ecm = EventCodeManager(evcode, verbos=0)
        logger.info('requested event-code list %s' % str(ecm.event_code_list()))

    kwa_dpo = {}
    dpo = DataProc(args, **kwa_dpo)
    nrun_tot  = 0
    nstep_tot = 0
    nevt_tot  = 0
    metad = None

    #sys.exit('TEST EXIT')

    for orun in ds.runs():
      nrun_tot += 1
      if metad is None:
         metad = metadata(ds, orun, det)
         logger.info(' '.join(['\n%s: %s'%(k.ljust(10), str(v)) for k, v in metad.items()]))

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
    save_status(arr_status, args, metad)

    logger.info('Consumed time %.3f sec' % (time()-t0_sec))


def save_status(arr_status, args, dmd):
    fmt        = '%d'
    runnum     = dmd['runnum']
    itype      = dmd['dettype']
    typename   = dmd['typename']
    expname    = dmd['expname']
    ts_run     = dmd['ts_run']
    panel_ids  = dmd['detid'].split('_')
    ctype      = args.ctype # 'pixel_status_data'
    dirrepo    = args.dirrepo
    filemode   = args.filemode
    group      = args.group
    is_slice   = args.slice != '0:,0:'
    segind     = args.segind
    panel_id   = panel_ids[segind]
    repoman    = args.repoman
    dirdettype = repoman.makedir_dettype(dettype=typename)
    dirpanel   = repoman.dir_panel(panel_id)
    fname_aliases = repoman.fname_aliases(dettype=typename, fname='.aliases_%s.txt' % typename)
    fname_prefix, panel_alias = uc.file_name_prefix(typename, panel_id, ts_run, expname, runnum, fname_aliases)
    logger.debug('panel index: %02d alias: %s dir: %s\n  fname_prefix: %s' % (segind, panel_alias, dirpanel, fname_prefix))
    dirname = repoman.makedir_ctype(panel_id, ctype)
    fname = '%s/%s_%s' % (dirname, fname_prefix, ctype)
    if is_slice: fname += '_slice'
    fname += '.dat'
    uc.save_2darray_in_textfile(arr_status, fname, filemode, fmt, umask=0o0, group=group)


def det_raw_pixel_status(args):
    logger.debug('Arguments: %s\n' % str(args))
    event_loop(args)

# EOF
