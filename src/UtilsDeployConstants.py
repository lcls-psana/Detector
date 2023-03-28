"""
:py:class:`UtilsDeployConstants`
================================

Usage::
    import Detector.UtilsDeployConstants as udc

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2022-06-01 by Mikhail Dubrovin
"""

import os
import psana
import Detector.PyDataAccess as pda
import Detector.UtilsCalib as uc
gu = uc.cgu


import logging
logger = logging.getLogger(__name__)


def detector_name(det):
    """ returns detname like XcsEndstation-0-Epix100a-1
    """
    return gu.string_from_source(det.pyda.source).replace(':','-').replace('.','-')


def id_det(det, env):
    """ returns detector panel id e.g. for epix100a:
        3925999616-0996579585-0553648138-1232098304-1221641739-2650251521-3976200215
    """
    detid = None
    da = det.pyda
    #co = det.pyda.det_config_object(env)
    if da.dettype in (gu.EPIX100A, gu.EPIX10KA):
        co = pda.get_epix_config_object(env, da.source)
        from Detector.UtilsEpix import id_epix
        detid = id_epix(co)
    elif da.dettype in (gu.EPIX10KA2M, gu.EPIX10KAQUAD):
        co = pda.get_epix10ka_any_config_object(env, da.source)
        from Detector.UtilsEpix10ka2M import id_epix10ka2m  # id_epix, id_epix10ka
        detid = id_epix10ka2m(co)
    elif da.dettype == gu.JUNGFRAU:
        co = pda.get_jungfrau_config_object(env, da.source)
        from Detector.UtilsJungfrau import id_jungfrau_from_config
        detid = id_jungfrau_from_config(co)
    else:
        detid = None
    return detid


def detector_id_or_name(det, env):
    detid = id_det(det, env)
    return detector_name(det) if detid is None else detid


def deploy_constants(**kwa):
    exp        = kwa.get('exp', None)
    detname    = kwa.get('det', None)
    run        = kwa.get('run', None)
    runrange   = kwa.get('runrange', '0-end')
    dsnamex    = kwa.get('dsnamex', None)
    tstamp     = kwa.get('tstamp', None)
    dirrepo    = kwa.get('dirrepo', './work')
    dircalib   = kwa.get('dircalib', None)
    ctype      = kwa.get('ctype', 'gain')   # None
    logmode    = kwa.get('logmode', 'DEBUG')
    dirmode    = kwa.get('dirmode',  0o2775)
    filemode   = kwa.get('filemode', 0o664)
    group      = kwa.get('group', 'ps-users')
    deploy     = kwa.get('deploy', False)
    repoman    = kwa.get('repoman', None)
    fname_only = kwa.get('repo_fname_only', False)

    assert ctype is not None, 'calibration type needs to be specified by -C CTYPE or --ctype CTYPE'

    dsn = uc.str_dsname(exp, run, dsnamex)
    logger.debug('dataset_name: %s' % dsn)

    ds = psana.DataSource(dsn)
    env = ds.env()
    irun = next(ds.runs()).run()
    det = psana.Detector(detname, env)

    #co = det.pyda.det_config_object(env)
    #cfg = env.configStore()
    #.deviceID() works for Rayonix
    strsrc = gu.string_from_source(det.source)  # 'MfxEndstation.0:Epix10ka.0'
    dettype_ind = gu.det_type_from_source(det.source)
    dettype = gu.dic_det_type_to_name[dettype_ind].lower()
    logger.debug('dettype index: %d name:%s' % (dettype_ind, dettype))

    detname = detector_name(det)
    logger.debug('detname: %s' % detname)

    detid = id_det(det, env)
    logger.debug('detid: %s' % detid)

    if detid is None: detid = detname

    tsrun, tsnow = uc.tstamps_run_and_now(env, fmt='%Y%m%d%H%M%S') #TSTAMP_FORMAT = '%Y%m%d%H%M%S'
    _tstamp = tsrun if tstamp is None else tstamp
    logger.info('tstamps now: %s run: %s -t or --tstamp: %s search constants for: %s' % (tsnow, tsrun, str(tstamp), _tstamp))

    repoman.makedir_dettype(dettype)  # <repodir>/<dettype>/
    repoman.makedir_default()         # <repodir>/<dettype>/default/
    repoman.makedir_ctypes(detid, ctypes=('gain', 'common_mode', 'geometry'))  # <repodir>/<dettype>/<detid>/<ctype>
    dir_ctype = repoman.dir_ctype(detid, ctype=ctype)

    fname_aliases = repoman.fname_aliases(dettype)  # '<repodir>/<dettype>/.aliases.txt'
    #alias = uc.alias_for_id(detid, fname=fname_aliases, exp=exp, run=irun)  # '0001'
    kwa = {'src':strsrc}
    fname_prefix, alias = uc.file_name_prefix(dettype, detid, _tstamp, exp, irun, fname_aliases, **kwa)
    # 'epix100a_0001_20160318190730_xpptut15_r0260', '0001'

    logger.debug('fname_aliases: %s alias: %s' % (fname_aliases, alias))
    logger.debug('fname_prefix: %s' % fname_prefix)

    if fname_only:
        prefix = fname_prefix if runrange in ('0-end', None) else\
                 uc.file_name_prefix(dettype, detid, _tstamp, exp, int(runrange), fname_aliases, **kwa)[0]
        return '%s/%s_%s.txt' % (dir_ctype, prefix, ctype)

    pattern = '%s_%s' % (dettype, alias) #  ex. 'epix100a_0001'
    fname = uc.find_file_for_timestamp(dir_ctype, pattern, _tstamp)

    logger.info('file_for_timestamp(tstamp=%s): %s' % (_tstamp, fname))
    if fname is None:
        fname = repoman.fname_default(dettype, ctype)  # '<dirrepo>/epix100a/default/epix100a_default_gain.txt'
        logger.info('use default constants from: %s' % fname)

    if not os.path.exists(fname):
        logger.warning('NON EXISTENT file: %s ' % fname)
        return

    logger.debug('standard calib dir: %s' % env.calibDir())       # 'calib/'
    logger.debug('non-default calib dir: %s' % dircalib)
    calibdir = env.calibDir().replace('//','/') if dircalib is None else dircalib  # '/reg/d/psdm/XPP/xpptut15/calib'
    calibgrp = uc.calib_group_for_tname_lower(dettype)           # 'Epix10ka::CalibV1'
    ctypedir = '%s/%s/%s' % (calibdir, calibgrp, strsrc)         # 'calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'
    octype = {'gain':'pixel_gain',
              'rms':'pixel_rms',
              'status':'pixel_status',
              'pixel_gain':'pixel_gain',
              'pixel_rms':'pixel_rms',
              'pixel_status':'pixel_status',
              'common_mode':'common_mode',
              'geometry':'geometry'}[ctype]
    ofname = '%s.data' % runrange
    lfname = None
    logger.info('ready to deploy calib file %s under %s/%s' % (fname, ctypedir, octype))

    if deploy:
        gu.deploy_file(fname, ctypedir, octype, ofname, lfname, verbos=(logmode=='DEBUG'),\
                       filemode=filemode, dirmode=dirmode, group=group)
    else:
        logger.warning('Add option -D to deploy files under directory %s' % ctypedir)


def file_name_in_repo(exp, runnum, detname, ctype, tstamp=None, rundepl=None, dirmode=0o2775, filemode=0o664, group='ps-users'):
    """Usage:
    from Detector.UtilsDeployConstants import file_name_in_repo
    f = file_name_in_repo('xpptut15', 260, 'XcsEndstation.0:Epix100a.1', 'gain', tstamp='20220901120000', rundepl='123')
    """
    from Detector.dir_root import DIR_REPO, DIR_LOG_AT_START
    from Detector.RepoManager import RepoManager
    kwa_rm = {'dirmode':dirmode, 'filemode':filemode, 'group':group, 'dir_log_at_start':DIR_LOG_AT_START}
    kwa = {'exp':exp, 'run':runnum, 'det':detname, 'ctype':ctype, 'tstamp':tstamp, 'runrange':rundepl}
    kwa.update(kwa_rm)
    kwa['repoman'] = RepoManager(DIR_REPO, **kwa_rm)
    kwa['repo_fname_only'] = True
    return deploy_constants(**kwa)


def save_epix100a_ctype_in_repo(arr2d, exp, runnum, detname, ctype, tstamp=None, rundepl=None, fmt='%.4f',\
                                dirmode=0o2775, filemode=0o664, group='ps-users'):
    import numpy as np
    from Detector.GlobalUtils import info_ndarr
    from Detector.UtilsCalib import save_ndarray_in_textfile, change_file_ownership  #save_2darray_in_textfile

    assert isinstance(arr2d, np.ndarray), 'input array of offsets type:%s is not a numpy array' % type(nda)
    assert arr2d.shape == (704,768)
    logger.info('save_epix100a_ctype_in_repo %s' % info_ndarr(arr2d, 'arr2d'))

    fname = file_name_in_repo(exp, runnum, detname, ctype, tstamp=tstamp, rundepl=rundepl, dirmode=dirmode, filemode=filemode, group=group)
    logger.info('save file: %s' % fname)

    save_ndarray_in_textfile(arr2d, fname, filemode, fmt)
    #change_file_ownership(fname, user=None, group=group)

# EOF
