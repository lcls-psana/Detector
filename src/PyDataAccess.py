#!/usr/bin/env python

"""
:py:class:`PyDataAccess` contains methods to access psana data objects
=======================================================================

Usage ::

    # Import:
    from Detector.PyDataAccess import get_jungfrau_data_object, get_jungfrau_config_object

    o  = get_jungfrau_data_object(env, src)
    co = get_jungfrau_config_object(env, src)

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created by Mikhail Dubrovin
"""

import _psana
from time import strftime, localtime


def get_cspad_data_object(evt, src):
    """get cspad data object
    """
    o = evt.get(_psana.CsPad.DataV2, src)
    if o is not None: return o

    o = evt.get(_psana.CsPad.DataV1, src)
    if o is not None: return o

    return None


def get_cspad_config_object(env, src):
    """get cspad config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.CsPad.ConfigV5, src)
    if o is not None: return o

    o = cfg.get(_psana.CsPad.ConfigV4, src)
    if o is not None: return o

    o = cfg.get(_psana.CsPad.ConfigV3, src)
    if o is not None: return o

    o = cfg.get(_psana.CsPad.ConfigV2, src)
    if o is not None: return o

    return None


def get_cspad2x2_data_object(evt, src):
    """get cspad2x2 data object
    """
    o = evt.get(_psana.CsPad2x2.ElementV1, src)
    if o is not None: return o

    return None


def get_cspad2x2_config_object(env, src):
    """get cspad2x2 config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.CsPad2x2.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.CsPad2x2.ConfigV1, src)
    if o is not None: return o

    return None


def get_camera_data_object(evt, src):
    """get camera data object
    """
    o = evt.get(_psana.Camera.FrameV1, src)
    if o is not None: return o

    return None


def get_camera_config_object(env, src):
    """get camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Camera.FrameFexConfigV1, src)
    if o is not None: return o

    return None


def get_opal1k_config_object(env, src):
    """get camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Opal1k.ConfigV1, src)
    if o is not None: return o

    return None


def get_princeton_data_object(evt, src):
    """get princeton data object
    """
    o = evt.get(_psana.Princeton.FrameV2, src)
    if o is not None: return o

    o = evt.get(_psana.Princeton.FrameV1, src)
    if o is not None: return o

    o = evt.get(_psana.Pimax.FrameV1, src)
    if o is not None: return o

    o = evt.get(_psana.Pixis.FrameV1, src)
    if o is not None: return o

    return None


def get_princeton_config_object(env, src):
    """get princeton config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Princeton.ConfigV5, src)
    if o is not None: return o

    o = cfg.get(_psana.Princeton.ConfigV4, src)
    if o is not None: return o

    o = cfg.get(_psana.Princeton.ConfigV3, src)
    if o is not None: return o

    o = cfg.get(_psana.Princeton.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Princeton.ConfigV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Pimax.ConfigV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Pixis.ConfigV1, src)
    if o is not None: return o

    return None


def get_pnccd_data_object(evt, src):
    """get pnccd data object
    """
    o = evt.get(_psana.PNCCD.FramesV1, src)
    if o is not None: return o

    return None


def get_pnccd_config_object(env, src):
    """get pnccd config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.PNCCD.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.PNCCD.ConfigV1, src)
    if o is not None: return o

    return None


def get_andor_data_object(evt, src):
    """get andor data object
    """
    o = evt.get(_psana.Andor3d.FrameV1, src)
    if o is not None: return o

    o = evt.get(_psana.Andor.FrameV1, src)
    if o is not None: return o

    return None


def get_andor_config_object(env, src):
    """get andor config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Andor3d.ConfigV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Andor.ConfigV1, src)
    if o is not None: return o

    return None


get_fccd_data_object = get_camera_data_object


def get_fccd_config_object(env, src):
    """get fccd config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.FCCD.FccdConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.FCCD.FccdConfigV1, src)
    if o is not None: return o

    o = cfg.get(_psana.FCCD.FccdConfig, src)
    if o is not None: return o

    return None


get_fccd960_data_object = get_camera_data_object
get_fccd960_config_object = get_fccd_config_object


def get_epix_data_object(evt, src):
    """get epix data object
    """
    o = evt.get(_psana.Epix.ElementV3, src)
    if o is not None: return o

    o = evt.get(_psana.Epix.ElementV2, src)
    if o is not None: return o

    o = evt.get(_psana.Epix.ElementV1, src)
    if o is not None: return o

    o = evt.get(_psana.Epix.ArrayV1, src)
    if o is not None: return o

    return None


def get_epix_config_object(env, src):
    """get epix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config100aV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config100aV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10ka2MV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10ka2MV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaQuadV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaQuadV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10KV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.ConfigV1, src)
    if o is not None: return o

    return None


def get_epix10ka_any_config_object(env, src):
    """get epix10ka2m config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config10ka2MV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10ka2MV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaQuadV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaQuadV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaV1, src)
    if o is not None: return o

    return None


def get_epix10ka_config_object(env, src):
    """get epix10ka config object faster than from get_epix_config_object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config10kaV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaV1, src)
    if o is not None: return o

    return None


def get_epix10ka2m_config_object(env, src):
    """get epix10ka2m config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config10ka2MV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10ka2MV1, src)
    if o is not None: return o

    return None


def get_epix10ka2m_data_object(evt, src):
    """get epix10ka2m data object
    """
    o = evt.get(_psana.Epix.ArrayV1, src)
    if o is not None: return o

    return None


def get_epix10kaquad_config_object(env, src):
    """get epix10kaquad config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config10kaQuadV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Epix.Config10kaQuadV1, src)
    if o is not None: return o

    return None


get_epix10kaquad_data_object = get_epix10ka2m_data_object


def get_tm6740_config_object(env, src):
    """get pulnix tm6740 config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Pulnix.TM6740ConfigV1, src)
    if o is not None: return o

    o = cfg.get(_psana.Pulnix.TM6740ConfigV2, src)
    if o is not None: return o

    return None


get_quartz_data_object = get_camera_data_object


def get_quartz_config_object(env, src):
    """get quartz config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Quartz.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Quartz.ConfigV1, src)
    if o is not None: return o

    return None


get_rayonix_data_object = get_camera_data_object


def get_rayonix_config_object(env, src):
    """get rayonix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Rayonix.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Rayonix.ConfigV1, src)
    if o is not None: return o

    return None


def get_timepix_data_object(evt, src):
    """get timepix data object
    """
    o = evt.get(_psana.Timepix.DataV2, src)
    if o is not None: return o

    o = evt.get(_psana.Timepix.DataV1, src)
    if o is not None: return o

    return None


def get_timepix_config_object(env, src):
    """get timepix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Timepix.ConfigV3, src)
    if o is not None: return o

    o = cfg.get(_psana.Timepix.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Timepix.ConfigV1, src)
    if o is not None: return o

    return None


def get_fli_data_object(evt, src):
    """get fli data object
    """
    o = evt.get(_psana.Fli.FrameV1, src)
    if o is not None: return o

    return None


def get_fli_config_object(env, src):
    """get fli config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Fli.ConfigV1, src)
    if o is not None: return o

    return None


def get_pimax_data_object(evt, src):
    """get pimax data object
    """
    o = evt.get(_psana.Pimax.FrameV1, src)
    if o is not None: return o

    return None


def get_pimax_config_object(env, src):
    """get pimax config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Pimax.ConfigV1, src)
    if o is not None: return o

    return None


def get_pixis_data_object(evt, src):
    """get pixis data object
    """
    o = evt.get(_psana.Pixis.FrameV1, src)
    if o is not None: return o

    return None


def get_pixis_config_object(env, src):
    """get pixis config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Pixis.ConfigV1, src)
    if o is not None: return o

    return None


def get_orca_config_object(env, src):
    """get orca config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Orca.ConfigV1, src)
    if o is not None: return o

    return None


def get_zyla_data_object(evt, src):
    """get zyla data object
    """
    o = evt.get(_psana.Zyla.FrameV1, src)
    if o is not None: return o

    return None


def get_zyla_config_object(env, src):
    """get zyla config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Zyla.ConfigV1, src)
    if o is not None: return o

    return None


def get_istar_config_object(env, src):
    """get istar config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.iStar.ConfigV1, src)
    if o is not None: return o

    return None


def get_vimba_data_object(evt, src):
    """get vimba data object
    """
    o = evt.get(_psana.Vimba.FrameV1, src)
    if o is not None: return o

    return None


def get_alvium_config_object(env, src):
    """get alvium config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Vimba.AlviumConfigV1, src)
    if o is not None: return o

    return None


def get_jungfrau_data_object(evt, src):
    """get jungfrau data object
    """
    o = evt.get(_psana.Jungfrau.ElementV2, src)
    if o is not None: return o

    o = evt.get(_psana.Jungfrau.ElementV1, src)
    if o is not None: return o

    return None


def get_jungfrau_config_object(env, src):
    if src is None: return None

    cfg = env.configStore()

    o = cfg.get(_psana.Jungfrau.ConfigV3, src)
    if o is not None: return o

    o = cfg.get(_psana.Jungfrau.ConfigV2, src)
    if o is not None: return o

    o = cfg.get(_psana.Jungfrau.ConfigV1, src)
    if o is not None: return o

    return None


def get_jungfrau_gain_mode_object(env, src):
    """Returns gain mode object, usage: gmo=..., gmo.name, gmo.names.items(), gm.values.items(), etc.
    """
    co = get_jungfrau_config_object(env, _psana.Source(src))
    return co.gainMode()


def get_epicscam_config_object(env, src):
    """get epics camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Camera.ControlsCameraConfigV1, src)
    if o is not None: return o

    return None

##---- For WFDetector.py ------

def get_acqiris_data_object(evt, src):
    """get acqiris data object
    """
    o = evt.get(_psana.Acqiris.DataDescV1, src)
    if o is not None: return o

    return None


def get_acqiris_config_object(env, src):
    """get acqiris config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Acqiris.ConfigV1, src)
    if o is not None: return o

    return None


def get_imp_data_object(evt, src):
    """get imp data object
    """
    o = evt.get(_psana.Imp.ElementV1, src)
    if o is not None: return o

    return None


def get_imp_config_object(env, src):
    """get imp config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Imp.ConfigV1, src)
    if o is not None: return o

    return None


def get_uxi_data_object(evt, src):
    """get uxi data object
    """
    o = evt.get(_psana.Uxi.FrameV1, src)
    if o is not None: return o

    return None


def get_uxi_config_object(env, src):
    """get uxi config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Uxi.ConfigV1, src)
    if o is not None: return o

    return None


get_streak_data_object = get_camera_data_object


def get_streak_config_object(env, src):
    """get streak config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Streak.ConfigV1, src)
    if o is not None: return o

    return None


get_archon_data_object = get_camera_data_object


def get_archon_config_object(env, src):
    """get streak config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Archon.ConfigV3, src)
    if o is not None: return o

    return None

##----- Other data objects ----

def get_evr_data_object(evt, src):
    """get evr data object for event codes
    """
    o = evt.get(_psana.EvrData.DataV4, src)
    if o is not None: return o

    o = evt.get(_psana.EvrData.DataV3, src)
    if o is not None: return o

    return None


def time_pars_evt(evt):
    """Returns time parameters from psana.Event object.

    Parameter
    - evt (psana.Event) - psana event object

    Returns tuple of the event time parameters:

    - tsec (int) - time in sec since 1970
    - tnsec (int) - time in nanosecond
    - fid (uint16) - fiducials
    - date (str) - date in format YYYY-MM-DD
    - time (str) - date in format MM:MM:SS
    """
    evtid = evt.get(_psana.EventId)
    tsec, tnsec = evtid.time()
    fid = evtid.fiducials()
    date = strftime('%Y-%m-%d', localtime(tsec))
    time = strftime('%H:%M:%S', localtime(tsec))
    return tsec, tnsec, fid, date, time

# EOF
