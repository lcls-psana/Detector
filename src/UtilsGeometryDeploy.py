"""
:py:class:`UtilsGeometryDeploy`
===============================

Usage::
    import Detector.UtilsGeometryDeploy as ugd

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created on 2022-03-18 by Mikhail Dubrovin
"""
import logging
logger = logging.getLogger(__name__)

from time import time
import os
import sys
import psana
import numpy as np
from time import time #, localtime, strftime
import PSCalib.GlobalUtils as gu
from PSCalib.GeometryAccess import GeometryAccess
import Detector.UtilsCalib as uc


def command_line(): return ' '.join(sys.argv)


def geometry_deploy_constants(**kwa):
    s = '\n'.join(['  %12s : %s' % (k, str(v)) for k,v in kwa.items()])
    logger.info('input parameters\n%s' % s)

    exp        = kwa.get('exp', None)
    detname    = kwa.get('det', None)
    run        = kwa.get('run', None)
    runrange   = kwa.get('runrange', '0-end')
    dssuffix   = kwa.get('dssuffix', None)
    _dsname    = kwa.get('dsname', None)
    tstamp     = kwa.get('tstamp', None)
    dirrepo    = kwa.get('dirrepo', './work')
    dircalib   = kwa.get('dircalib', None)
    deploy     = kwa.get('deploy', False)
    logmode    = kwa.get('logmode', 'DEBUG')
    dirmode    = kwa.get('dirmode',  0o777)
    filemode   = kwa.get('filemode', 0o666)
    repoman    = kwa.get('repoman', None)
    name_parent= kwa.get('parent', 'IP')

    dsname = 'exp=%s:run=%s' % (exp, str(run)) # 'exp=xpptut15:run=54' # :idx, :smd or *.xtc file name
    if dssuffix is not None: dsname += dssuffix
    if _dsname is not None: dsname = _dsname

    logger.info('open dataset %s' % dsname)

    ds  = psana.DataSource(dsname)
    det = psana.Detector(detname)
    env = ds.env()
    src = det.source

    strsrc = gu.string_from_source(src)
    _detname = strsrc.replace(':','-').replace('.','-')
    dettype = gu.dic_det_type_to_name[gu.det_type_from_source(src)].lower()
    dir_dettype = repoman.dir_in_repo(dettype)
    logger.info('directory for dettype: %s' % dir_dettype)

    pattern = fname_prefix = '%s_%s' % (dettype, _detname)

    list_of_files = [name for name in os.listdir(dir_dettype) if fname_prefix in name]
    logger.info('list of found in repository geometry files for dettype_detname: %s\n  %s' % (fname_prefix, '\n  '.join(list_of_files)))

    tsrun, tsnow = uc.tstamps_run_and_now(env, fmt='%Y%m%d') #TSTAMP_FORMAT = '%Y%m%d%H%M%S'
    fname = uc.find_file_for_timestamp(dir_dettype, pattern, tsrun)

    if fname is None: fname = '%s/%s_default.data' % (dir_dettype, dettype) # use default if not found
    logger.info('file_for_timestamp(tsrun=%s): %s' % (tsrun, fname))

    cmd = command_line()
    if '--pos' in cmd or '--rot' in cmd or '--parent' in cmd:
        geo = GeometryAccess(fname, 0o377 if (logmode=='DEBUG') else 0)
        geo_ip = geo.get_geo(name_parent, 0)
        if geo_ip is not None:
          list_of_geo_ip_children = geo_ip.list_of_children
          if list_of_geo_ip_children is not None and len(list_of_geo_ip_children)==1:
             geo_det = list_of_geo_ip_children[0]
             logger.info('geo_det: %s' % geo_det.info_geo())
             x0    = kwa.get('posx', 0)
             y0    = kwa.get('posy', 0)
             z0    = kwa.get('posz', 0)
             rot_x = kwa.get('rotx', 0)
             rot_y = kwa.get('roty', 0)
             rot_z = kwa.get('rotz', 0)
             tilt_z, tilt_y, tilt_x = 0, 0, 0 #geo_det.tilt_z, geo_det.tilt_y, geo_det.tilt_x
             geo_det.set_geo_pars(x0, y0, z0, rot_z, rot_y, rot_x, tilt_z, tilt_y, tilt_x)
             logger.info('geo_det updated: %s' % geo_det.info_geo())

             fname = os.path.join(dir_dettype, '%s_tmp.data' % dettype) #, tsnow)
             geo.save_pars_in_file(fname)

    if not os.path.exists(fname):
        logger.warning('NOT EXISTS file: %s ' % fname)
        return

    logger.info('standard calib dir: %s' % env.calibDir())
    logger.info('non-default calib dir: %s' % dircalib)
    calibdir = env.calibDir() if dircalib is None else dircalib # '/reg/d/psdm/XPP/xpptut15/calib'
    calibgrp = uc.calib_group_for_tname_lower(dettype) # 'Epix10ka::CalibV1'
    ctypedir = '%s/%s/%s' % (calibdir, calibgrp, strsrc) # '/calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'

    if deploy:
        octype   = 'geometry'
        ofname   = '%s.data' % runrange
        lfname   = None
        logger.info('deploy calib file %s under %s/%s' % (fname, ctypedir, octype))
        gu.deploy_file(fname, ctypedir, octype, ofname, lfname, verbos=(logmode=='DEBUG'))
    else:
        logger.warning('Add option -D to deploy files under directory %s' % ctypedir)
# EOF
