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
#import PSCalib.GlobalUtils as gu
from Detector.UtilsEpix10ka2M import id_epix10ka2m_for_env_det


#from PSCalib.UtilsPanelAlias import alias_for_id, id_for_alias, alias_file_formatted
import PSCalib.UtilsPanelAlias as upa

from PSCalib.GeometryAccess import GeometryAccess
import Detector.UtilsCalib as uc

gu = uc.cgu

RAYONIX_PIXEL_SIZE = 44.271  # um 85.00 +/- 0.05mm/1920pixel

def cond_msg(cond, msg='', logger_method=logger.warning):
    if cond: logger_method(msg)
    return cond

def str_rayonix_geo_matrix_segment(d):
    """returns str like 'MTRX:V2:3840:3840:44.271:44.271' using configuration data.
    d = {'maxWidth': 3840, 'height': 1920, 'readoutMode': psana.Rayonix.ReadoutMode.Unknown,
    'Version': 2, 'MX340HS_Row_Pixels': 7680, 'rawMode': 0, 'TypeId': 73, 'numPixels': 3686400,
    'binning_f': 2, 'BasePixelSize': 44, 'MX170HS_Column_Pixels': 3840, 'width': 1920,
    'ReadoutMode': psana.Rayonix.ReadoutMode(0), 'trigger': 0, 'binning_s': 2,
    'MX170HS_Row_Pixels': 3840, 'pixelHeight': 88, 'DeviceIDMax': 40, 'pixelWidth': 88,
    'darkFlag': 0, 'exposure': 0, 'maxHeight': 3840, 'MX340HS_Column_Pixels': 7680,
    'deviceID': 'name:0000', 'testPattern': 0}
    """
    #d = gu.dict_of_object_metadata(rco)
    logger.debug('dict_rayonix_cfg: %s' % str(d))
    height = d.get('height', None)  # 1920
    width = d.get('width', None)  # 1920
    binning_s = d.get('binning_f', None)  # 2
    binning_f = d.get('binning_f', None)  # 2

    if None in (height, width, binning_s, binning_f):
        maxHeight = d.get('maxHeight', None)  # 3840
        maxWidth = d.get('maxWidth', None)  # 3840
        logger.warning('Rayonis configuration has undefined parameters: '\
                       +'maxHeight:%s maxWidth:%s height:%s width:%s binning_s:%s binning_f:%s' %\
                       (str(maxHeight), str(maxWidth), str(height), str(width), str(binning_s), str(binning_f)))
        return None
    return 'MTRX:V2:%d:%d:%.3f:%.3f' % (height, width, RAYONIX_PIXEL_SIZE*binning_s, RAYONIX_PIXEL_SIZE*binning_f)


def det_aliasname(dtype, det_alias):
    """ returns <dettype>_<detalias>, e.g. epix10ka2m_0002"""
    return '%s_%s' % (dtype, det_alias)

def fname_aliases(dir_dettype, dtype):
    """returns pass like /sdf/group/lcls/ds/ana/detector/calib/geometry/epix10ka2m/.aliases-epix10ka2m.txt"""
    return '%s/.aliases-%s.txt' % (dir_dettype, dtype)


def geometry_deploy_constants(**kwa):
    """ """

    s = '\n'.join(['  %12s : %s' % (k, str(v)) for k,v in kwa.items()])
    logger.info('input parameters\n%s' % s)

    exp        = kwa.get('exp', None)
    detname    = kwa.get('det', None)
    run        = kwa.get('run', None)
    runrange   = kwa.get('runrange', '0-end')
    dsnamex    = kwa.get('dsnamex', None)
    tstamp     = kwa.get('tstamp', None)
    dirrepo    = kwa.get('dirrepo', './work')
    dircalib   = kwa.get('dircalib', None)
    deploy     = kwa.get('deploy', False)
    backwrd    = kwa.get('backwrd', False)
    loglev     = kwa.get('loglev', 'DEBUG')
    dirmode    = kwa.get('dirmode',  0o2775)
    filemode   = kwa.get('filemode', 0o664)
    group      = kwa.get('group', 'ps-users')
    repoman    = kwa.get('repoman', None)
    name_parent= kwa.get('parent', 'IP')
    addgeof    = kwa.get('addgeof', None)
    dsname = uc.str_dsname(exp, run, dsnamex)

    logger.info('open dataset %s' % dsname)

    ds  = psana.DataSource(dsname)
    det = psana.Detector(detname)
    env = ds.env()
    src = det.source

    strsrc = gu.string_from_source(src)
    int_dettype = gu.det_type_from_source(src)
    dettype = gu.dic_det_type_to_name[int_dettype].lower() # epix10ka2m
    dir_dettype = repoman.dir_in_repo(dettype) # /sdf/group/lcls/ds/ana/detector/calib/geometry/epix10ka2m
    fname_als = fname_aliases(dir_dettype, dettype) # /sdf/group/lcls/ds/ana/detector/calib/geometry/epix10ka2m/.aliases-epix10ka2m.txt
    is_epix10ka_any = int_dettype in (gu.EPIX10K, gu.EPIX10KAQUAD, gu.EPIX10KA2M) # True
    id_det = id_epix10ka2m_for_env_det(ds.env(), det) if is_epix10ka_any else None # 0000000002-0172166401-1342177302-...
    det_alias    = None if id_det is None else upa.alias_for_id(id_det, fname=fname_als, exp=exp, run=int(run)) # 0002
    det_aliasn   = None if id_det is None else det_aliasname(dettype, det_alias) #epix10ka2m_0002
    id_det_fmted = None if id_det is None else upa.id_det_formatted(id_det, gap='\n    ')

    logger.info('\n  dettype: %s' % dettype\
              + '\n  repository: %s' % dir_dettype\
              + '\n  file with aliases: %s' % fname_als\
              + '\n  id_det: %s' % id_det_fmted\
              + '\n  alias for id_det: %s' % det_alias\
              + '\n  detector type and alias: %s' % det_aliasn)
    logger.debug(upa.alias_file_formatted(fname_als))

    tsrun, tsnow = uc.tstamps_run_and_now(env, fmt='%Y%m%d%H%M%S') # e.g. 20241003211628

    if is_epix10ka_any and addgeof is not None:
        # Add reference like epix10ka2m_0002_20241003211628.data to existing geometry file
        # Extra parameters:
        # --addgeof <file-name> - existing geometry file evaluated from optical metrology
        # --tstamp <YYYYmmDDHHMMSS> - non-default timestamp if specified, else tsrun
        # -D - confirms deployment

        path_ref = '%s/%s_%s.data' % (dir_dettype, det_aliasn, (tsrun if tstamp is None else tstamp))
        path_geo = '%s/%s' % (dir_dettype, addgeof)

        if cond_msg(not os.path.exists(path_geo), msg='DOES NOT EXIST: %s' % path_geo, logger_method=logger.warning):
            logger.info('path_ref: %s' % path_ref) # -a 2021-02-02-geometry-epix10ks2m.1-recentred-for-psana.txt
            return

        cmd = 'ln -s %s %s' % (addgeof, path_ref)
        logger.info('cmd: %s' % cmd)
        if deploy:
            if cond_msg(os.path.exists(path_ref),\
                        msg='EXIT DUE TO EXISTING REFERENCE %s' % path_ref, logger_method=logger.warning):
                return
            os.system(cmd)
            logger.info('deployed reference: %s' % path_ref)
        else:
            logger.warning('!!! add -D to deploy reference !!!')
        return

    _detname = None if det_aliasn is None else det_aliasn.split('_')[-1]

    if (not is_epix10ka_any) or backwrd:
        _detname = strsrc.replace(':','-').replace('.','-')
        tsrun, _ = uc.tstamps_run_and_now(env, fmt='%Y%m%d') # e.g. 20241003

    pattern = fname_prefix = '%s_%s' % (dettype, _detname)
    list_of_files = [name for name in os.listdir(dir_dettype) if fname_prefix in name]
    logger.info('list of found in repository geometry files for dettype_detname: %s\n  %s' % (fname_prefix, '\n  '.join(list_of_files)))

    fname = uc.find_file_for_timestamp(dir_dettype, pattern, tsrun)

    if fname is None: fname = '%s/%s_default.data' % (dir_dettype, dettype) # use default if not found
    logger.info('file_for_timestamp(tsrun=%s): %s' % (tsrun, fname))

    cmd = ' '.join(sys.argv)
    if '--pos' in cmd or '--rot' in cmd or '--parent' in cmd or int_dettype == gu.RAYONIX:

        geo = GeometryAccess(fname, 0o377 if (loglev=='DEBUG') else 0)
        geo_ip = geo.get_geo(name_parent, 0)

        logger.debug('dir(geo): %s' % str(dir(geo)))

        if int_dettype == gu.RAYONIX:
            d = det.pyda.dict_rayonix_config()
            str_mtrx = str_rayonix_geo_matrix_segment(d)
            logger.info('MTRX segment from rayonix configuration: %s' % str_mtrx)
            if str_mtrx is not None:
                for g in geo.list_of_geos:
                    logger.info('geo.oname: %s' % g.oname)
                    if g.oname[:4] == 'MTRX': g.oname = str_mtrx
            else:
                logger.warning('RAYONIX SEGMENT DESCRIPTOR IS NOT CORRECTED because of missing configuration parameters.')

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

    logger.info('standard calib dir: %s' % env.calibDir().replace('//','/'))
    logger.info('non-default calib dir: %s' % dircalib)
    calibdir = env.calibDir().replace('//','/') if dircalib is None else dircalib # '/reg/d/psdm/XPP/xpptut15/calib'
    calibgrp = uc.calib_group_for_tname_lower(dettype) # 'Epix10ka::CalibV1'
    ctypedir = '%s/%s/%s' % (calibdir, calibgrp, strsrc) # '/calib/Epix10ka::CalibV1/MfxEndstation.0:Epix10ka.0/'

    if deploy:
        octype   = 'geometry'
        ofname   = '%s.data' % runrange
        lfname   = None
        logger.info('deploy calib file %s under %s/%s' % (fname, ctypedir, octype))
        gu.deploy_file(fname, ctypedir, octype, ofname, lfname, verbos=(loglev=='DEBUG'),\
                       filemode=filemode, dirmode=dirmode, group=group)
    else:
        logger.warning('Add option -D to deploy files under directory %s' % ctypedir)
# EOF
