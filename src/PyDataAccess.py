#!/usr/bin/env python
#------------------------------
"""
:py:class:`PyDataAccess` contains methods to access psana data objects
=======================================================================

This software was developed for the SIT project.
If you use all or part of it, please give an appropriate acknowledgment.

Created by Mikhail Dubrovin
"""

#import sys
import _psana
from time import strftime, localtime

##-----------------------------

def get_cspad_data_object(evt, src) :
    """get cspad data object
    """
    o = evt.get(_psana.CsPad.DataV2, src)
    if o is not None : return o

    o = evt.get(_psana.CsPad.DataV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_cspad_config_object(env, src) :
    """get cspad config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.CsPad.ConfigV5, src)
    if o is not None : return o

    o = cfg.get(_psana.CsPad.ConfigV4, src)
    if o is not None : return o

    o = cfg.get(_psana.CsPad.ConfigV3, src)
    if o is not None : return o

    o = cfg.get(_psana.CsPad.ConfigV2, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_cspad2x2_data_object(evt, src) :
    """get cspad2x2 data object
    """
    o = evt.get(_psana.CsPad2x2.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_cspad2x2_config_object(env, src) :
    """get cspad2x2 config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.CsPad2x2.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.CsPad2x2.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_camera_data_object(evt, src) :
    """get camera data object
    """
    o = evt.get(_psana.Camera.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_camera_config_object(env, src) :
    """get camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Camera.FrameFexConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_opal1k_config_object(env, src) :
    """get camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Opal1k.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_princeton_data_object(evt, src) :
    """get princeton data object
    """
    o = evt.get(_psana.Princeton.FrameV2, src)
    if o is not None : return o

    o = evt.get(_psana.Princeton.FrameV1, src)
    if o is not None : return o

    o = evt.get(_psana.Pimax.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_princeton_config_object(env, src) :
    """get princeton config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Princeton.ConfigV5, src)
    if o is not None : return o

    o = cfg.get(_psana.Princeton.ConfigV4, src)
    if o is not None : return o

    o = cfg.get(_psana.Princeton.ConfigV3, src)
    if o is not None : return o

    o = cfg.get(_psana.Princeton.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Princeton.ConfigV1, src)
    if o is not None : return o

    o = cfg.get(_psana.Pimax.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_pnccd_data_object(evt, src) :
    """get pnccd data object
    """
    o = evt.get(_psana.PNCCD.FramesV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_pnccd_config_object(env, src) :
    """get pnccd config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.PNCCD.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.PNCCD.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_andor_data_object(evt, src) :
    """get andor data object
    """
    o = evt.get(_psana.Andor3d.FrameV1, src)
    if o is not None : return o

    o = evt.get(_psana.Andor.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_andor_config_object(env, src) :
    """get andor config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Andor3d.ConfigV1, src)
    if o is not None : return o

    o = cfg.get(_psana.Andor.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_fccd_data_object(env, src) :
    """get fccd data object
    """
    return get_camera_data_object(evt, src)

##-----------------------------

def get_fccd_config_object(env, src) :
    """get fccd config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.FCCD.FccdConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.FCCD.FccdConfigV1, src)
    if o is not None : return o

    o = cfg.get(_psana.FCCD.FccdConfig, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_fccd960_data_object(env, src) :
    """get fccd960 data object
    """
    return get_camera_data_object(evt, src)

##-----------------------------

def get_fccd960_config_object(env, src) :
    """get fccd960 config object
    """
    return get_fccd_config_object(env, src)
    
##-----------------------------

def get_epix_data_object(evt, src) :
    """get epix data object
    """
    o = evt.get(_psana.Epix.ElementV3, src)
    if o is not None : return o

    o = evt.get(_psana.Epix.ElementV2, src)
    if o is not None : return o

    o = evt.get(_psana.Epix.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_epix_config_object(env, src) :
    """get epix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Epix.Config100aV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Epix.Config100aV1, src)
    if o is not None : return o

    o = cfg.get(_psana.Epix.Config10KV1, src)
    if o is not None : return o

    o = cfg.get(_psana.Epix.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_tm6740_config_object(env, src) :
    """get pulnix tm6740 config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Pulnix.TM6740ConfigV1, src)
    if o is not None : return o

    o = cfg.get(_psana.Pulnix.TM6740ConfigV2, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_quartz_data_object(evt, src) :
    """get quartz data object
    """
    return get_camera_data_object(evt, src)

##-----------------------------

def get_quartz_config_object(env, src) :
    """get quartz config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Quartz.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Quartz.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_rayonix_data_object(evt, src) :
    """get rayonix data object
    """
    return get_camera_data_object(evt, src)

##-----------------------------

def get_rayonix_config_object(env, src) :
    """get rayonix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Rayonix.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Rayonix.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_timepix_data_object(evt, src) :
    """get timepix data object
    """
    o = evt.get(_psana.Timepix.DataV2, src)
    if o is not None : return o

    o = evt.get(_psana.Timepix.DataV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_timepix_config_object(env, src) :
    """get timepix config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Timepix.ConfigV3, src)
    if o is not None : return o

    o = cfg.get(_psana.Timepix.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Timepix.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_fli_data_object(evt, src) :
    """get fli data object
    """
    o = evt.get(_psana.Fli.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_fli_config_object(env, src) :
    """get fli config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Fli.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_pimax_data_object(evt, src) :
    """get pimax data object
    """
    o = evt.get(_psana.Pimax.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_pimax_config_object(env, src) :
    """get pimax config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Pimax.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_orca_config_object(env, src) :
    """get orca config object
    """
    cfg = env.configStore()

    o = cfg.get(_psana.Orca.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_zyla_data_object(evt, src) :
    """get zyla data object
    """
    o = evt.get(_psana.Zyla.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_zyla_config_object(env, src) :
    """get zyla config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Zyla.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_jungfrau_data_object(evt, src) :
    """get jungfrau data object
    """
    o = evt.get(_psana.Jungfrau.ElementV2, src)
    if o is not None : return o

    o = evt.get(_psana.Jungfrau.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_jungfrau_config_object(env, src) :
    cfg = env.configStore()

    o = cfg.get(_psana.Jungfrau.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(_psana.Jungfrau.ConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_jungfrau_gain_mode_object(env, src) :
    """Returns gain mode object, usage: gmo=..., gmo.name, gmo.names.iteritems(), gm.values.iteritems(), etc.
    """
    co = get_jungfrau_config_object(env, _psana.Source(src))
    return co.gainMode()

##-----------------------------

def get_epicscam_config_object(env, src) :
    """get epics camera config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Camera.ControlsCameraConfigV1, src)
    if o is not None : return o

    return None

##-----------------------------
##-----------------------------
##---- For WFDetector.py ------
##-----------------------------
##-----------------------------

def get_acqiris_data_object(evt, src) :
    """get acqiris data object
    """
    o = evt.get(_psana.Acqiris.DataDescV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_acqiris_config_object(env, src) :
    """get acqiris config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Acqiris.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------

def get_imp_data_object(evt, src) :
    """get imp data object
    """
    o = evt.get(_psana.Imp.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_imp_config_object(env, src) :
    """get imp config object
    """
    cfg = env.configStore()
    o = cfg.get(_psana.Imp.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------
##----- Other data objects ----
##-----------------------------
##-----------------------------

def get_evr_data_object(evt, src) :
    """get evr data object for event codes
    """
    o = evt.get(_psana.EvrData.DataV4, src)
    if o is not None : return o

    o = evt.get(_psana.EvrData.DataV3, src)
    if o is not None : return o

    return None

##-----------------------------

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

##-----------------------------
