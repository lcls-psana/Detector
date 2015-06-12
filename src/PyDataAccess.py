#!/usr/bin/env python

#import sys
import psana

##-----------------------------

def get_cspad_data_object(evt, src) :
    """get cspad data object
    """
    o = evt.get(psana.CsPad.DataV2, src)
    if o is not None : return o

    o = evt.get(psana.CsPad.DataV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_cspad_config_object(env, src) :
    """get cspad config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.CsPad.ConfigV5, src)
    if o is not None : return o

    o = cfg.get(psana.CsPad.ConfigV4, src)
    if o is not None : return o

    o = cfg.get(psana.CsPad.ConfigV3, src)
    if o is not None : return o

    o = cfg.get(psana.CsPad.ConfigV2, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------

def get_cspad2x2_data_object(evt, src) :
    """get cspad2x2 data object
    """
    o = evt.get(psana.CsPad2x2.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_cspad2x2_config_object(env, src) :
    """get cspad2x2 config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.CsPad2x2.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(psana.CsPad2x2.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------

def get_camera_data_object(evt, src) :
    """get camera data object
    """
    o = evt.get(psana.Camera.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_camera_config_object(env, src) :
    """get camera config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.Camera.FrameFexConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------

def get_princeton_data_object(evt, src) :
    """get princeton data object
    """
    o = evt.get(psana.Princeton.FrameV2, src)
    if o is not None : return o

    o = evt.get(psana.Princeton.FrameV1, src)
    if o is not None : return o

    o = evt.get(psana.Pimax.FrameV1, src)
    if o is not None : return o

    return None

##-----------------------------

def get_princeton_config_object(env, src) :
    """get princeton config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.Princeton.ConfigV5, src)
    if o is not None : return o

    o = cfg.get(psana.Princeton.ConfigV4, src)
    if o is not None : return o

    o = cfg.get(psana.Princeton.ConfigV3, src)
    if o is not None : return o

    o = cfg.get(psana.Princeton.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(psana.Princeton.ConfigV1, src)
    if o is not None : return o

    o = cfg.get(psana.Pimax.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------

def get_pnccd_config_object(env, src) :
    """get pnccd config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.PNCCD.ConfigV2, src)
    if o is not None : return o

    o = cfg.get(psana.PNCCD.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------

def get_epix_data_object(evt, src) :
    """get epix data object
    """
    o = evt.get(psana.Epix.ElementV2, src)
    if o is not None : return o

    o = evt.get(psana.Epix.ElementV1, src)
    if o is not None : return o

    return None

##-----------------------------
##-----------------------------

def get_epix_config_object(env, src) :
    """get epix config object
    """
    cfg = env.configStore()
    o = cfg.get(psana.Epix.Config100aV1, src)
    if o is not None : return o

    o = cfg.get(psana.Epix.Config10KV1, src)
    if o is not None : return o

    o = cfg.get(psana.Epix.ConfigV1, src)
    if o is not None : return o

    return None
    
##-----------------------------
##-----------------------------
